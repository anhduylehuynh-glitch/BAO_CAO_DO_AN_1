from ultralytics import YOLO
import sys
import json
import os

os.environ["YOLO_CONFIG_DIR"] = "/tmp/Ultralytics"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.join(BASE_DIR, "best.pt")

model = YOLO(model_path)

image_path = sys.argv[1]

# TẮT LOG
results = model(image_path, verbose=False)

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