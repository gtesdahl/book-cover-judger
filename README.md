---
title: Book Cover Judger
emoji: 📚
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
license: mit
app_port: 10000
---

# Book Cover Judger

Upload a book cover image and predict its popularity (High, Medium, or Low) using a ResNet34 CNN trained with fastai on Goodreads data.

Built as a capstone project for the Machine Learning Guild Apprentice Program.

## Live demo

**Primary hosting (free):** [www.bookcoverjudger.com](https://www.bookcoverjudger.com) (Render: `book-cover-judger-c5bz.onrender.com`)

> **Note:** Render's free tier sleeps after ~15 minutes of inactivity. The first visit after sleep may take 30–90 seconds to load while the server and model start up.

## Hugging Face Spaces

As of July 2026, Hugging Face requires a [PRO subscription](https://huggingface.co/pro) ($9/month) to create new Gradio or Docker Spaces on CPU Basic hardware. This project is configured for Docker-based deployment and can be moved to HF Spaces if you upgrade to PRO later.

## Local development

```bash
docker build -t book-cover-judger .
docker run --rm -p 10000:10000 -e PORT=10000 book-cover-judger
```

Open http://localhost:10000

## Deploy to Render (free tier)

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → **New** → **Blueprint**
3. Connect the `gtesdahl/book-cover-judger` repository
4. Render reads `render.yaml` and creates a **free** web service
5. Cancel any paid Render plan once the free service is live

## Project structure

| Path | Purpose |
|------|---------|
| `app/server.py` | Starlette API routes |
| `app/inference.py` | ONNX preprocessing + inference |
| `app/models/book_cover_model.onnx` | v1 production model (~84 MB) |
| `app/index.html` | Frontend UI |
| `scripts/export_onnx.py` | Regenerate ONNX from fastai export (dev) |
| `Dockerfile` | Container for deployment |
| `render.yaml` | Render free-tier config |
| `docs/HANDOFF.md` | Agent turnover doc for ML v2 thread |

## Model file

Production inference uses **ONNX Runtime** (`app/models/book_cover_model.onnx`, ~84MB) — lightweight enough for Render's free tier (512 MB RAM). The original fastai export lives in the [capstone training repo](https://github.com/gtesdahl/mlg-06-capstone).

To regenerate the ONNX file from the capstone model:
```bash
pip install fastai==1.0.61 torch torchvision onnx
python scripts/export_onnx.py /path/to/final_model_export.pkl
```

Training labels are numeric tertiles (`0`, `1`, `2`) mapped to Low/Medium/High at inference time.

## Original capstone

Trained August 2020 for the Machine Learning Guild Apprentice Program. ~44% accuracy on 3-class Goodreads cover popularity prediction.

## Agent handoff (ML v2)

See **[docs/HANDOFF.md](docs/HANDOFF.md)** for full turnover documentation: architecture, v1 model archive, infrastructure, lessons learned, and the recommended Colab roadmap for the next phase.
