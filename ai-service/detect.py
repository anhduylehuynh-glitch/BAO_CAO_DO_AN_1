import os
import sys
import json
import time

os.environ["YOLO_CONFIG_DIR"] = "/tmp/Ultralytics"
print("SCRIPT START", file=sys.stderr)

from ultralytics import YOLO
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, "best.pt")
model = YOLO(model_path)

image_path = sys.argv[1]
img = Image.open(image_path)

print(f"SIZE GOC: {img.width}x{img.height}", file=sys.stderr)

# 1. Chuyển đổi hệ màu trước khi xử lý kích thước nhằm tránh lỗi kênh Alpha
if img.mode == "RGBA":
    img = img.convert("RGB")

# 2. Sử dụng .resize() để ép chuẩn ma trận VUÔNG 640x640 khớp hoàn toàn với cấu hình lúc train
img_resized = img.resize((640, 640))

tmp_path = image_path + "_predict.jpg"
img_resized.save(tmp_path, "JPEG")

print(f"SIZE SAU RESIZE: {img_resized.width}x{img_resized.height}", file=sys.stderr)

t2 = time.time()
# 3. Cập nhật imgsz=640 để đồng bộ dữ liệu và hạ nhẹ conf xuống 0.35 để nhạy hơn với ảnh thực tế
results = model(
    tmp_path,
    imgsz=640,
    conf=0.35,
    verbose=False
)
print(f"PREDICT: {time.time()-t2:.2f}s", file=sys.stderr)

boxes = results[0].boxes

if len(boxes) > 0:
    # Lấy bounding box có score cao nhất (đầu tiên)
    best_box = boxes[0]
    label_id = int(best_box.cls[0])
    label_name = model.names[label_id]

    print(json.dumps({
        "success": True,
        "label": label_name
    }))
else:
    print(json.dumps({
        "success": False
    }))

# Dọn dẹp file tạm để tránh tràn bộ nhớ đệm Docker
if os.path.exists(tmp_path):
    try:
        os.remove(tmp_path)
    except:
        pass