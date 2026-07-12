FROM python:3.10-slim-bookworm

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    --extra-index-url https://download.pytorch.org/whl/cpu

COPY app app/

# Book-cover model from capstone training repo (not the old Dropbox bird classifier)
ARG MODEL_URL=https://raw.githubusercontent.com/gtesdahl/mlg-06-capstone/master/final_model_export.pkl
RUN mkdir -p app/models \
    && curl -fsSL "$MODEL_URL" -o app/models/export.pkl \
    && python -c "from pathlib import Path; p=Path('app/models/export.pkl'); assert p.stat().st_size > 1_000_000, f'Model download failed ({p.stat().st_size} bytes)'"

ENV PORT=10000
EXPOSE 10000

CMD ["python", "app/server.py"]
