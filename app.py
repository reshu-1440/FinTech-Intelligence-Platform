"""
TransOrg AgentIQ Datathon - Track 1: FinTech & BFSI
UPI Fraud Ring & Merchant Analytics Dashboard with Graph-First AI Agent.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="AgentIQ | UPI Fraud Ring & Merchant Analytics",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add repo root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.analytics_engine import AnalyticsEngine
from src.graph_agent import FraudGraphEngine, AgentIQAssistant

# Custom CSS for Premium Design & Visual Polish
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    
    .sub-title {
        color: #8892b0;
        font-size: 1.0rem;
        margin-bottom: 1.5rem;
    }
    
    .kpi-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.2rem 1.0rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    .kpi-card:hover {
        transform: translateY(-3px);
        border-color: #3a7bd5;
    }
    
    .kpi-val {
        font-size: 1.7rem;
        font-weight: 700;
        color: #00f2fe;
        margin-top: 0.3rem;
    }
    
    .kpi-label {
        font-size: 0.85rem;
        font-weight: 500;
        color: #a0aec0;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .badge-critical {
        background-color: #ff4b4b22;
        color: #ff4b4b;
        padding: 2px 8px;
        border-radius: 6px;
        font-weight: 600;
        border: 1px solid #ff4b4b66;
    }
    
    .badge-high {
        background-color: #ffa50022;
        color: #ffa500;
        padding: 2px 8px;
        border-radius: 6px;
        font-weight: 600;
        border: 1px solid #ffa50066;
    }
    
    .badge-success {
        background-color: #00cc8822;
        color: #00cc88;
        padding: 2px 8px;
        border-radius: 6px;
        font-weight: 600;
        border: 1px solid #00cc8866;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource(show_spinner="Initializing Analytics Engine & Knowledge Graph...")
def get_engines():
    engine = AnalyticsEngine("data_cleaned")
    graph_engine = FraudGraphEngine("data_cleaned")
    agent = AgentIQAssistant(engine, graph_engine)
    return engine, graph_engine, agent

engine, graph_engine, agent = get_engines()
kpis = engine.get_summary_kpis()

# Header Banner
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown("<div class='main-title'>🛡️ AgentIQ FinTech Intelligence Platform</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>UPI Fraud Ring Detection, Merchant Risk Scoring & Dispute Analytics</div>", unsafe_allow_html=True)
with col_h2:
    st.markdown("""
    <div style='text-align: right; padding-top: 10px;'>
        <span class='badge-success'>System Online</span> &bull; 
        <span class='badge-critical'>Graph Active</span>
    </div>
    """, unsafe_allow_html=True)

# Top KPI Metric Row
k1, k2, k3, k4, k5, k6 = st.columns(6)
with k1:
    st.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-label'>Total Volume</div>
        <div class='kpi-val'>₹{kpis['total_transaction_amount']/1e7:.2f} Cr</div>
    </div>
    """, unsafe_allow_html=True)
with k2:
    st.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-label'>Transactions</div>
        <div class='kpi-val'>{kpis['total_transaction_count']:,}</div>
    </div>
    """, unsafe_allow_html=True)
with k3:
    st.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-label'>Avg Ticket Size</div>
        <div class='kpi-val'>₹{kpis['average_transaction_value']:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)
with k4:
    st.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-label'>Dispute Rate</div>
        <div class='kpi-val' style='color:#ff7675;'>{kpis['chargeback_to_transaction_ratio']:.1%}</div>
    </div>
    """, unsafe_allow_html=True)
