# Book Cover Judger — Agent Handoff Document

**Last updated:** July 13, 2026  
**Purpose:** Onboard the next agent/thread focused on **ML v2 (data + model)** in Google Colab.  
**Owner:** Grant Tesdahl (`gtesdahl`)

---

## 1. Project summary

**Book Cover Judger** is a 2020 MLG capstone artifact: upload a book cover image, predict popularity as **High / Medium / Low**. The live site demonstrates that Grant learned ML and deployment. It is **not** primarily a McKinsey portfolio piece — the **About Me** section is intentionally frozen as a 2020 time capsule.

| Item | Value |
|------|-------|
| **Deploy repo** | https://github.com/gtesdahl/book-cover-judger |
| **Training repo (v1)** | https://github.com/gtesdahl/mlg-06-capstone |
| **Live URL** | https://www.bookcoverjudger.com |
| **Render URL** | https://book-cover-judger-c5bz.onrender.com |
| **Hosting cost** | **$0/month** (Render free tier) |
| **Domain** | `bookcoverjudger.com` via Cloudflare (~$10/yr at-cost) |

---

## 2. What the previous thread accomplished

### Phase 1 — Restore & cut costs ($7/mo → $0)
- Revived a ~6-year-old fast.ai/Starlette app that was down
- Targeted Hugging Face Spaces → pivoted to **Render free tier** (HF requires PRO for new Docker/Gradio Spaces as of July 2026)
- Fixed bugs: `client.js` label mapping, missing `import sys`, broken Dockerfile `RUN`
- Removed Dropbox model dependency; bundled model via build/download

### Phase 2 — Fix wrong model & labels
- **Root cause of `092.Nighthawk` predictions:** Dropbox `export.pkl` was a **CUB-200 bird classifier** (fast.ai demo), not the book model
- Switched to `final_model_export.pkl` from `mlg-06-capstone` (classes `0`/`1`/`2`)
- Mapped tertiles → Low / Medium / High; added confidence % in API + UI
- Fixed Starlette 0.27+ routing (`Route`/`Mount` instead of `@app.route`)

### Phase 2b — ONNX for 512 MB RAM
- PyTorch+fastai (~600 MB RSS) **OOM'd** on Render free tier (512 MB) → `/analyze` returned 502
- Exported v1 model to **ONNX** (`app/models/book_cover_model.onnx`, ~84 MB)
- Production stack: `onnxruntime` + Pillow only (no PyTorch in Docker)
- Inference runs in thread pool; session warmed on startup

### Phase 3a — UX & domain
- **Example covers** on Judge page (model-verified, not ratings-verified):
  - High: *River of Blue Fire* (`10084.jpg`)
  - Medium: *Homo Faber* (`10009.jpg`)
  - Low: *Mary, Queen of Scots* (`10096.jpg`)
- Domain `bookcoverjudger.com` on Cloudflare → Render (orange cloud, certs green)
- Header logo: **`book cover judger.`** (spaces; browser title updated)
- Left **About Me**, Methodology body text, and footer as 2020 artifacts (`book-cover-judger` hyphenation preserved there)

---

## 3. Current architecture

```
Browser (index.html + client.js)
    │  POST /analyze (multipart image)
    ▼
Starlette (app/server.py) — port from $PORT (default 10000)
    │  run_in_threadpool
    ▼
ONNX Runtime (app/inference.py)
    │  preprocess: pad-resize 384×256, ImageNet norm
    ▼
book_cover_model.onnx  →  logits  →  argmax  →  Low/Medium/High + confidence
```

| File | Role |
|------|------|
| `app/server.py` | HTTP routes: `/`, `/health`, `/analyze`, static files |
| `app/inference.py` | Preprocessing + ONNX inference + label mapping |
| `app/models/book_cover_model.onnx` | **v1 production model** (committed, ~84 MB) |
| `app/index.html` | Single-page UI (Bootstrap/jQuery, 2020 design) |
| `app/static/js/client.js` | Upload, example covers, error handling |
| `scripts/export_onnx.py` | Regenerate ONNX from fastai `export.pkl` (dev only) |
| `Dockerfile` | Python 3.10-slim + onnxruntime |
| `render.yaml` | Free web service, `healthCheckPath: /health` |

