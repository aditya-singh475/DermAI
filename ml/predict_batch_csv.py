# src/predict_batch_csv.py

import os
import csv
import json
import argparse
import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model

SUPPORTED_EXTS = (".jpg", ".jpeg", ".png")

def load_model_and_classes(model_path, class_map_path):
    model = load_model(model_path)
    with open(class_map_path) as f:
        class_indices = json.load(f)
    inv_map = {v: k for k, v in class_indices.items()}
    return model, inv_map

def iter_image_paths(root_dir, recursive=False):
    if recursive:
        for dirpath, _, filenames in os.walk(root_dir):
            for name in filenames:
                if name.lower().endswith(SUPPORTED_EXTS):
                    yield os.path.join(dirpath, name)
    else:
        for name in os.listdir(root_dir):
            if name.lower().endswith(SUPPORTED_EXTS):
                yield os.path.join(root_dir, name)

def preprocess_image(img_path, img_size=(224, 224)):
    img = Image.open(img_path).convert("RGB")
    img = img.resize(img_size)
    arr = np.array(img, dtype=np.float32) / 255.0
    return np.expand_dims(arr, axis=0)

def main(args):
    # Prepare model and classes
    model, inv_map = load_model_and_classes(args.model_path, args.class_map_path)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(args.output_csv), exist_ok=True)

    total = 0
    written = 0

    with open(args.output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "filepath", "predicted_class", "confidence"])

        for img_path in iter_image_paths(args.image_dir, recursive=args.recursive):
            total += 1
            try:
                arr = preprocess_image(img_path, img_size=(args.width, args.height))
                preds = model.predict(arr, verbose=0)
                cls_id = int(np.argmax(preds))
                conf = float(np.max(preds))
                cls_name = inv_map.get(cls_id, str(cls_id))

                # Confidence filtering (optional)
                if conf >= args.min_confidence:
                    writer.writerow([
                        os.path.basename(img_path),
                        os.path.abspath(img_path),
                        cls_name,
                        f"{conf:.6f}"
                    ])
                    written += 1
                else:
                    if args.include_low_confidence:
                        writer.writerow([
                            os.path.basename(img_path),
                            os.path.abspath(img_path),
                            cls_name,
                            f"{conf:.6f}"
                        ])
                        written += 1
                    else:
                        print(f"Skipped (low conf {conf:.3f}): {img_path}")

            except Exception as e:
                print(f"Error processing '{img_path}': {e}")

    print(f"Done. Scanned: {total} images, Written to CSV: {written}")
    print(f"CSV saved at: {os.path.abspath(args.output_csv)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch predict images and save to CSV.")
    parser.add_argument("--image_dir", required=True, help="Folder containing images.")
    parser.add_argument("--output_csv", default="model/reports/predictions.csv", help="Output CSV path.")
    parser.add_argument("--model_path", default="model/models/skin_model.h5", help="Path to trained model.")
    parser.add_argument("--class_map_path", default="model/models/class_indices.json", help="Path to class map JSON.")
    parser.add_argument("--width", type=int, default=224, help="Resize width.")
    parser.add_argument("--height", type=int, default=224, help="Resize height.")
    parser.add_argument("--recursive", action="store_true", help="Recurse into subfolders.")
    parser.add_argument("--min_confidence", type=float, default=0.0, help="Min confidence to include.")
    parser.add_argument("--include_low_confidence", action="store_true", help="Include predictions below min_confidence.")
    args = parser.parse_args()
    main(args)
