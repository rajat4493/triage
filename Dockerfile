FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DEFAULT_TIMEOUT=120 PIP_PROGRESS_BAR=off

# system deps
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

# upgrade pip (stabler downloads)
RUN python -m pip install --upgrade pip

# 1) Install PyTorch CPU wheels first (required for T5 to run)
RUN pip install --no-cache-dir --retries 5 --timeout 120 \
  --index-url https://download.pytorch.org/whl/cpu \
  torch==2.3.1

# 2) Install the rest (small wheels)
RUN pip install --no-cache-dir --retries 5 --timeout 120 \
  transformers==4.43.3 sentencepiece==0.2.0 streamlit==1.36.0 pydantic==2.8.2

# 3) Point HF caches to a writable place (and create it)
ENV TRANSFORMERS_CACHE=/tmp/hf_cache \
    HF_HOME=/tmp/hf_cache \
    HF_HUB_DISABLE_SYMLINKS_WARNING=1 \
    HF_MODEL=google/flan-t5-small
#RUN mkdir -p /app/.cache/huggingface

EXPOSE 7860
CMD ["bash","-lc","streamlit run app.py --server.port ${PORT:-7860} --server.address 0.0.0.0"]
