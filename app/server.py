import os
import sys
from io import BytesIO
from pathlib import Path

import uvicorn
from fastai.vision import load_learner, open_image
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, JSONResponse
from starlette.staticfiles import StaticFiles

export_file_name = 'export.pkl'
path = Path(__file__).parent
model_path = path / 'models' / export_file_name

app = Starlette()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_headers=['X-Requested-With', 'Content-Type'],
)
app.mount('/static', StaticFiles(directory=path / 'static'))

learn = None


def get_learner():
    global learn
    if learn is None:
        if not model_path.exists():
            raise FileNotFoundError(f'Model not found at {model_path}')
        learn = load_learner(path / 'models', export_file_name)
    return learn


@app.on_event('startup')
async def startup():
    get_learner()


@app.route('/')
async def homepage(request):
    html_file = path / 'index.html'
    return HTMLResponse(html_file.read_text())


@app.route('/health')
async def health(request):
    return JSONResponse({'status': 'ok'})


@app.route('/analyze', methods=['POST'])
async def analyze(request):
    img_data = await request.form()
    img_bytes = await img_data['file'].read()
    img = open_image(BytesIO(img_bytes))
    prediction = get_learner().predict(img)[0]
    return JSONResponse({'result': str(prediction)})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 7860))
    uvicorn.run(app=app, host='0.0.0.0', port=port, log_level='info')
