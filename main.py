# main.py
import json
import re
from typing import Literal
from pydantic import BaseModel, Field, ValidationError

from crewai import Crew, Task, Process
from agents import classifier_agent, routing_agent, response_agent
from mock_data import ticket_data, user_profiles

import os
# kill leftover env that forces LiteLLM default model
os.environ.pop("LITELLM_MODEL", None)

# ---------- Pydantic schema ----------
class TicketClassification(BaseModel):
    issue_type: Literal["Bonus Issue", "Technical Issue", "Login Problem", "Withdrawal Delay", "Other"]
    confidence: float = Field(..., ge=0, le=1)

# ---------- Helpers ----------
def extract_first_json(text: str) -> dict:
    """Grab the first {...} JSON object from text."""
    m = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not m:
        raise ValueError("No JSON object found in LLM output.")
    return json.loads(m.group(0))

# ---------- Data ----------
user = user_profiles[ticket_data["user_id"]]

# ---------- Tasks ----------
classify_task = Task(
    description=(
        "Classify this ticket message:\n"
        f"---\n{ticket_data['message']}\n---\n\n"
        "Return STRICT JSON only:\n"
        '{"issue_type": one of ["Bonus Issue","Technical Issue","Login Problem","Withdrawal Delay","Other"],'
        '"confidence": float 0..1}\n'
        "No extra text."
    ),
    expected_output='JSON: {"issue_type": "...", "confidence": 0.x}',
    agent=classifier_agent
)

route_task = Task(
    description=(
        "Decide department using the classification JSON and user context.\n"
        f"- VIP level: {user['vip_level']}\n"
        f"- Recent issues: {user['recent_issues']}\n"
        "Rules:\n"
        "- Bonus Issue -> Bonuses\n"
        "- Withdrawal Delay -> Payments\n"
        "- Technical Issue or Login Problem -> Tech\n"
        "- Otherwise -> Support Triage\n"
        "- If VIP is Gold+ and confidence < 0.7 -> Support Triage with VIP flag\n\n"
        "Return STRICT JSON only: {\"department\": \"...\", \"vip_escalation\": true/false}"
    ),
    expected_output='JSON: {"department": "...", "vip_escalation": true/false}',
    agent=routing_agent,
    context=[classify_task]  # passes classifier output
)

respond_task = Task(
    description=(
        "Write a short customer response using the ticket, classification, and routing decision.\n"
        f"Ticket: {ticket_data['message']}\n"
        f"User VIP level: {user['vip_level']}\n"
        "Tone: clear, polite, concise; acknowledge VIP if vip_escalation is true; avoid promises; state next step."
    ),
    expected_output="3–5 sentence reply ready to send.",
    agent=response_agent,
    context=[classify_task, route_task]
)

crew = Crew(
    agents=[classifier_agent, routing_agent, response_agent],
    tasks=[classify_task, route_task, respond_task],
    process=Process.sequential,
    verbose=True
)

if __name__ == "__main__":
    # Run the crew
    final = crew.kickoff()

    # Validate the classifier JSON (post‑run check)
    try:
        raw = str(classify_task.output)  # CrewAI stores the task result here
        data = extract_first_json(raw)
        validated = TicketClassification(**data)
        print("\n[Classifier JSON ✅ Valid]")
        print(validated.model_dump())
    except (ValidationError, ValueError, json.JSONDecodeError) as e:
        print("\n[Classifier JSON ❌ Invalid]")
        print(e)

    print("\n=== FINAL RESPONSE ===")
    print(final)