### API: `POST /analyze`
- **Request:** `multipart/form-data`, field `file`
- **Response (200):**
  ```json
  {"result": "Low", "confidence": 67.4, "raw_class": "0"}
  ```
- **Labels:** `0`→Low, `1`→Medium, `2`→High (ratings_count tertiles from training)

---

## 4. v1 model — archived reference

### Training (2020)
- **Notebook:** `mlg-06-capstone/Tesdahl_Modeling.ipynb`
- **Data:** `books.csv` + `cover_images/{bookID}.jpg` scraped from Goodreads
- **Label:** `pd.qcut(ratings_count, 3)` → classes `'0'`, `'1'`, `'2'`
  - Low: ≤ ~217 ratings | Medium: ~218–2,567 | High: > ~2,567
- **Architecture:** ResNet34 transfer learning, fastai v1
- **Reported accuracy:** ~44%
- **Export:** `final_model_export.pkl` in capstone repo root (~84 MB)

### Important caveats for v2 agent
1. **Popularity ≠ cover design quality** — model learns visual correlates of fame
2. **Example "Expected: High"** means *model prediction*, not ground-truth ratings tier
3. **Preprocessing must match export:** 384×256 pad-resize + ImageNet normalization (see `inference.py`)
4. **Do not use** old Dropbox URL — it was the wrong (bird) model

### Regenerate v1 ONNX (if needed)
```bash
pip install fastai==1.0.61 torch torchvision onnx
git clone https://github.com/gtesdahl/mlg-06-capstone.git
python scripts/export_onnx.py mlg-06-capstone/final_model_export.pkl
# Output: app/models/book_cover_model.onnx
```

---

## 5. Infrastructure notes

### Render (free tier)
- **512 MB RAM / 0.1 CPU** — why ONNX was required
- **Cold starts:** ~15 min idle → ~30–90s wake on first request
- **Deploy:** push to `master` → auto-deploy, or Manual Deploy in dashboard
- **Blueprint name:** `book-cover-judger free`

### Cloudflare + Render
- Both `@` and `www` CNAME → `book-cover-judger-c5bz.onrender.com`
- **Proxied (orange cloud)** enabled after initial verification
- SSL/TLS: **Full** mode
- Remove **AAAA** records if verification fails

### Domains no longer used
- `book-cover-judger.com` (hyphenated) — removed from Render; let lapse
- `book-cover-judger.onrender.com` — dead URL (old service); use `-c5bz` subdomain

### Hugging Face
- User revoked exposed write token during Phase 1 — do not reference old token
- New Gradio/Docker Spaces require HF PRO ($9/mo) as of July 2026

---

## 6. Known issues & lessons (don't repeat)

| Issue | Cause | Fix applied |
|-------|-------|-------------|
| `Not Found` + `x-render-routing: no-server` | Wrong/old Render URL | Use `book-cover-judger-c5bz.onrender.com` |
| Git LFS pointer as model | 130-byte stub in Docker | Bundle ONNX in repo |
| `092.Nighthawk` labels | Wrong Dropbox bird model | Use capstone `final_model_export.pkl` |
| Stuck on "Analyzing..." | 502 OOM + JS didn't handle errors | ONNX + client error handling |
| `@app.route` crash | Starlette 0.27 API change | `Route`/`Mount` pattern |
| Example covers wrong | Ratings tier ≠ model prediction | Scan training set for confident predictions |

---

## 7. Explicitly out of scope (unless user asks)

- **About Me section** — keep as 2020 artifact
- **Methodology/footer hyphenation** — historical; update only when v2 model ships
- **McKinsey portfolio positioning**
- **Hugging Face migration** (unless user gets PRO)

---

