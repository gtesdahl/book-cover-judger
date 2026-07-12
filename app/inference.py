import numpy as np
from io import BytesIO
from pathlib import Path

import onnxruntime as ort
from PIL import Image

MODEL_FILE = 'book_cover_model.onnx'
MODEL_PATH = Path(__file__).parent / 'models' / MODEL_FILE

POPULARITY_LABELS = {
    '0': 'Low',
    '1': 'Medium',
    '2': 'High',
}

IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
IMAGENET_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)
IMAGE_SIZE = (384, 256)  # height, width — matches exported fastai learner

_session = None


def get_session():
    global _session
    if _session is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f'Model not found at {MODEL_PATH}')
        _session = ort.InferenceSession(
            str(MODEL_PATH),
            providers=['CPUExecutionProvider'],
        )
    return _session


def resize_pad_reflect(arr: np.ndarray, target_h: int, target_w: int) -> np.ndarray:
    h, w, _ = arr.shape
    scale = min(target_w / w, target_h / h)
    new_w, new_h = int(w * scale), int(h * scale)
    resized = np.array(Image.fromarray(arr).resize((new_w, new_h), Image.BILINEAR))
    pad_h = target_h - new_h
    pad_w = target_w - new_w
    top, bottom = pad_h // 2, pad_h - pad_h // 2
    left, right = pad_w // 2, pad_w - pad_w // 2
    return np.pad(resized, ((top, bottom), (left, right), (0, 0)), mode='reflect')


def preprocess_image(image_bytes: bytes) -> np.ndarray:
    target_h, target_w = IMAGE_SIZE
    img = Image.open(BytesIO(image_bytes)).convert('RGB')
    arr = resize_pad_reflect(np.array(img), target_h, target_w)
    arr = arr.astype(np.float32) / 255.0
    arr = arr.transpose(2, 0, 1)
    arr = (arr - IMAGENET_MEAN[:, None, None]) / IMAGENET_STD[:, None, None]
    return arr[None, ...].astype(np.float32)


def predict(image_bytes: bytes):
    tensor = preprocess_image(image_bytes)
    logits = get_session().run(None, {'input': tensor})[0][0]
    idx = int(logits.argmax())
    exp_logits = np.exp(logits - logits.max())
    probs = exp_logits / exp_logits.sum()
    raw = str(idx)
    label = POPULARITY_LABELS.get(raw, raw)
    confidence = round(float(probs[idx]) * 100, 1)
    return label, confidence, raw
