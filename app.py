import os, json, re, streamlit as st
from string import Template

# ---- Writable HF caches BEFORE importing transformers ----
CACHE_DIR = "/tmp/hf_cache"
os.environ.setdefault("TRANSFORMERS_CACHE", CACHE_DIR)
os.environ.setdefault("HF_HOME", CACHE_DIR)
os.environ.setdefault("HUGGINGFACE_HUB_CACHE", CACHE_DIR)
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
os.environ.setdefault("XDG_CACHE_HOME", CACHE_DIR)

# Modest CPU threading to reduce contention on Spaces
os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("MKL_NUM_THREADS", "2")

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import torch

@st.cache_resource(show_spinner=False)
def get_pipe():
    model_name = os.getenv("HF_MODEL", "google/flan-t5-small")  # try flan-t5-base for better quality
    torch.set_num_threads(int(os.getenv("TORCH_THREADS", "2")))
    tok = AutoTokenizer.from_pretrained(model_name, cache_dir=CACHE_DIR)
    mod = AutoModelForSeq2SeqLM.from_pretrained(model_name, cache_dir=CACHE_DIR)
    return pipeline(
        "text2text-generation",
        model=mod,
        tokenizer=tok,
        max_new_tokens=96,        # keep short for speed
        do_sample=False,          # deterministic
        num_beams=1,              # faster than beam search
        clean_up_tokenization_spaces=True
    )

gen = get_pipe()

def gen_text(prompt: str) -> str:
    return gen(prompt, num_return_sequences=1)[0]["generated_text"].strip()

