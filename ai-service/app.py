import os
import sys

os.environ["YOLO_CONFIG_DIR"] = "/tmp"
os.environ["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"

from flask import Flask, request, jsonify
from ultralytics import YOLO
from PIL import Image
import io

app = Flask(__name__)

# Nạp model trực tiếp vào RAM ngay khi container khởi động
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
        # Hạ kích thước ảnh ngay trên RAM để tăng tốc tính toán
        img.thumbnail((160, 160))
        if img.mode == "RGBA":
            img = img.convert("RGB")
            
        results = model(img, imgsz=160, conf=0.4, verbose=False)
        boxes = results[0].boxes
        
        if len(boxes) > 0:
            label_name = model.names[int(boxes[0].cls[0])]
            return jsonify({"success": True, "label": label_name})
        return jsonify({"success": False})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    # Chạy trên localhost cổng 5000 ẩn phía sau Rails
    app.run(host='127.0.0.1', port=5000, debug=False)