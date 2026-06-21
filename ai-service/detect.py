import os

os.environ["YOLO_CONFIG_DIR"] = "/tmp/Ultralytics"

import sys
import json
import time
print("SCRIPT START", file=sys.stderr)

# đo thời gian import
t0 = time.time()

from ultralytics import YOLO

print(f"IMPORT: {time.time()-t0:.2f}s", file=sys.stderr)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, "best.pt")

# đo thời gian load model
t1 = time.time()

model = YOLO(model_path)

print(f"LOAD MODEL: {time.time()-t1:.2f}s", file=sys.stderr)

image_path = sys.argv[1]

from PIL import Image

img = Image.open(image_path)

print(
    f"SIZE GOC: {img.width}x{img.height}",
    file=sys.stderr
)

# Resize ảnh trước khi predict
img.thumbnail((640, 640))

tmp_path = image_path + "_small.jpg"

img.save(tmp_path)

print(
    f"SIZE SAU RESIZE: {img.width}x{img.height}",
    file=sys.stderr
)

# đo thời gian predict
t2 = time.time()

results = model(
    tmp_path,
    imgsz=320,
    conf=0.5,
    verbose=False
)
print(f"PREDICT: {time.time()-t2:.2f}s", file=sys.stderr)

boxes = results[0].boxes

if len(boxes) > 0:
    label_id = int(boxes[0].cls[0])
    label_name = model.names[label_id]

    print(json.dumps({
        "success": True,
        "label": label_name
    }))
else:
    print(json.dumps({
        "success": False
    }))