def first_json(txt: str):
    m = re.search(r"\{.*\}", txt, flags=re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None

def repair_json(raw: str, schema_desc: str):
    prompt = f"""Instruction:
You will be given text that was supposed to be JSON. Repair it to valid JSON that matches this schema exactly:
{schema_desc}

Rules:
- Output JSON only. No code fences, no extra text.

Input:
{raw}

Output:
"""
    fixed = gen_text(prompt)
    return first_json(fixed)

# --- Lightweight rules (fallbacks) ---
SERVICE_MAP = {
    "refund": "Billing", "payment": "Billing", "invoice": "Billing",
    "login": "Identity", "password": "Identity", "account": "Identity",
    "slow": "Performance", "down": "Availability", "error": "Application"
}
TEAM_MAP = {
    "Billing": "Finance Ops",
    "Identity": "IAM",
    "Performance": "SRE",
    "Availability": "SRE",
    "Application": "App Support",
}
def heuristic_classify(text: str):
    t = text.lower()
    service = next((v for k, v in SERVICE_MAP.items() if k in t), "Application")
    is_request = any(w in t for w in ["request", "feature", "access", "please enable", "refund"])
    ticket_type = "request" if is_request else "incident"
    sev = "high" if any(w in t for w in ["urgent", "immediately", "down", "critical", "p1"]) else \
          ("medium" if any(w in t for w in ["not provided", "not working", "error", "failed", "pending"]) else "low")
    entities = [w for w in ["order", "invoice", "account", "payment", "refund", "login", "password", "server", "api"]
                if w in t]
    return {
        "ticket_type": ticket_type,
        "service": service,
        "subservice": None,
        "severity": sev,
        "summary": text.strip()[:240],
        "entities": entities
    }

def heuristic_route(c_json):
    service = (c_json.get("service") or "Application")
    team = TEAM_MAP.get(service, "App Support")
    sev = (c_json.get("severity") or "medium").lower()
    priority = {"high": "P1", "medium": "P2", "low": "P3"}.get(sev, "P2")
    return {"team": team, "priority": priority, "rationale": f"Routed by service={service} severity={sev}"}

# --- Few-shot templates via string.Template (no brace conflicts) ---
CLASSIFY_FEWSHOT_TPL = Template("""Instruction:
You are a ticket classifier. Extract fields and return STRICT JSON only with keys:
ticket_type ("incident"|"request"), service, subservice, severity ("low"|"medium"|"high"), summary, entities (array of strings).
Rules:
- JSON only. No extra text, no code fences.
- Use null if unknown.
- Keep values concise.

Input:
"My laptop cannot connect to Wi-Fi since morning."
Output:
{"ticket_type":"incident","service":"Network","subservice":null,"severity":"medium","summary":"Laptop cannot connect to Wi-Fi","entities":["laptop","wifi"]}

Input:
"I need a refund for order #123, double charged."
Output:
{"ticket_type":"request","service":"Billing","subservice":"Refunds","severity":"medium","summary":"Refund request for double charge on order #123","entities":["refund","order 123","double charge"]}

Input:
"$ticket_text"
Output:
""")

ROUTE_FEWSHOT_TPL = Template("""Instruction:
Given the ticket JSON, choose owning team and priority. Return JSON only with keys: team, priority ("P1"|"P2"|"P3"), rationale.

Input:
{"ticket_type":"request","service":"Billing","subservice":"Refunds","severity":"medium","summary":"Refund for order #123","entities":["refund","order 123"]}
Output:
{"team":"Finance Ops","priority":"P2","rationale":"Billing refund handled by Finance Ops; medium severity -> P2"}

Input:
$ticket_json
Output:
""")

REPLY_TEMPLATE_TPL = Template("""Instruction:
Write a short, customer-safe reply (70–110 words) based on the ticket and routing. Be clear, empathetic, no internal jargon. Plain text only (no JSON).

Input:
Ticket: $ticket_json
Routing: $routing_json

Output:
""")

def classify(text: str):
    prompt = CLASSIFY_FEWSHOT_TPL.substitute(ticket_text=text)
    raw = gen_text(prompt)
    j = first_json(raw)
    schema = """{
  "ticket_type": "incident|request",
  "service": "string|null",
  "subservice": "string|null",
  "severity": "low|medium|high",
  "summary": "string",
  "entities": ["string", ...]
}"""
    if j is None:
        j = repair_json(raw, schema)
    if j is None:
        j = heuristic_classify(text)
    return raw, j

def route(c_json):
    prompt = ROUTE_FEWSHOT_TPL.substitute(ticket_json=json.dumps(c_json, ensure_ascii=False))
    raw = gen_text(prompt)
    j = first_json(raw)
    schema = """{
  "team": "string",
  "priority": "P1|P2|P3",
  "rationale": "string"
}"""
    if j is None:
        j = repair_json(raw, schema)
    if j is None:
        j = heuristic_route(c_json)
    return raw, j

def draft_reply(c_json, r_json):
    prompt = REPLY_TEMPLATE_TPL.substitute(
        ticket_json=json.dumps(c_json, ensure_ascii=False),
        routing_json=json.dumps(r_json, ensure_ascii=False)
    )
    txt = gen_text(prompt)
    if not txt or len(txt.split()) < 20:
        txt = (f"Thanks for reaching out. We’ve routed your case to {r_json.get('team','our support team')} "
               f"with priority {r_json.get('priority','P3')}. We understand the issue: "
               f"{c_json.get('summary','your request/incident')}. "
               "We’re investigating and will update you with next steps. "
               "If you have screenshots or any additional details, please reply so we can help faster.")
    return txt.strip()

# ---- UI ----
st.title("Ticket Triage (T5)")
txt = st.text_area("Paste ticket text", height=160, placeholder="e.g., My refund is still pending. I need urgent resolution")
go = st.button("Triage", type="primary", disabled=not bool(txt.strip()))

if go:
    c_raw, c_json = classify(txt)
    st.subheader("Classification")
    st.code(c_raw or "—", language="json")
    with st.expander("Parsed JSON"):
        st.json(c_json)

    r_raw, r_json = route(c_json)
    st.subheader("Routing")
    st.code(r_raw or "—", language="json")
    with st.expander("Parsed JSON"):
        st.json(r_json)

    reply = draft_reply(c_json, r_json)
    st.subheader("Reply")
    st.write(reply)
