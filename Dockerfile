# Use slim Python image
FROM python:3.10-slim

# System deps
RUN apt-get update && apt-get install -y curl git && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | bash
ENV OLLAMA_MODELS=/root/.ollama/models
# (Optional) change model here if you use another one
ENV OLLAMA_MODEL=llama2

# Workdir & copy code
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest (app.py, agents.py, litellm.config.yaml, etc.)
COPY . /app

# Pull the model at build time (cached layer)
RUN ollama serve & sleep 3 && ollama pull $OLLAMA_MODEL && pkill ollama || true

# Expose HF port
EXPOSE 7860

# Start Ollama + Streamlit
CMD bash -lc 'ollama serve & sleep 3 && python -m streamlit run app.py --server.address 0.0.0.0 --server.port ${PORT:-7860}'
