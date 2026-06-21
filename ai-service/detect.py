import os

os.environ["YOLO_CONFIG_DIR"] = "/tmp/Ultralytics"

import sys
import json
import time

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

# đo thời gian predict
t2 = time.time()

results = model(image_path, verbose=False)

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