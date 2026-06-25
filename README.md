# Trust-Aware Dynamic Collaboration Framework

A Confidence-Calibrated Trust-Aware Dynamic Collaboration Framework for Autonomous Multi-Agent LLM Systems.

This repository implements a modular decision layer positioned between collaborating LLM agents. Instead of allowing unconditional error propagation, this layer evaluates trust dynamically, calibrates agent confidence, manages communication, and attributes failures.

---

## 🚀 Setup Instructions

### 1. Initialize Virtual Environment
Ensure you have Python 3.10+ installed.

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.venv\Scripts\activate

# Activate virtual environment (Linux/Mac)
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
Copy the example environment template and configure your LLM API keys:
```bash
cp .env.example .env
```
Open `.env` and fill in your keys (e.g. `GEMINI_API_KEY`, `OPENAI_API_KEY`). By default, `USE_SIMULATION=true` is enabled to let you test the entire workflow with simulated agents without making real API calls.

---

## 🏃 Running the Framework

### 1. Command-Line Demo
Run the CLI demo to execute a sample multi-agent task and watch trust/confidence scores update in real-time:
```bash
python run_demo.py
```

### 2. Launch Streamlit Web UI Dashboard
Launch the interactive dashboard to run tasks, visualize the dynamic routing graph, inspect trust score histories, and run batch evaluations:
```bash
streamlit run app/main.py
```

### 3. Run Unit Tests
Execute the automated test suites using `pytest`:
```bash
pytest tests/
```

---

## 🐳 Running with Docker (Phase 10 Containerization)

To spin up the entire framework (Redis caching instance, FastAPI backend, and Streamlit frontend) automatically inside isolated container networks, run:

```bash
# Build images and start all services
docker-compose up --build
```

Once running, the applications are available at:
* **Streamlit Dashboard Web UI:** `http://localhost:8501`
* **FastAPI Server API:** `http://localhost:8000`
* **Redis Instance:** `localhost:6379`
