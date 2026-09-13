"""
Business and Risk Analytics Engine for Track 1: FinTech & BFSI - UPI Fraud Ring & Merchant Analytics.
TransOrg AgentIQ Datathon.

This module computes all business metrics, risk scores, anomaly metrics, and merchant/customer 360 profiles.
"""

import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

class AnalyticsEngine:
    def __init__(self, data_dir: str = "data_cleaned"):
        self.data_dir = Path(data_dir)
        self.load_data()
        
    def load_data(self):
        """Loads cleaned data files."""
        self.df_txn = pd.read_parquet(self.data_dir / "fact_transactions.parquet")
        self.df_cb = pd.read_parquet(self.data_dir / "fact_chargebacks.parquet")
        self.df_cust = pd.read_parquet(self.data_dir / "dim_customers.parquet")
        self.df_mch = pd.read_parquet(self.data_dir / "dim_merchants.parquet")
        self.df_unified = pd.read_parquet(self.data_dir / "fact_unified_analytics.parquet")
        
        # Ensure timestamp types
        self.df_txn['timestamp'] = pd.to_datetime(self.df_txn['timestamp'])
        self.df_cb['reported_timestamp'] = pd.to_datetime(self.df_cb['reported_timestamp'])
        self.df_unified['timestamp'] = pd.to_datetime(self.df_unified['timestamp'])

    # --- Core Business Metrics ---

    def get_summary_kpis(self) -> Dict[str, Any]:
        """Calculates core executive business KPIs."""
        total_txns = len(self.df_txn)
        total_vol = float(self.df_txn['amount'].sum())
        atv = float(self.df_txn['amount'].mean()) if total_txns > 0 else 0.0
        
        status_counts = self.df_txn['status'].value_counts()
        success_cnt = int(status_counts.get('SUCCESS', 0))
        failed_cnt = int(status_counts.get('FAILED', 0))
        pending_cnt = int(status_counts.get('PENDING', 0))
        
        failed_rate = (failed_cnt / total_txns) if total_txns > 0 else 0.0
        pending_rate = (pending_cnt / total_txns) if total_txns > 0 else 0.0
        success_rate = (success_cnt / total_txns) if total_txns > 0 else 0.0
        
        cb_count = len(self.df_cb)
        cb_amount = float(self.df_cb['disputed_amount'].sum())
        cb_ratio = (cb_count / total_txns) if total_txns > 0 else 0.0
        cb_vol_ratio = (cb_amount / total_vol) if total_vol > 0 else 0.0
        
        # KYC Metrics
        kyc_total = len(self.df_cust)
        kyc_status_counts = self.df_cust['kyc_status'].value_counts()
        kyc_completed = int(kyc_status_counts.get('VERIFIED', 0))
        kyc_rejected = int(kyc_status_counts.get('REJECTED', 0))
        kyc_pending = int(kyc_status_counts.get('PENDING', 0))
        
        kyc_comp_rate = (kyc_completed / kyc_total) if kyc_total > 0 else 0.0
        kyc_rej_rate = (kyc_rejected / kyc_total) if kyc_total > 0 else 0.0
        
        # Dispute reporting delay
        avg_delay = float(self.df_cb['reporting_delay_days'].mean()) if cb_count > 0 else 0.0
        delay_gt_7d = int((self.df_cb['reporting_delay_days'] > 7).sum())
        delay_gt_7d_pct = (delay_gt_7d / cb_count) if cb_count > 0 else 0.0

        return {
            "total_transaction_count": total_txns,
            "total_transaction_amount": round(total_vol, 2),
            "average_transaction_value": round(atv, 2),
            "success_transaction_rate": round(success_rate, 4),
            "failed_transaction_rate": round(failed_rate, 4),
            "pending_transaction_rate": round(pending_rate, 4),
            "chargeback_count": cb_count,
            "chargeback_amount": round(cb_amount, 2),
            "chargeback_to_transaction_ratio": round(cb_ratio, 4),
            "chargeback_to_volume_ratio": round(cb_vol_ratio, 4),
            "kyc_completion_rate": round(kyc_comp_rate, 4),
            "kyc_rejection_rate": round(kyc_rej_rate, 4),
            "total_kyc_users": kyc_total,
            "average_dispute_reporting_delay_days": round(avg_delay, 2),
            "disputes_over_7_days_count": delay_gt_7d,
            "disputes_over_7_days_pct": round(delay_gt_7d_pct, 4)
        }

    # --- Trend Analytics ---

    def get_daily_trends(self) -> pd.DataFrame:
        """Returns daily transaction volume, count, ATV, and success/fail/pending splits."""
        daily = self.df_txn.groupby('date').agg(
            txn_count=('txn_id', 'count'),
            total_amount=('amount', 'sum'),
            avg_amount=('amount', 'mean'),
            success_count=('status', lambda s: (s == 'SUCCESS').sum()),
            failed_count=('status', lambda s: (s == 'FAILED').sum()),
            pending_count=('status', lambda s: (s == 'PENDING').sum()),
        ).reset_index()
        daily['date'] = pd.to_datetime(daily['date'])
        daily = daily.sort_values('date')
        
        # Merge daily chargebacks
        cb_daily = self.df_cb.groupby(self.df_cb['reported_timestamp'].dt.date).agg(
            chargeback_count=('complaint_id', 'count'),
            disputed_amount=('disputed_amount', 'sum')
        ).reset_index().rename(columns={'reported_timestamp': 'date'})
        cb_daily['date'] = pd.to_datetime(cb_daily['date'])
        
        daily = pd.merge(daily, cb_daily, on='date', how='left').fillna(0)
        daily['dispute_rate'] = daily['chargeback_count'] / daily['txn_count']
        return daily

    def get_hourly_failure_trend(self) -> pd.DataFrame:
        """Returns failure rates and volume by hour of day (0-23)."""
        hourly = self.df_txn.groupby('hour').agg(
            total_txns=('txn_id', 'count'),
            failed_txns=('status', lambda s: (s == 'FAILED').sum()),
            success_txns=('status', lambda s: (s == 'SUCCESS').sum()),
            pending_txns=('status', lambda s: (s == 'PENDING').sum()),
            avg_amount=('amount', 'mean')
        ).reset_index()
        hourly['failure_rate'] = hourly['failed_txns'] / hourly['total_txns']
        return hourly.sort_values('hour')

    # --- Merchant & Category Performance ---

    def get_merchant_category_metrics(self) -> pd.DataFrame:
        """Computes performance, volume, dispute rate, and failure rate by merchant category."""
        cat_summary = self.df_unified.groupby('merchant_category').agg(
            txn_count=('txn_id', 'count'),
            total_amount=('amount', 'sum'),
            avg_ticket_size=('amount', 'mean'),
            chargeback_count=('is_disputed', 'sum'),
            disputed_amount=('disputed_amount', 'sum'),
            failed_count=('status', lambda s: (s == 'FAILED').sum())
        ).reset_index()
        
        cat_summary['dispute_rate'] = cat_summary['chargeback_count'] / cat_summary['txn_count']
        cat_summary['dispute_volume_share'] = cat_summary['disputed_amount'] / cat_summary['total_amount']
        cat_summary['failure_rate'] = cat_summary['failed_count'] / cat_summary['txn_count']
        return cat_summary.sort_values('total_amount', ascending=False)

    def get_top_merchants_by_chargebacks(self, top_n: int = 15) -> pd.DataFrame:
        """Returns top merchants by chargeback count, disputed amount, and dispute ratio."""
        mch_perf = self.df_unified.groupby(['merchant_id', 'merchant_name', 'merchant_category', 'merchant_status']).agg(
            txn_count=('txn_id', 'count'),
            total_amount=('amount', 'sum'),
            chargeback_count=('is_disputed', 'sum'),
            disputed_amount=('disputed_amount', 'sum')
        ).reset_index()
        
        mch_perf['chargeback_ratio'] = mch_perf['chargeback_count'] / mch_perf['txn_count']
        return mch_perf.sort_values('chargeback_count', ascending=False).head(top_n)

    def get_high_risk_merchants(self, min_txns: int = 3, top_n: int = 20) -> pd.DataFrame:
        """
        Identifies high-risk merchants based on:
        - High chargeback-to-transaction ratio (>15%)
        - High dispute volume
        - Suspended or inactive status with active transactions
        """
        mch_perf = self.df_unified.groupby(['merchant_id', 'merchant_name', 'merchant_category', 'merchant_status']).agg(
            txn_count=('txn_id', 'count'),
            total_amount=('amount', 'sum'),
            chargeback_count=('is_disputed', 'sum'),
            disputed_amount=('disputed_amount', 'sum'),
            declared_avg_ticket=('declared_avg_ticket_size', 'first')
        ).reset_index()
        
        mch_perf['chargeback_ratio'] = mch_perf['chargeback_count'] / mch_perf['txn_count']
        mch_perf['actual_avg_ticket'] = mch_perf['total_amount'] / mch_perf['txn_count']
        
        # Risk Score Calculation (0 to 100)
        # Factor 1: CB ratio (up to 40 pts)
        # Factor 2: Disputed Amount (up to 30 pts)
        # Factor 3: Ticket Size Deviation (up to 20 pts)
        # Factor 4: Status flag (up to 10 pts)
        max_cb_amt = mch_perf['disputed_amount'].max() or 1.0
        
        def calc_risk(row):
            score = min(row['chargeback_ratio'] * 200, 40.0) # 20% cb ratio = 40 pts
            score += min((row['disputed_amount'] / max_cb_amt) * 30, 30.0)
            if pd.notna(row['declared_avg_ticket']) and row['declared_avg_ticket'] > 0:
                ticket_ratio = row['actual_avg_ticket'] / row['declared_avg_ticket']
                if ticket_ratio > 2.0 or ticket_ratio < 0.5:
                    score += 15.0
            if row['merchant_status'] in ['SUSPENDED', 'ON_HOLD']:
                score += 15.0
            return round(min(score, 100.0), 1)
            
        mch_perf['risk_score'] = mch_perf.apply(calc_risk, axis=1)
        filtered = mch_perf[mch_perf['txn_count'] >= min_txns]
        return filtered.sort_values('risk_score', ascending=False).head(top_n)

    # --- Customer & KYC Analytics ---

    def get_kyc_status_breakdown(self) -> pd.DataFrame:
        """Returns KYC status volume and dispute rates."""
        kyc_df = self.df_unified.groupby('kyc_status').agg(
            txn_count=('txn_id', 'count'),
            total_amount=('amount', 'sum'),
            avg_amount=('amount', 'mean'),
            chargeback_count=('is_disputed', 'sum'),
            disputed_amount=('disputed_amount', 'sum'),
            failed_count=('status', lambda s: (s == 'FAILED').sum())
        ).reset_index()
        
        kyc_df['dispute_rate'] = kyc_df['chargeback_count'] / kyc_df['txn_count']
        kyc_df['failure_rate'] = kyc_df['failed_count'] / kyc_df['txn_count']
        return kyc_df.sort_values('total_amount', ascending=False)

    def get_high_risk_users(self, top_n: int = 20) -> pd.DataFrame:
        """Identifies customers with repeat chargebacks and high dispute values."""
        user_cb = self.df_cb.groupby(['user_id']).agg(
            dispute_count=('complaint_id', 'count'),
            total_disputed_amount=('disputed_amount', 'sum'),
            avg_delay=('reporting_delay_days', 'mean'),
            severity_critical=('severity', lambda s: (s == 'CRITICAL').sum())
        ).reset_index()
        
        # Merge with KYC info
        user_cb = pd.merge(user_cb, self.df_cust, on='user_id', how='left')
        user_cb['kyc_status'] = user_cb['kyc_status'].fillna('UNREGISTERED')
        user_cb['risk_segment'] = user_cb['risk_segment'].fillna('UNKNOWN')
        
        return user_cb.sort_values(['dispute_count', 'total_disputed_amount'], ascending=False).head(top_n)

    # --- Dispute & Chargeback Analytics ---

    def get_chargeback_reasons(self) -> pd.DataFrame:
        """Returns dispute distribution by canonical reason."""
        reasons = self.df_cb.groupby('reason_category').agg(
            complaint_count=('complaint_id', 'count'),
            total_disputed_amount=('disputed_amount', 'sum'),
            avg_disputed_amount=('disputed_amount', 'mean'),
            avg_delay_days=('reporting_delay_days', 'mean')
        ).reset_index()
        reasons['share_of_disputes'] = reasons['complaint_count'] / len(self.df_cb)
        return reasons.sort_values('complaint_count', ascending=False)

    def get_chargeback_severity(self) -> pd.DataFrame:
        """Returns dispute breakdown by severity level."""
        sev = self.df_cb.groupby('severity').agg(
            complaint_count=('complaint_id', 'count'),
            total_disputed_amount=('disputed_amount', 'sum'),
            avg_disputed_amount=('disputed_amount', 'mean')
        ).reset_index()
        sev['share_of_complaints'] = sev['complaint_count'] / len(self.df_cb)
        
        # Sort by severity order
        sev_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        sev['order'] = sev['severity'].map(sev_order).fillna(4)
        return sev.sort_values('order').drop(columns=['order'])

    def get_utr_health_metrics(self) -> Dict[str, Any]:
        """Analyzes missing and invalid UTR correlation with failed and disputed transactions."""
        total = len(self.df_unified)
        missing_utr = self.df_unified[self.df_unified['utr'].isna()]
        invalid_utr = self.df_unified[~self.df_unified['is_valid_utr']]
        valid_utr = self.df_unified[self.df_unified['is_valid_utr']]
        
        return {
            "total_transactions": total,
            "valid_utr_count": len(valid_utr),
            "invalid_or_missing_utr_count": len(invalid_utr),
            "valid_utr_failure_rate": round(float((valid_utr['status'] == 'FAILED').mean()), 4) if len(valid_utr) > 0 else 0,
            "invalid_utr_failure_rate": round(float((invalid_utr['status'] == 'FAILED').mean()), 4) if len(invalid_utr) > 0 else 0,
            "valid_utr_dispute_rate": round(float(valid_utr['is_disputed'].mean()), 4) if len(valid_utr) > 0 else 0,
            "invalid_utr_dispute_rate": round(float(invalid_utr['is_disputed'].mean()), 4) if len(invalid_utr) > 0 else 0,
        }

    def detect_merchant_transaction_spikes(self, z_thresh: float = 2.5) -> pd.DataFrame:
        """
        Detects merchants experiencing sudden transaction count or volume spikes followed by disputes.
        """
        mch_daily = self.df_unified.groupby(['merchant_id', 'merchant_name', 'date']).agg(
            daily_txns=('txn_id', 'count'),
            daily_vol=('amount', 'sum'),
            daily_disputes=('is_disputed', 'sum')
        ).reset_index()
        
        # Calculate rolling stats per merchant
        results = []
        for mch_id, group in mch_daily.groupby('merchant_id'):
            if len(group) >= 3:
                mean_txns = group['daily_txns'].mean()
                std_txns = group['daily_txns'].std()
                if std_txns and std_txns > 0:
                    group = group.copy()
                    group['z_score'] = (group['daily_txns'] - mean_txns) / std_txns
                    spikes = group[group['z_score'] >= z_thresh]
                    if not spikes.empty:
                        results.append(spikes)
                        
        if results:
            spike_df = pd.concat(results, ignore_index=True)
            return spike_df.sort_values('z_score', ascending=False)
        return pd.DataFrame(columns=['merchant_id', 'merchant_name', 'date', 'daily_txns', 'daily_vol', 'daily_disputes', 'z_score'])
