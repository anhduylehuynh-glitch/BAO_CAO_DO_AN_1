import os
import sys

# Khống chế thư mục cấu hình và pycache ghi file vào /tmp
os.environ["YOLO_CONFIG_DIR"] = "/tmp/Ultralytics"
os.environ["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
os.environ["PYTHONPYCACHEPREFIX"] = "/tmp/pycache"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

from flask import Flask, request, jsonify
from ultralytics import YOLO
from ultralytics import SETTINGS
from PIL import Image
import io

try:
    SETTINGS.update({"sync": False, "check": False})
except:
    pass

app = Flask(__name__)

# Nạp model trực tiếp vào bộ nhớ RAM duy nhất một lần khi container khởi động
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, "best.pt")
model = YOLO(model_path)

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "No file"}), 400
    
    file = request.files['file']
    try:
        img = Image.open(io.BytesIO(file.read()))
        
        # Chuyển đổi màu nếu là ảnh RGBA để tránh lỗi kênh Alpha
        if img.mode == "RGBA":
            img = img.convert("RGB")
            
        # Ép chuẩn ma trận vuông 640x640 khớp hoàn toàn với cấu hình lúc train model
        img_resized = img.resize((640, 640))
        
        # Dự đoán với cấu hình tối ưu độ nhạy cho ảnh chụp camera thực tế
        results = model(img_resized, imgsz=640, conf=0.35, verbose=False)
        boxes = results[0].boxes
        
        if len(boxes) > 0:
            best_box = boxes[0]
            label_name = model.names[int(best_box.cls[0])]
            return jsonify({"success": True, "label": label_name})
            
        return jsonify({"success": False, "message": "Không tìm thấy vùng đặc trưng phù hợp"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)