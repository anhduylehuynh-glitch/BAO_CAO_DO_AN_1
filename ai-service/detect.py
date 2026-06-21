import os
import sys

# Ép lưu cache và cấu hình vào thư mục /tmp được cấp quyền ghi trên Render
os.environ["YOLO_CONFIG_DIR"] = "/tmp"
os.environ["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
os.environ["PYTHONPYCACHEPREFIX"] = "/tmp/pycache"

import json
from PIL import Image

# Tắt bớt luồng tính toán dư thừa để không nghẽn CPU Render gói Free
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

from ultralytics import YOLO
from ultralytics import SETTINGS

# Tắt tính năng tự động kiểm tra cập nhật trực tuyến để khởi động tức thì
try:
    SETTINGS.update({"sync": False, "check": False})
except:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, "best.pt")

# Tải model
model = YOLO(model_path)

image_path = sys.argv[1]
img = Image.open(image_path)

# Hạ kích thước ảnh gốc xuống cực nhỏ ngay trên bộ nhớ RAM để xử lý nhanh
img.thumbnail((160, 160))
if img.mode == "RGBA":
    img = img.convert("RGB")

tmp_path = image_path + "_small.jpg"
img.save(tmp_path, "JPEG")

# Dự đoán với kích thước ma trận ảnh nhỏ nhất (imgsz=160)
results = model(tmp_path, imgsz=160, conf=0.4, verbose=False)
boxes = results[0].boxes

if len(boxes) > 0:
    label_id = int(boxes[0].cls[0])
    label_name = model.names[label_id]
    print(json.dumps({"success": True, "label": label_name}))
else:
    print(json.dumps({"success": False}))

# Dọn dẹp file tạm sau khi nhận diện xong
if os.path.exists(tmp_path):
    os.remove(tmp_path)