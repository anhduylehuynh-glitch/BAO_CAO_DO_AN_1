import os
import sys

# Tối ưu hóa biến môi trường cho Ultralytics trên môi trường Docker
os.environ["YOLO_CONFIG_DIR"] = "/tmp"
os.environ["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"

import logging
logging.getLogger("ultralytics").setLevel(logging.ERROR)

from flask import Flask, request, jsonify
from ultralytics import YOLO
from PIL import Image
import io

app = Flask(__name__)

# NẠP SẴN MODEL VÀO RAM NGAY KHI KHỞI ĐỘNG
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, "best.pt")
model = YOLO(model_path)

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "Không tìm thấy file ảnh"}), 400
        
    file = request.files['file']
    try:
        img_bytes = file.read()
        img = Image.open(io.BytesIO(img_bytes))
        
        # Tối ưu kích thước ảnh trực tiếp trong RAM
        img.thumbnail((256, 256))
        if img.mode == "RGBA":
            img = img.convert("RGB")
            
        # Nhận diện siêu tốc (chỉ mất vài mili giây vì model có sẵn trên RAM)
        results = model(img, imgsz=160, conf=0.4, verbose=False)
        boxes = results[0].boxes
        
        if len(boxes) > 0:
            label_id = int(boxes[0].cls[0])
            label_name = model.names[label_id]
            return jsonify({"success": True, "label": label_name})
        else:
            return jsonify({"success": False})
            
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    # Chạy cục bộ ở cổng nội bộ 5000 ẩn phía sau Rails
    app.run(host='127.0.0.1', port=5000)