with k5:
    st.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-label'>Failure Rate</div>
        <div class='kpi-val' style='color:#fab1a0;'>{kpis['failed_transaction_rate']:.1%}</div>
    </div>
    """, unsafe_allow_html=True)
with k6:
    st.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-label'>KYC Verified</div>
        <div class='kpi-val' style='color:#55efc4;'>{kpis['kyc_completion_rate']:.1%}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Navigation Tabs
tabs = st.tabs([
    "📊 Executive Overview",
    "🏪 Merchant & Category Risk",
    "👤 Customer & KYC 360",
    "⚠️ Disputes & Chargebacks",
    "🕸️ Fraud Ring Graph Visualizer",
    "🤖 AgentIQ AI Copilot"
])

# ==========================================
# TAB 1: EXECUTIVE OVERVIEW
# ==========================================
with tabs[0]:
    st.subheader("Payment Health & Volume Trends")
    df_daily = engine.get_daily_trends()
    
    col_t1, col_t2 = st.columns([2, 1])
    with col_t1:
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Scatter(
            x=df_daily['date'], y=df_daily['total_amount'],
            mode='lines+markers', name='Daily Volume (₹)',
            line=dict(color='#00d2ff', width=2.5),
            fill='tozeroy', fillcolor='rgba(0, 210, 255, 0.1)'
        ))
        fig_vol.update_layout(
            title="Daily Transaction Volume Trend (₹)",
            template="plotly_dark",
            margin=dict(l=20, r=20, t=40, b=20),
            hovermode="x unified",
            height=320
        )
        st.plotly_chart(fig_vol, use_container_width=True)
        
    with col_t2:
        status_dist = engine.df_txn['status'].value_counts().reset_index()
        status_dist.columns = ['Status', 'Count']
        fig_pie = px.pie(
            status_dist, names='Status', values='Count',
            title="Transaction Status Distribution",
            color='Status',
            color_discrete_map={'SUCCESS': '#00cc88', 'FAILED': '#ff4b4b', 'PENDING': '#ffa500'},
            hole=0.45,
            template="plotly_dark"
        )
        fig_pie.update_layout(height=320, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_pie, use_container_width=True)
        
    col_t3, col_t4 = st.columns(2)
    with col_t3:
        fig_status_bar = go.Figure()
        fig_status_bar.add_trace(go.Bar(x=df_daily['date'], y=df_daily['success_count'], name='Success', marker_color='#00cc88'))
        fig_status_bar.add_trace(go.Bar(x=df_daily['date'], y=df_daily['failed_count'], name='Failed', marker_color='#ff4b4b'))
        fig_status_bar.add_trace(go.Bar(x=df_daily['date'], y=df_daily['pending_count'], name='Pending', marker_color='#ffa500'))
        fig_status_bar.update_layout(
            barmode='stack',
            title="Daily Success vs Failed vs Pending Transactions",
            template="plotly_dark",
            height=300,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_status_bar, use_container_width=True)
        
    with col_t4:
        df_hourly = engine.get_hourly_failure_trend()
        fig_hour = px.bar(
            df_hourly, x='hour', y='failure_rate',
            title="Hourly Payment Failure Rate (00:00 - 23:00)",
            labels={'hour': 'Hour of Day', 'failure_rate': 'Failure Rate'},
            color='failure_rate',
            color_continuous_scale='Reds',
            template="plotly_dark"
        )
        fig_hour.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_hour, use_container_width=True)

    st.markdown("---")
    st.subheader("UTR Data Quality & Failure Correlation")
    utr_m = engine.get_utr_health_metrics()
    
    u1, u2, u3, u4 = st.columns(4)
    u1.metric("Valid UTR Transactions", f"{utr_m['valid_utr_count']:,}")
    u2.metric("Invalid / Missing UTRs", f"{utr_m['invalid_or_missing_utr_count']:,}")
    u3.metric("Valid UTR Dispute Rate", f"{utr_m['valid_utr_dispute_rate']:.2%}")
    u4.metric("Invalid UTR Dispute Rate", f"{utr_m['invalid_utr_dispute_rate']:.2%}")


# ==========================================
# TAB 2: MERCHANT & CATEGORY RISK
# ==========================================
with tabs[1]:
    st.subheader("Merchant Category Performance & Dispute Exposure")
    df_cat = engine.get_merchant_category_metrics()
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        fig_cat_vol = px.bar(
            df_cat, x='total_amount', y='merchant_category', orientation='h',
            title="Transaction Volume by Category (₹)",
            color='total_amount', color_continuous_scale='Blues',
            template="plotly_dark"
        )
        fig_cat_vol.update_layout(height=360, margin=dict(l=20, r=20, t=40, b=20), yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_cat_vol, use_container_width=True)
        
    with col_c2:
        fig_cat_disp = px.bar(
            df_cat.sort_values('dispute_rate', ascending=True),
            x='dispute_rate', y='merchant_category', orientation='h',
            title="Dispute Rate by Merchant Category (%)",
            color='dispute_rate', color_continuous_scale='Reds',
            template="plotly_dark"
        )
        fig_cat_disp.update_layout(height=360, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_cat_disp, use_container_width=True)

    st.markdown("---")
    st.subheader("High-Risk Merchant Risk Matrix")
    
    risk_merchants = engine.get_high_risk_merchants(min_txns=3, top_n=20)
    st.dataframe(
        risk_merchants[[
            'merchant_id', 'merchant_name', 'merchant_category', 'merchant_status',
            'txn_count', 'chargeback_count', 'disputed_amount', 'chargeback_ratio', 'risk_score'
        ]].style.format({
            'disputed_amount': '₹{:,.2f}',
            'chargeback_ratio': '{:.1%}',
            'risk_score': '{:.1f}'
        }),
        use_container_width=True
    )


# ==========================================
# TAB 3: CUSTOMER & KYC 360
# ==========================================
with tabs[2]:
    st.subheader("Customer KYC Funnel & Risk Segment Breakdown")
    df_kyc = engine.get_kyc_status_breakdown()
    
    col_k1, col_k2 = st.columns(2)
    with col_k1:
        fig_kyc_vol = px.pie(
            df_kyc, names='kyc_status', values='total_amount',
            title="Transaction Volume by Customer KYC Status",
            hole=0.45,
            color='kyc_status',
            color_discrete_map={'VERIFIED': '#00cc88', 'PENDING': '#ffa500', 'REJECTED': '#ff4b4b', 'UNREGISTERED': '#636e72'},
            template="plotly_dark"
        )
        fig_kyc_vol.update_layout(height=320, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_kyc_vol, use_container_width=True)
        
    with col_k2:
        fig_kyc_disp = px.bar(
            df_kyc, x='kyc_status', y='dispute_rate',
            title="Dispute Rate by KYC Status (%)",
            color='dispute_rate', color_continuous_scale='Reds',
            template="plotly_dark"
        )
        fig_kyc_disp.update_layout(height=320, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_kyc_disp, use_container_width=True)

    st.markdown("---")
    st.subheader("High-Risk Repeat-Dispute Customer Watchlist")
    high_risk_users = engine.get_high_risk_users(top_n=20)
    st.dataframe(
        high_risk_users[[
            'user_id', 'full_name', 'kyc_status', 'risk_segment', 'city',
            'dispute_count', 'total_disputed_amount', 'avg_delay'
        ]].style.format({
            'total_disputed_amount': '₹{:,.2f}',
            'avg_delay': '{:.1f} days'
        }),
        use_container_width=True
    )


# ==========================================
# TAB 4: DISPUTES & CHARGEBACKS
# ==========================================
with tabs[3]:
    st.subheader("Chargeback Root Cause & Severity Analysis")
    df_reasons = engine.get_chargeback_reasons()
    df_sev = engine.get_chargeback_severity()
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        fig_reason = px.pie(
            df_reasons, names='reason_category', values='complaint_count',
            title="Dispute Reason Code Distribution",
            hole=0.45,
            template="plotly_dark"
        )
        fig_reason.update_layout(height=320, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_reason, use_container_width=True)
        
    with col_d2:
        fig_sev = px.bar(
            df_sev, x='severity', y='complaint_count',
            title="Dispute Severity Breakdown",
            color='severity',
            color_discrete_map={'CRITICAL': '#ff4b4b', 'HIGH': '#ff7675', 'MEDIUM': '#ffa500', 'LOW': '#00cc88'},
            template="plotly_dark"
        )
        fig_sev.update_layout(height=320, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_sev, use_container_width=True)

    st.markdown("---")
    st.subheader("Dispute Reporting Delays (>7 Days Indicates ATO / Fraud Syndicate)")
    df_cb = engine.df_cb
    fig_delay = px.histogram(
        df_cb, x='reporting_delay_days', nbins=30,
        title="Dispute Reporting Delay Distribution (Days from Transaction to Dispute)",
        labels={'reporting_delay_days': 'Reporting Delay (Days)'},
        color_discrete_sequence=['#00d2ff'],
        template="plotly_dark"
    )
    fig_delay.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_delay, use_container_width=True)


# ==========================================
# TAB 5: FRAUD RING GRAPH VISUALIZER
# ==========================================
with tabs[4]:
    st.subheader("Graph-First Fraud Ring & Mule Syndicate Explorer")
    
    rings = graph_engine.detect_shared_account_rings()
    clusters = graph_engine.detect_collusive_fraud_clusters()
    
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown(f"#### 🔗 Mule Merchant Rings (Shared Accounts: {len(rings)})")
        if rings:
            mule_summary = []
            for r in rings[:10]:
                mule_summary.append({
                    "Settlement Account": r['account_identifier'],
                    "Merchants": r['merchant_count'],
                    "Total Transactions": r['total_transactions'],
                    "Disputes": r['total_disputes'],
                    "Disputed Amount": f"₹{r['disputed_amount']:,.2f}",
                    "Risk Level": r['risk_level']
                })
            st.dataframe(pd.DataFrame(mule_summary), use_container_width=True)
            
    with col_g2:
        st.markdown(f"#### 🚨 Collusive Fraud Syndicates ({len(clusters)})")
        if clusters:
            clust_summary = []
            for c in clusters[:10]:
                clust_summary.append({
                    "Cluster ID": c['cluster_id'],
                    "Users": c['user_count'],
                    "Merchants": c['merchant_count'],
                    "Disputes": c['total_disputes'],
                    "Disputed Amount": f"₹{c['total_disputed_amount']:,.2f}",
                    "Risk Score": c['syndicate_risk_score'],
                    "Risk Tier": c['risk_tier']
                })
            st.dataframe(pd.DataFrame(clust_summary), use_container_width=True)

    st.markdown("---")
    st.subheader("Interactive Entity Ego Network Visualizer")
    
    col_s1, col_s2, col_s3 = st.columns([2, 1, 1])
    with col_s1:
        selected_node = st.text_input("Enter Merchant ID (e.g. MCH7045) or Customer ID (e.g. USR45826):", value="MCH7045")
    with col_s2:
        hops = st.slider("Hops Distance", min_value=1, max_value=2, value=1)
    with col_s3:
        st.write("")
        st.write("")
        btn_visualize = st.button("Render Network Graph", use_container_width=True)

    if selected_node:
        subg_data = graph_engine.extract_subgraph(selected_node, hops=hops)
        if "error" in subg_data:
            st.error(subg_data["error"])
        else:
            st.info(f"Visualizing network around **{subg_data['center_node']}** ({subg_data['total_nodes']} nodes, {subg_data['total_edges']} edges)")
            
            # Plotly Network Visualization
            edge_x = []
            edge_y = []
            edge_colors = []
            
            node_map = {n['id']: (n['x'], n['y']) for n in subg_data['nodes']}
            for edge in subg_data['edges']:
                if edge['source'] in node_map and edge['target'] in node_map:
                    x0, y0 = node_map[edge['source']]
                    x1, y1 = node_map[edge['target']]
                    edge_x.extend([x0, x1, None])
                    edge_y.extend([y0, y1, None])
                    
            edge_trace = go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=1.2, color='#74b9ff'),
                hoverinfo='none',
                mode='lines'
            )
            
            node_x = [n['x'] for n in subg_data['nodes']]
            node_y = [n['y'] for n in subg_data['nodes']]
            node_text = [n['label'] for n in subg_data['nodes']]
            node_colors = []
            node_sizes = []
            
            for n in subg_data['nodes']:
                if n['is_center']:
                    node_colors.append('#e74c3c') # Red for center
                    node_sizes.append(22)
                elif n['node_type'] == 'merchant':
                    node_colors.append('#f39c12') # Orange for merchant
                    node_sizes.append(15)
                elif n['node_type'] == 'settlement_account':
                    node_colors.append('#9b59b6') # Purple for account
                    node_sizes.append(14)
                else:
                    node_colors.append('#2ecc71') # Green for customer
                    node_sizes.append(12)
                    
            node_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                hoverinfo='text',
                text=[n['id'] for n in subg_data['nodes']],
                textposition="top center",
                textfont=dict(size=9, color="#ffffff"),
                hovertext=node_text,
                marker=dict(
                    color=node_colors,
                    size=node_sizes,
                    line=dict(width=2, color='#ffffff')
                )
            )
            
            fig_net = go.Figure(
                data=[edge_trace, node_trace],
                layout=go.Layout(
                    title=f"Network Ego Graph: {subg_data['center_node']}",
                    template="plotly_dark",
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20, l=20, r=20, t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    height=500
                )
            )
            st.plotly_chart(fig_net, use_container_width=True)


# ==========================================
# TAB 6: AGENTIQ AI COPILOT
# ==========================================
with tabs[5]:
    st.subheader("AgentIQ Conversational Assistant")
    st.markdown("Ask natural language queries regarding payment volumes, failure trends, high-risk entities, and fraud rings.")
    
    col_q1, col_q2, col_q3, col_q4 = st.columns(4)
    with col_q1:
        if st.button("📈 Daily Volume Trend", use_container_width=True):
            st.session_state['user_prompt'] = "Show daily transaction volume trend."
    with col_q2:
        if st.button("⚖️ Success vs Failed", use_container_width=True):
            st.session_state['user_prompt'] = "Compare successful vs failed transactions by day."
    with col_q3:
        if st.button("🚨 Top Disputed Merchants", use_container_width=True):
            st.session_state['user_prompt'] = "Which merchant has the highest chargeback count?"
    with col_q4:
        if st.button("🕸️ Detect Fraud Rings", use_container_width=True):
            st.session_state['user_prompt'] = "Detect mule accounts and fraud rings."

    user_query = st.text_input(
        "Enter your query:",
        value=st.session_state.get('user_prompt', 'Show total transaction amount by merchant category.')
    )
    
    if user_query:
        with st.spinner("Analyzing graph & executing analytics query..."):
            response = agent.answer_query(user_query)
            
        st.markdown(f"### {response['title']}")
        st.markdown(response['text'])
        
        if 'data' in response and isinstance(response['data'], pd.DataFrame) and not response['data'].empty:
            st.markdown("#### Query Results")
            st.dataframe(response['data'], use_container_width=True)
            
            # Auto-render chart if specified
            chart_type = response.get('chart_type')
            if chart_type == 'bar':
                fig_q = px.bar(response['data'], x=response['x'], y=response['y'], template="plotly_dark")
                fig_q.update_layout(height=350, margin=dict(l=20, r=20, t=30, b=20))
                st.plotly_chart(fig_q, use_container_width=True)
            elif chart_type == 'line':
                fig_q = px.line(response['data'], x=response['x'], y=response['y'], markers=True, template="plotly_dark")
                fig_q.update_layout(height=350, margin=dict(l=20, r=20, t=30, b=20))
                st.plotly_chart(fig_q, use_container_width=True)
            elif chart_type == 'pie':
                fig_q = px.pie(response['data'], names=response['names'], values=response['values'], hole=0.45, template="plotly_dark")
                fig_q.update_layout(height=350, margin=dict(l=20, r=20, t=30, b=20))
                st.plotly_chart(fig_q, use_container_width=True)
