import os
import sys

# Ép hệ thống lưu cấu hình và cache biên dịch vào thư mục tmp cho phép ghi của Render
os.environ["YOLO_CONFIG_DIR"] = "/tmp"
os.environ["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
os.environ["PYTHONPYCACHEPREFIX"] = "/tmp/pycache"

import json
import time
import logging

# Chặn hoàn toàn log thừa tránh làm tràn bộ nhớ đệm STDOUT
logging.getLogger("ultralytics").setLevel(logging.ERROR)

print("SCRIPT START", file=sys.stderr)

t0 = time.time()
from ultralytics import YOLO
from ultralytics import SETTINGS

# Tắt đồng bộ hóa cấu hình trực tuyến và tính năng check update tự động
try:
    SETTINGS.update({"sync": False, "check": False})
except:
    pass

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

# Hạ độ phân giải ảnh đầu vào xuống mức cực thấp để CPU Render tính toán nhanh gọn
img.thumbnail((160, 160))

if img.mode == "RGBA":
    img = img.convert("RGB")

tmp_path = image_path + "_small.jpg"
img.save(tmp_path, "JPEG")
print(f"SIZE SAU RESIZE: {img.width}x{img.height}", file=sys.stderr)

t2 = time.time()
# imgsz=160 giúp mô hình chạy siêu tốc trên CPU yếu gói Free
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