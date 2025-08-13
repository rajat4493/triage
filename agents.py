# agents.py
from crewai import Agent, LLM

# Point to your local Ollama
llm = LLM(
    model="ollama/llama2",                   # or llama3, mistral, etc. (must be pulled in Ollama)
    base_url="http://localhost:11434",
    temperature=0.3,
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
