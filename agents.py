import os
from crewai import LLM

ollama_tag = os.getenv("OLLAMA_MODEL", "llama3.2:1b")

llm = LLM(
    model=ollama_tag,                 # e.g. "llama3.2:1b" or "qwen2.5:1.5b-instruct"
    base_url="http://localhost:11434",
    temperature=0.2,
    timeout=60
)
classifier_agent = Agent(
    role="Ticket Classifier",
    goal="Understand and classify support issues",
    backstory="You help determine issue types quickly for support teams.",
    verbose=True,
    llm=llm
)

routing_agent = Agent(
    role="Routing Advisor",
    goal="Determine which department should handle the ticket",
    backstory="You know the internal routing rules and department scopes.",
    verbose=True,
    llm=llm
)

response_agent = Agent(
    role="Support Responder",
    goal="Draft a clear, polite support response based on issue and user type",
    backstory="Your work for Evoke iGaming company and your name is Barney.You use company tone and prioritize VIP experiences.",
    verbose=True,
    llm=llm
)
