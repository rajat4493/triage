#!/usr/bin/env bash
set -euo pipefail

# -------- Config --------
: "${PORT:=7860}"                      # fallback if platform didn’t inject
: "${OLLAMA_MODEL:=llama3.2:1b}"      # small, CPU-friendly
: "${OLLAMA_HOST:=127.0.0.1:11434}"
: "${HOME:=/home/user}"
: "${OLLAMA_HOME:=$HOME/.ollama}"
: "${OLLAMA_MODELS:=$OLLAMA_HOME/models}"

export HOME OLLAMA_HOST OLLAMA_HOME OLLAMA_MODELS OLLAMA_MODEL

# -------- Ensure writable dirs --------
mkdir -p "$OLLAMA_MODELS"
# If you previously used /data and hit "permission denied", take ownership now:
if [ -d "/data/.ollama" ]; then
  # best effort; ignore errors if we don't own it
  chown -R "$(id -u)":"$(id -g)" /data/.ollama || true
fi

# -------- Start Ollama in background --------
ollama serve &
OL_PID=$!

# -------- Wait for Ollama to be ready --------
tries=0
until curl -fsS "http://$OLLAMA_HOST/api/tags" >/dev/null 2>&1; do
  tries=$((tries+1))
  if [ "$tries" -gt 60 ]; then
    echo "Ollama failed to become ready." >&2
    exit 1
  fi
  sleep 1
done

# -------- Pull the model (idempotent) --------
ollama pull "$OLLAMA_MODEL" || true

# -------- Launch Streamlit on the platform port --------
exec streamlit run app.py --server.port "$PORT" --server.address 0.0.0.0
