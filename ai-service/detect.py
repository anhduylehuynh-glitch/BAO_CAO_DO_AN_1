import os
import sys

# Ép hệ thống nhận diện thư mục tmp
os.environ["YOLO_CONFIG_DIR"] = "/tmp"
os.environ["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"

import json
import time
import logging

# Chặn log ở mức độ hệ thống
logging.getLogger("ultralytics").setLevel(logging.ERROR)

print("SCRIPT START", file=sys.stderr)

t0 = time.time()
from ultralytics import YOLO
from ultralytics.utils import settings

# TẮT CHÍNH XÁC CÁC TÍNH NĂNG ĐỒNG BỘ/CẬP NHẬT CỦA ULTRALYTICS
settings.update({"sync": False, "check": False, " some_other_setting": False})

print(f"IMPORT: {time.time()-t0:.2f}s", file=sys.stderr)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, "best.pt")

t1 = time.time()
model = YOLO(model_path)
print(f"LOAD MODEL: {time.time()-t1:.2f}s", file=sys.stderr)

image_path = sys.argv[1]

from PIL import Image
img = Image.open(image_path)

print(f"SIZE GOC: {img.width}x{img.height}", file=sys.stderr)

# HẠ MẠNH kích thước ảnh thumbnail xuống để CPU không phải tính toán nhiều
img.thumbnail((320, 320))

if img.mode == "RGBA":
    img = img.convert("RGB")

tmp_path = image_path + "_small.jpg"
img.save(tmp_path, "JPEG")

print(f"SIZE SAU RESIZE: {img.width}x{img.height}", file=sys.stderr)

t2 = time.time()

# GIẢM ĐỘ PHÂN GIẢI NHẬN DIỆN XUỐNG 160 (Siêu nhẹ cho CPU Render Free)
results = model(
    tmp_path,
    imgsz=160, 
    conf=0.4,
    verbose=False
)
print(f"PREDICT: {time.time()-t2:.2f}s", file=sys.stderr)

boxes = results[0].boxes

if len(boxes) > 0:
    label_id = int(boxes[0].cls[0])
    label_name = model.names[label_id]
    print(json.dumps({"success": True, "label": label_name}))
else:
    print(json.dumps({"success": False}))