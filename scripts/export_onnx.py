"""Export the capstone fastai model to ONNX for lightweight inference.

Requires fastai/torch (dev only — not used in production):
  pip install fastai==1.0.61 torch torchvision

Usage:
  python scripts/export_onnx.py /path/to/final_model_export.pkl
"""

import sys
from pathlib import Path

import torch
from fastai.vision import load_learner, open_image


def export(model_path: Path, output_path: Path):
    learn = load_learner(model_path.parent, model_path.name)
    learn.model.eval()

    sample = open_image(next(Path('app/static/images').glob('*.jpg')))
    batch = learn.data.one_item(sample)[0]
    h, w = batch.shape[-2], batch.shape[-1]
    dummy = torch.randn(1, 3, h, w)

    torch.onnx.export(
        learn.model,
        dummy,
        str(output_path),
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={'input': {0: 'batch', 2: 'h', 3: 'w'}, 'output': {0: 'batch'}},
        opset_version=11,
    )
    print(f'Exported {output_path} ({output_path.stat().st_size} bytes)')


if __name__ == '__main__':
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('final_model_export.pkl')
    out = Path('app/models/book_cover_model.onnx')
    out.parent.mkdir(parents=True, exist_ok=True)
    export(src, out)
