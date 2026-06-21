import os
import sys
import json
import time
from PIL import Image

# Ép lưu cache và cấu hình vào thư mục /tmp được cấp quyền trên Render
os.environ["YOLO_CONFIG_DIR"] = "/tmp/Ultralytics"
os.environ["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
os.environ["PYTHONPYCACHEPREFIX"] = "/tmp/pycache"

# Tắt bớt luồng dư thừa để CPU Render không bị quá tải
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

print("SCRIPT START", file=sys.stderr)

from ultralytics import YOLO
from ultralytics import SETTINGS

try:
    SETTINGS.update({"sync": False, "check": False})
except:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, "best.pt")

# Tải model AI
model = YOLO(model_path)

# Nhận đường dẫn ảnh truyền từ Rails
image_path = sys.argv[1]
img = Image.open(image_path)

print(f"SIZE GOC: {img.width}x{img.height}", file=sys.stderr)

# CHUẨN HÓA KÍCH THƯỚC: Thay vì thumbnail, ta dùng resize chuẩn 640x640 
# giúp khớp hoàn toàn với ma trận ảnh đầu vào lúc bạn train model.
img_resized = img.resize((640, 640))

# Chuyển đổi định dạng nếu là ảnh RGBA (tránh lỗi kênh màu)
if img_resized.mode == "RGBA":
    img_resized = img_resized.convert("RGB")

tmp_path = image_path + "_predict.jpg"
img_resized.save(tmp_path, "JPEG")

# ĐO THỜI GIAN VÀ DỰ ĐOÁN
t2 = time.time()
# - Đổi imgsz lên 640 để trùng khớp độ phân giải nhận diện mẫu tốt nhất
# - Giảm conf xuống 0.35 để bắt được các ảnh chụp thực tế có độ sáng/góc nghiêng nhẹ
results = model(tmp_path, imgsz=640, conf=0.35, verbose=False)
print(f"PREDICT TIME: {time.time()-t2:.2f}s", file=sys.stderr)

boxes = results[0].boxes

if len(boxes) > 0:
    # Lấy ra bounding box có độ tin cậy cao nhất (vị trí đầu tiên)
    best_box = boxes[0]
    label_id = int(best_box.cls[0])
    label_name = model.names[label_id]

    print(json.dumps({
        "success": True,
        "label": label_name
    }))
else:
    print(json.dumps({
        "success": False,
        "message": "Không tìm thấy vùng đặc trưng phù hợp trên ảnh"
    }))

# Dọn dẹp file tạm để tiết kiệm dung lượng ổ đĩa cho Render
if os.path.exists(tmp_path):
    try:
        os.remove(tmp_path)
    except:
        pass