## 8. Next phase — ML v2 (for the new thread)

### User goals
- Build **new model + data pipeline** iteratively in **Google Colab**
- Learn / refresh deep learning using **MIT Hands-On Deep Learning** course materials (user will provide in new thread)
- **Archive v1** — keep capstone repo + current ONNX untouched as record
- Work **collaboratively** — user wants to understand each step, not black-box automation

### Recommended work order

#### Session 1 — Data pipeline v2 (notebook in `mlg-06-capstone` or Colab)
- **Replace Goodreads HTML scraping** with **Open Library API**
  - Search: `https://openlibrary.org/search.json`
  - Covers: `https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg`
- Target: 20k–50k fiction covers with rating/popularity metadata
- Document label strategy (keep tertiles for v2 baseline, or refine)
- Output: clean CSV + image folder or parquet manifest

#### Session 2 — EDA & baseline
- Class balance, image size distribution, sample visualizations
- Compare v1 dataset stats vs v2

#### Session 3–5 — Model v2
- **Framework:** PyTorch + `timm` (EfficientNet-B0 or ViT-small) or fastai v2
- Train in Colab (GPU); track accuracy, confusion matrix, per-class F1
- **Target:** beat 44% baseline on same 3-class task first (apples-to-apples)
- Align concepts with user's MIT course notebooks when provided

#### Session 6 — Deploy v2
- Export to ONNX (reuse `scripts/export_onnx.py` pattern or torch.onnx)
- Swap `app/models/book_cover_model.onnx` in deploy repo
- Update Methodology section with v2 results (not About Me yet)
- Optional UI: show all three class probabilities as bar chart

### Swapping model into production
1. Train/export new ONNX in Colab
2. Replace `app/models/book_cover_model.onnx` in `book-cover-judger` repo
3. Update `IMAGE_SIZE` / preprocessing in `inference.py` if architecture input size changed
4. Update `POPULARITY_LABELS` if label schema changes
5. Push to `master` → Render auto-deploys
6. Re-scan example covers against new model (same script pattern as Phase 3a)

### Tag v1 archive (suggested, not done yet)
```bash
# In book-cover-judger repo
git tag -a v1-capstone-2020 -m "ONNX export of 2020 MLG capstone model"
git push origin v1-capstone-2020
```

---

## 9. Key repositories & artifacts

| Resource | Location |
|----------|----------|
| Deploy / website | https://github.com/gtesdahl/book-cover-judger |
| v1 training data + notebooks | https://github.com/gtesdahl/mlg-06-capstone |
| v1 fastai export | `mlg-06-capstone/final_model_export.pkl` |
| v1 ONNX (production) | `book-cover-judger/app/models/book_cover_model.onnx` |
| Example cover sources | `mlg-06-capstone/cover_images/{bookID}.jpg` |
| MIT course materials | **User to provide** in new thread |

---

## 10. Local dev quick start

```bash
git clone https://github.com/gtesdahl/book-cover-judger.git
cd book-cover-judger
pip install -r requirements.txt
cd app && PORT=10000 python server.py
# Open http://localhost:10000
```

Docker:
```bash
docker build -t book-cover-judger .
docker run --rm -p 10000:10000 -e PORT=10000 book-cover-judger
```

---

## 11. Prompt starter for the next thread

Copy this into a new Cursor thread:

> I'm continuing Book Cover Judger ML v2. Read `docs/HANDOFF.md` in https://github.com/gtesdahl/book-cover-judger and https://github.com/gtesdahl/mlg-06-capstone. v1 is live and archived — do not change About Me. Start Colab Session 1: Open Library data pipeline. I'll share my MIT Hands-On Deep Learning materials. Work iteratively so I learn each step.

---

## 12. Contact / ownership

- **GitHub:** `gtesdahl`
- **Original capstone:** Machine Learning Guild Apprentice Program, August 2020
- **Domain registrar:** Cloudflare

---

*End of handoff. The deployment/infrastructure thread is complete. Next thread owns data + model v2.*
