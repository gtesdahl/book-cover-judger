import os
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from starlette.applications import Starlette
from starlette.concurrency import run_in_threadpool
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from inference import get_session, predict

path = Path(__file__).parent


@asynccontextmanager
async def lifespan(app):
    # Warm up ONNX session at startup so first /analyze is fast
    await run_in_threadpool(get_session)
    yield


async def homepage(request):
    html_file = path / 'index.html'
    return HTMLResponse(html_file.read_text())


async def health(request):
    return JSONResponse({'status': 'ok'})


async def analyze(request):
    try:
        img_data = await request.form()
        img_bytes = await img_data['file'].read()
        label, confidence, raw = await run_in_threadpool(predict, img_bytes)
        return JSONResponse({
            'result': label,
            'confidence': confidence,
            'raw_class': raw,
        })
    except Exception as exc:
        return JSONResponse({'error': str(exc)}, status_code=500)


app = Starlette(
    lifespan=lifespan,
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
