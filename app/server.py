import os
from io import BytesIO
from pathlib import Path

import uvicorn
from fastai.vision import load_learner, open_image
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

export_file_name = 'export.pkl'
path = Path(__file__).parent
model_path = path / 'models' / export_file_name

# Training used pd.qcut tertiles: 0=low, 1=medium, 2=high ratings_count
POPULARITY_LABELS = {
    '0': 'Low',
    '1': 'Medium',
    '2': 'High',
}

learn = None


def get_learner():
    global learn
    if learn is None:
        if not model_path.exists():
            raise FileNotFoundError(
                f'Model not found at {model_path}. '
                'Ensure export.pkl is downloaded during the Docker build.'
            )
        learn = load_learner(path / 'models', export_file_name)
    return learn


def format_prediction(pred, pred_idx, probs):
    raw = str(pred)
    label = POPULARITY_LABELS.get(raw, raw)
    confidence = round(float(probs[pred_idx]) * 100, 1)
    return label, confidence, raw


async def homepage(request):
    html_file = path / 'index.html'
    return HTMLResponse(html_file.read_text())


async def health(request):
    return JSONResponse({'status': 'ok'})


async def analyze(request):
    img_data = await request.form()
    img_bytes = await img_data['file'].read()
    img = open_image(BytesIO(img_bytes))
    pred, pred_idx, probs = get_learner().predict(img)
    label, confidence, raw = format_prediction(pred, pred_idx, probs)
    return JSONResponse({
        'result': label,
        'confidence': confidence,
        'raw_class': raw,
    })


app = Starlette(
    routes=[
        Route('/', homepage),
        Route('/health', health),
        Route('/analyze', analyze, methods=['POST']),
        Mount('/static', StaticFiles(directory=path / 'static'), name='static'),
    ],
    middleware=[
        Middleware(
            CORSMiddleware,
            allow_origins=['*'],
            allow_headers=['X-Requested-With', 'Content-Type'],
        ),
    ],
)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    uvicorn.run(app=app, host='0.0.0.0', port=port, log_level='info')
