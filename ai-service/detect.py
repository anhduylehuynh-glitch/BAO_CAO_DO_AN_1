import os
import sys

# Khống chế PyTorch và OpenMP chỉ dùng đúng 1 luồng xử lý để tránh nghẽn CPU Render
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

# Chỉ định thư mục tạm cho Ultralytics để không tốn thời gian khởi tạo file cấu hình mới
os.environ["YOLO_CONFIG_DIR"] = "/tmp"
os.environ["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
os.environ["PYTHONPYCACHEPREFIX"] = "/tmp/pycache"

import json
import time
import logging

# Tắt toàn bộ log cảnh báo hệ thống
logging.getLogger("ultralytics").setLevel(logging.ERROR)

from ultralytics import YOLO
from ultralytics import SETTINGS

try:
    SETTINGS.update({"sync": False, "check": False})
except:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, "best.pt")
model = YOLO(model_path)

image_path = sys.argv[1]

from PIL import Image
img = Image.open(image_path)

# Thu nhỏ ảnh về kích thước siêu nhỏ trước khi truyền vào ma trận quét
img.thumbnail((160, 160))
if img.mode == "RGBA":
    img = img.convert("RGB")

tmp_path = image_path + "_small.jpg"
img.save(tmp_path, "JPEG")

# Giảm imgsz xuống 160 giúp CPU xử lý ảnh cực nhanh mà vẫn bắt được khung CCCD
results = model(
    tmp_path,
    imgsz=160,
    conf=0.4,
    verbose=False
)

boxes = results[0].boxes

if len(boxes) > 0:
    label_id = int(boxes[0].cls[0])
    label_name = model.names[label_id]
    print(json.dumps({"success": True, "label": label_name}))
else:
    print(json.dumps({"success": False}))