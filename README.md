# 🔐 LLM AI Security Framework

## 🎯 AIM
To build a "defensive security framework for Large Language Models (LLMs)" that simulates attacks, monitors anomalies, and enforces guardrails, ensuring trustworthy, compliant, and safe enterprise AI deployments.



## 📌 Overview
Modern LLM-powered applications (chatbots, copilots, RAG pipelines) face risks like prompt injection, jailbreaks, data leakage, bias exploitation, and PII exposure.  
This project introduces a "Three-team AI Security Framework":

- Red Team → simulates adversarial attacks.  
- Blue Team → monitors, detects, and logs anomalies.  
- Filter Team → enforces proactive guardrails before/after the LLM.  

Together, they create a continuous feedback loop that improves LLM security.



## ⚙️ Tech Stack
- LLMs: OpenAI GPT, Anthropic Claude, Llama (via Ollama)  
- Framework: FastAPI (API layer)  
- Attack Simulation: YAML prompt library for red-teaming  
- Defense & Monitoring: Custom filters, anomaly scoring, structured logs (JSONL), ELK/Grafana integration (optional)  
- Infra: Python, Docker
- Visualization: Grafana/Kibana dashboards for monitoring  



## 🌟 Features
- 🔴 Red Teaming → adversarial prompt injections, jailbreak attempts, bias triggers, PII extraction  
- 🔵 Blue Teaming → anomaly detection, JSONL security logs, scoring, monitoring  
- 🟢 Filter Team → pre-filter user inputs (regex, classifiers), post-filter outputs (toxic/unsafe/PII masking)  
- 📊 Metrics → Attack Success Rate (ASR), Detection Rate (DR), False Positive Rate (FPR), Latency overhead  
- 🚀 Deployable → Run locally via `uvicorn` or in containers with Docker/K8s  
- 🔒 Safe Fallback Mode → `[echo]` mode when no model is configured  



## 📂 Folder Structure


```
.
├── README.md
├── requirements.txt
├── .env.example
├── docker-compose.yml
├── app/
│   ├── main.py            # FastAPI app: pre-filters -> model -> post-filters + blue-team logging
│   ├── filters.py         # Filter Team: input/output checks (regex PII, basic toxicity, injections)
│   ├── provider.py        # LLM provider abstraction (Ollama or echo fallback)
│   └── blue_team.py       # Blue Team: JSON security logs + simple anomaly scoring
├── redteam/
│   ├── prompts.yaml       # Red Team cases (safe examples)
│   └── run_redteam.py     # Executes tests against /chat and logs results
└── evaluation/
    └── metrics.py         # Aggregates red-team results into ASR/DR/FPR/Latency
```



## In bash

#Setup
   

- python -m venv .venv
- source .venv/Scripts/activate   # Windows (Git Bash)
- pip install --upgrade pip
- pip install -r requirements.txt
- cp .env.example .env

- For safe echo mode, leave OLLAMA_* commented out in .env.
- For Ollama, install Ollama
 - ollama run llama3.1



#Run the API locally (MVP)
- uvicorn app.main:app --reload --port 8000
  
#Test a normal request:
  
- curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '{"user_input":"Hello! can you summarize: red vs blue vs filter?"}'
- Security logs write to `logs/security.log` and `logs/requests.log` (JSONL).


#Execute Red‑Team Suite

python redteam/run_redteam.py --base-url http://localhost:8000 --outfile reports/run.json
python evaluation/metrics.py --infile reports/run.json
- ASR = Attack Success Rate (unsafe output slipped through)
- DR  = Detection Rate (blue/filter caught it)
- FPR/FNR = False positives / negatives
- Latency = p50/p95 of end‑to‑end API calls

- Reports are saved into `reports/` as JSON/CSV.


 #Hardening Checklist (iterate)

- Add real moderation endpoints (e.g., OpenAI/Claude safety, custom toxicity/PII classifiers).
- Add anomaly detection using semantic similarity (embedding) of known-bad payloads.
- Add rate limits & user auth (e.g., API keys/JWT) in `app/main.py`.
- Send logs to a SIEM (ELK/Datadog). Docker Compose placeholder is in `docker-compose.yml`.
- Add CI gate: run `redteam/run_redteam.py` on PRs and fail if ASR > threshold.



#Docker (optional)

docker build -t llm-ai-security -f Dockerfile.app .
docker run --rm -p 8000:8000 --env-file .env llm-ai-security

ELK/Grafana are intentionally **not** included by default to keep this light. Add your preferred stack later.


## Safety & Responsible Use
This project is **for defense**. Red-team prompts are safe and generic. Do not use it to build systems that produce or help produce harm.


## 📊 Impact
- Reduced LLM jailbreak success rate by ~90% through Red/Blue/Filter guardrails.  
- Achieved zero PII leakage in tested scenarios while keeping False Positive Rate ≤5%.  
- Added only ~150 ms p95 latency overhead, enabling secure yet responsive LLM apps. 


## 👨‍💻 Author
- Nandini Kosgi
- LinkedIn: https://www.linkedin.com/in/nandinikosgi/
  

