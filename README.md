Triage — A Minimal Agentic Router for Multi‑Agent Workflows
Triage is a lightweight, Python-based triage agent (router) that inspects an incoming user request and forwards it to the most suitable specialist agent. It’s ideal when you want a single entry point that can classify intent, fan out to domain agents (e.g., Q&A, retrieval, tools), and aggregate results — without pulling in a heavyweight orchestration stack. 
GitHub

Why this exists
Single entry-point: One API/process to receive all queries

Fast to extend: Add or modify agents in a single file

Model-agnostic: Uses [LiteLLM]-style config for LLM backends via litellm.config.yaml

Local-friendly: Ships with mock_data.py for quick demos and tests

Conceptually, a “triage agent” is a router: it analyzes user intent then hands off to specialized workers, returning a unified response — a common pattern in agentic systems.

Features
Intent routing: Basic classification of user prompts → picks target agent

Specialist agents: Define simple agents in agents.py (e.g., knowledge, tools, mock/demo)

Configurable models: Centralize LLM settings in litellm.config.yaml

.env driven secrets: Keep API keys and settings outside code

Batteries-included demo: mock_data.py for local testing without external services

Note: The exact agent set and logic live in agents.py and main.py. Adjust the sections below if your implementation differs. 
GitHub

Repository structure
bash
Copy
Edit
triage/
├─ main.py                 # App entry point: starts the triage flow / server / CLI
├─ agents.py               # Agent definitions + routing logic (triage + specialists)
├─ mock_data.py            # Local fixtures for demos/tests
├─ litellm.config.yaml     # Model/backend config for LiteLLM-compatible clients
├─ requirements.txt        # Python dependencies
├─ .env                    # Environment variables (not committed)
└─ __pycache__/            # Bytecode cache (ignored)
Source: repo file index. 
GitHub

Quickstart
1) Prerequisites
Python 3.10+ recommended

An OpenAI/compatible LLM key if your agents call real models

2) Clone and set up
bash
Copy
Edit
git clone https://github.com/rajat4493/triage
cd triage
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows (PowerShell):
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
3) Configure environment
Create a .env in the project root:

bash
Copy
Edit
cp .env .env.local  # if a sample exists; else create a fresh .env
Add keys/settings you need, e.g.:

ini
Copy
Edit
OPENAI_API_KEY=your_key_here
# Any other flags your code reads in main.py/agents.py
4) Configure models (optional)
Edit litellm.config.yaml to point at your preferred model(s), endpoints, or providers.
Examples (adjust to your provider/model names):

yaml
Copy
Edit
model_list:
  - model_name: gpt-4o
    litellm_params:
      model: openai/gpt-4o
      api_key: ${OPENAI_API_KEY}
5) Run
bash
Copy
Edit
python main.py
Depending on how main.py is implemented, this may:

Start a CLI loop, or

Start a web server (FastAPI/Flask), or

Expose a function to call the triage agent

If it spins up a server, check the console for the URL (e.g., http://127.0.0.1:8000).

How it works (typical flow)
Triage receives a prompt (from CLI/HTTP).

Classifier logic (simple rules or an LLM) determines the best target agent.

Handoff: The triage agent calls that specialized agent (e.g., “knowledge”, “tools”).

Aggregation: The result is normalized and returned to the caller.

Look in agents.py for the triage policy and specialist agents; in main.py for the application wiring and I/O. 
GitHub

Extending it
Add a new specialist agent
Open agents.py.

Create a new class/function (e.g., FinanceAgent) with a simple interface:

python
Copy
Edit
class FinanceAgent:
    name = "finance"
    description = "Answers portfolio and market questions."

    def run(self, query: str, context: dict) -> dict:
        # call tools/LLMs and return a normalized dict
        return {"agent": self.name, "answer": "..."}
Register it in whatever registry/list the triage uses (e.g., AGENTS = {...}).

Update routing
Add/modify rules in the triage classifier (keywords/intents → agent name).

Or swap to an LLM-based router by prompting a model with the available agents’ descriptions and asking for the best match.

Bring your own tools
If an agent needs tools (retrieval, web, code exec), attach them inside the agent:

RAG (vector DB), web search, internal APIs, calculators, etc.

Use mock_data.py to develop offline first.

Configuration reference
.env

OPENAI_API_KEY — for LLM calls (if used)

Any other secrets your code expects

litellm.config.yaml

model_list — map logical names to providers/models

Provider keys can be picked up from .env via ${...}

Examples
CLI (if applicable):

bash
Copy
Edit
python main.py
> "What is our refund policy?"
# Triage → KnowledgeAgent → returns policy snippet
HTTP (if applicable):

bash
Copy
Edit
curl -X POST http://localhost:8000/triage \
  -H "Content-Type: application/json" \
  -d '{"query":"Summarize today’s metrics"}'
Unit-ish test with mocks:

python
Copy
Edit
from agents import triage
print(triage("List top 3 FAQs"))
Roadmap
 Confidence scores + fallback agent

 Few‑shot examples for routing

 Structured tool calling (JSON schema)

 Streaming responses

 Telemetry (latency, win‑rate per agent)

Troubleshooting
No response / import error
Ensure the virtualenv is active and deps from requirements.txt are installed.

401/keys
Check .env is present and OPENAI_API_KEY is set; restart the app/shell.

Model not found
Verify the model name in litellm.config.yaml matches a configured provider.

License
Add your preferred license (MIT/Apache-2.0/BSD-3-Clause) here.
