# streamlit_app.py
import streamlit as st
from crewai import Crew, Task, Process
from agents import classifier_agent, routing_agent, response_agent

st.title("🧭 Triage Agent")
q = st.text_area("Describe the issue:", height=140)

if st.button("Run"):
    if not q.strip():
        st.warning("Enter a query."); st.stop()

    classify_task = Task(
        description=f"""Classify this ticket and return STRICT JSON:
{{"issue_type":"...", "priority":"low|medium|high", "user_type":"vip|regular",
 "suggested_department":"billing|tech|operations|support", "confidence":0-1, "reason":"..." }}
Ticket: {q}""",
        agent=classifier_agent,
        expected_output="Strict JSON with keys: issue_type, priority, user_type, suggested_department, confidence, reason."
    )

    route_task = Task(
        description="Using classifier JSON, pick department and give 1-3 bullet reasons. Return STRICT JSON: {\"department\":\"...\",\"reasons\":[\"...\",\"...\"]}",
        agent=routing_agent,
        context=[classify_task],
        expected_output='Strict JSON with keys: department, reasons (list).'
    )

    respond_task = Task(
        description=f"Write a concise reply (<=200 words) using classifier + routing. Ticket: {q}",
        agent=response_agent,
        context=[classify_task, route_task],
        expected_output="A short, user-facing message (plain text)."
    )

    crew = Crew(
        agents=[classifier_agent, routing_agent, response_agent],
        tasks=[classify_task, route_task, respond_task],
        process=Process.sequential,
        verbose=False,
    )

    with st.spinner("Thinking..."):
        final = crew.kickoff()

    st.subheader("Final Reply")
    st.write(str(final))
    with st.expander("Classifier JSON"):
        st.write(str(classify_task.output))
    with st.expander("Routing Notes"):
        st.write(str(route_task.output))
