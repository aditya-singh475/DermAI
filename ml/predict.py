import os
import json
import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model

# ✅ Config
IMAGE_DIR = "data/val/acne"  # 🔁 Change this to any folder you want
MODEL_PATH = "model/models/skin_model.h5"
CLASS_MAP_PATH = "model/models/class_indices.json"
IMG_SIZE = (224, 224)

# ✅ Load model + class map
model = load_model(MODEL_PATH)
with open(CLASS_MAP_PATH) as f:
    class_indices = json.load(f)
inv_map = {v: k for k, v in class_indices.items()}

# ✅ Loop through images
print(f"🔍 Scanning folder: {IMAGE_DIR}")
for img_name in os.listdir(IMAGE_DIR):
    if not img_name.lower().endswith((".jpg", ".jpeg", ".png")):
        print(f"⚠️ Skipping non-image file: {img_name}")
        continue

    img_path = os.path.join(IMAGE_DIR, img_name)
    try:
        img = Image.open(img_path).convert("RGB")
        img = img.resize(IMG_SIZE)
        arr = np.array(img) / 255.0
        arr = np.expand_dims(arr, axis=0)

        pred = model.predict(arr)
        cls_id = int(np.argmax(pred))
        conf = float(np.max(pred))
        cls_name = inv_map[cls_id]

        print(f"🖼️ {img_name} → 🧠 {cls_name} ({conf:.4f})")
    except Exception as e:
        print(f"❌ Error processing {img_name}: {e}")
