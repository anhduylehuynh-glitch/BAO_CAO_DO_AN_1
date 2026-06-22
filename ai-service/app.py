import os
import sys
import io

# Khống chế các thư mục cấu hình ghi file vào phân vùng tạm /tmp của Render
os.environ["YOLO_CONFIG_DIR"] = "/tmp"
os.environ["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
os.environ["PYTHONPYCACHEPREFIX"] = "/tmp/pycache"
os.environ["OMP_NUM_THREADS"] = "1"

from flask import Flask, request, jsonify
from ultralytics import YOLO
from PIL import Image

app = Flask(__name__)

# Nạp model trực tiếp vào bộ nhớ RAM ngay khi deploy thành công để xử lý siêu tốc
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, "best.pt")
model = YOLO(model_path)

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "Không tìm thấy file ảnh gửi lên"}), 400
    
    file = request.files['file']
    try:
        img = Image.open(io.BytesIO(file.read()))
        
        # Xử lý hệ màu tránh lỗi kênh Alpha của ảnh PNG
        if img.mode == "RGBA":
            img = img.convert("RGB")
            
        # Ép chuẩn ma trận vuông 640x640 để nhận diện chính xác nhất
        img_resized = img.resize((640, 640))
        
        # Nhận diện trực tiếp từ biến ảnh trong RAM (không ghi file ra ổ đĩa)
        results = model(img_resized, imgsz=640, conf=0.35, verbose=False)
        boxes = results[0].boxes
        
        if len(boxes) > 0:
            label_name = model.names[int(boxes[0].cls[0])]
            return jsonify({"success": True, "label": label_name})
        
        return jsonify({"success": False, "message": "Không nhận diện được đặc trưng thẻ"})
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    # Chạy trên host nội bộ 127.0.0.1, cổng 5000 phía sau proxy Rails
    app.run(host='127.0.0.1', port=5000, debug=False)