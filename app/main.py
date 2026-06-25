import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import requests
import json
import time

# Configure page layouts and styles
st.set_page_config(
    page_title="Trust-Aware Multi-Agent Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom css for rich modern aesthetics
st.markdown("""
<style>
    .main { background-color: #fafafa; }
    .reportview-container .main .block-container{ max-width: 95%; }
    .stCard {
        background-color: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
        margin-bottom: 1rem;
    }
    h1, h2, h3 { font-family: 'DM Sans', sans-serif; color: #1e293b; }
    .stButton>button {
        background-color: #2563eb;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #1d4ed8;
        transform: scale(1.02);
    }
    .agent-pill {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 0.5rem;
    }
    .pill-success { background-color: #d1fae5; color: #065f46; }
    .pill-verify { background-color: #fef3c7; color: #92400e; }
    .pill-danger { background-color: #fee2e2; color: #991b1b; }
</style>
""", unsafe_allow_html=True)

# API Endpoint mapping
API_URL = "http://127.0.0.1:8000/api"

# Helper to check backend health
def check_health():
    try:
        res = requests.get(f"{API_URL}/health", timeout=2)
        return res.status_code == 200
    except:
        return False

# Sidebar config
st.sidebar.title("🛠️ Framework Control Panel")

is_healthy = check_health()
if is_healthy:
    st.sidebar.success("Backend API: Connected")
else:
    st.sidebar.error("Backend API: Offline. Ensure backend server is running on port 8000.")
    st.sidebar.info("Tip: Start backend with: uvicorn backend.app:app --port 8000")

# Run config settings
st.sidebar.subheader("Execution Settings")
mode = st.sidebar.radio("LLM Execution Mode", ["Simulated (Mock Agents)", "Real LLM APIs (LiteLLM)"])
complexity = st.sidebar.selectbox("Task Complexity", ["low", "medium", "high"])

st.sidebar.subheader("Decision Thresholds")
theta_accept = st.sidebar.slider("Accept Threshold (theta_accept)", 0.3, 0.95, 0.65, 0.05)
theta_verify = st.sidebar.slider("Verify Threshold (theta_verify)", 0.1, 0.6, 0.35, 0.05)

st.title("🤖 Confidence-Calibrated Trust-Aware Framework")
st.caption("Adaptive Collaboration Decision Layer for Multi-Agent Large Language Models")

# Create tabs
tab1, tab2, tab3 = st.tabs(["🚀 Run Tasks", "📈 Trust Evolution", "🔬 Batch Experiments"])

# TAB 1: RUN TASKS
with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Submit Prompt")
        query_input = st.text_area(
            "Enter natural language query / task statement:",
            value="Write a literature review on Vision Transformer calibration issues.",
            height=100
        )
        
        run_btn = st.button("Run Framework Pipeline")
        
        if run_btn:
            if not is_healthy:
                st.error("Cannot run query. Backend API is offline.")
            else:
                with st.spinner("Executing framework collaboration states..."):
                    payload = {
                        "query": query_input,
                        "complexity": complexity,
                        "use_simulation": (mode == "Simulated (Mock Agents)")
                    }
                    try:
                        t0 = time.time()
                        res = requests.post(f"{API_URL}/query", json=payload)
                        elapsed = time.time() - t0
                        
                        if res.status_code == 200:
                            st.session_state["last_run_result"] = res.json()
                            st.session_state["run_time"] = elapsed
                            st.success(f"Task executed successfully in {elapsed:.2f}s!")
                        else:
                            st.error(f"Error executing task: {res.text}")
                    except Exception as e:
                        st.error(f"Failed to communicate with API: {e}")
                        
    # Display results
    if "last_run_result" in st.session_state:
        res_data = st.session_state["last_run_result"]
        result = res_data["result"]
        trajectory = res_data["trajectory"]
        metrics = res_data["metrics"]
        
        with col2:
            st.subheader("Framework Output Summary")
            
            # KPI Cards
            kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
            with kpi_col1:
                st.metric("Status", result.get("status", "").upper())
            with kpi_col2:
                st.metric("Avg Calibrated Conf", f"{result.get('average_confidence', 0.0):.2f}")
            with kpi_col3:
                st.metric("Total Tokens", f"{metrics['token_usage']['total']:,}")
                
            st.markdown("### Aggregated Final Response")
            st.info(result.get("response", ""))

        st.divider()
        st.markdown("### 📋 Detailed Collaboration Trajectory Trace")
        
        # Draw Trajectory Steps
        for step in trajectory:
            role = step["role"].upper()
            agent = step["agent_name"]
            desc = step["task_description"]
            decision = step["decision"]
            response = step["response"]
            r_conf = step["raw_confidence"]
            c_conf = step["calibrated_conf"]
            trust = step["trust_score"]
            reasoning = step["reasoning"]
            
            # Select pill class
            if decision == "ACCEPT":
                pill_html = '<span class="agent-pill pill-success">ACCEPTED</span>'
            elif decision == "VERIFY":
                pill_html = '<span class="agent-pill pill-verify">VERIFIED</span>'
            else:
                pill_html = '<span class="agent-pill pill-danger">REJECTED</span>'
                
            with st.expander(f"Step {step['step']}: {role} - {agent} ({decision})"):
                st.markdown(f"**Task Description:** {desc}")
                st.markdown(f"**Decision Status:** {pill_html}", unsafe_allow_html=True)
                st.markdown(f"**Metrics:** Raw Conf: `{r_conf:.2f}` | Calibrated Conf: `{c_conf:.2f}` | Trust Score: `{trust:.2f}`")
                st.markdown(f"**Response:** {response}")
                st.markdown(f"**Reasoning Details:** *{reasoning}*")

# TAB 2: TRUST EVOLUTION
with tab2:
    st.subheader("Dynamic Trust Score Trajectories")
    
    if st.button("Refresh Trust History") or "trust_history_loaded" not in st.session_state:
        if is_healthy:
            try:
                res = requests.get(f"{API_URL}/trust")
                if res.status_code == 200:
                    st.session_state["trust_history"] = res.json()["history"]
                    st.session_state["current_trust"] = res.json()["trust_scores"]
                    st.session_state["trust_history_loaded"] = True
            except Exception as e:
                st.error(f"Failed to fetch trust: {e}")
                
    if "trust_history" in st.session_state and st.session_state["trust_history"]:
        history = st.session_state["trust_history"]
        current = st.session_state["current_trust"]
        
        # Display current scores in cards
        if len(current) > 0:
            current_cols = st.columns(len(current))
            for idx, (role, score) in enumerate(current.items()):
                with current_cols[idx]:
                    st.metric(role.capitalize() + " Trust", f"{score:.2f}")

        # Render History Chart
        fig = go.Figure()
        for role, points in history.items():
            scores = points
            steps = list(range(len(scores)))
            fig.add_trace(go.Scatter(x=steps, y=scores, mode='lines+markers', name=role.capitalize()))
            
        fig.update_layout(
            title="Agent Trust Score Convergence Over Tasks",
            xaxis_title="Step Index",
            yaxis_title="Trust Score",
            yaxis_range=[0.0, 1.05],
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)

# TAB 3: BATCH EXPERIMENTS
with tab3:
    st.subheader("🔬 Comparative Benchmark Evaluations")
    st.caption("Runs batch simulations to compare Proposed Calibrated Framework against Static Baselines.")
    
    exp_col1, exp_col2 = st.columns([1, 2])
    with exp_col1:
        num_runs = st.number_input("Number of Simulated Runs:", min_value=5, max_value=100, value=15)
        
        st.markdown("**Simulate Agent Skills (True Success Probabilities):**")
        r_skill = st.slider("Research Agent Skill", 0.5, 1.0, 0.85)
        w_skill = st.slider("Writing Agent Skill", 0.5, 1.0, 0.75)
        rev_skill = st.slider("Reviewer Agent Skill", 0.5, 1.0, 0.70)
        
        run_exp_btn = st.button("Trigger Comparative Experiment")
        
    if run_exp_btn:
        if not is_healthy:
            st.error("Cannot run evaluation. Backend API is offline.")
        else:
            with st.spinner("Executing comparative baseline run iterations..."):
                payload = {
                    "num_runs": num_runs,
                    "research_skill": r_skill,
                    "writer_skill": w_skill,
                    "reviewer_skill": rev_skill
                }
                try:
                    res = requests.post(f"{API_URL}/evaluate", json=payload)
                    if res.status_code == 200:
                        st.session_state["exp_result"] = res.json()
                        st.success("Experiment completed!")
                    else:
                        st.error(f"Evaluation error: {res.text}")
                except Exception as e:
                    st.error(f"Connection error: {e}")

    if "exp_result" in st.session_state:
        exp_res = st.session_state["exp_result"]
        proposed = exp_res["proposed"]
        baseline = exp_res["baseline"]
        comp = exp_res["comparison_metrics"]
        
        # Display comparison table
        with exp_col2:
            st.markdown("### Experiment Metrics Summary")
            
            # Format dataframe
            df = pd.DataFrame({
                "Metric": ["Task Success Rate", "Calibration Error (ECE)", "Avg Tokens Used", "Avg Latency (s)", "Agent Interactions"],
                "Proposed Framework": [f"{proposed['success_rate']:.1%}", f"{proposed['ece']:.3f}", f"{proposed['avg_tokens']:,.0f}", f"{proposed['avg_latency']:.2f}", proposed["interactions"]],
                "Baseline Framework": [f"{baseline['success_rate']:.1%}", f"{baseline['ece']:.3f}", f"{baseline['avg_tokens']:,.0f}", f"{baseline['avg_latency']:.2f}", baseline["interactions"]]
            })
            st.table(df)
            
            # Highlights
            acc_diff = comp["accuracy_improvement_pct"]
            tokens_saved = comp["tokens_saved_pct"]
            
            st.info(
                f"🌟 **Key Research Finding:** The proposed framework improved overall task success rate by "
                f"**{acc_diff:+.1f}%** while reducing token consumption by **{tokens_saved:.1f}%** due to "
                f"adaptive pipeline bypassing!"
            )
            
            # Draw side-by-side Plotly bar charts
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=["Proposed Framework", "Baseline Framework"],
                y=[proposed["success_rate"]*100, baseline["success_rate"]*100],
                marker_color=["#2563eb", "#94a3b8"],
                name="Success Rate %"
            ))
            fig.update_layout(
                title="Task Success Rate Comparison (%)",
                yaxis_title="Success Rate (%)",
                yaxis_range=[0, 105],
                template="plotly_white",
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
