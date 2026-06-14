import os, argparse
from PIL import Image

def resize_images(input_dir, output_dir, size=224):
    classes = os.listdir(input_dir)
    for cls in classes:
        cls_path = os.path.join(input_dir, cls)
        if not os.path.isdir(cls_path):
            continue

        out_cls_path = os.path.join(output_dir, cls)
        os.makedirs(out_cls_path, exist_ok=True)

        for img_name in os.listdir(cls_path):
            try:
                # ✅ Skip non-image files
                if not img_name.lower().endswith((".jpg", ".jpeg", ".png")):
                    print(f"⚠️ Skipping non-image file: {img_name}")
                    continue

                img_path = os.path.join(cls_path, img_name)
                img = Image.open(img_path).convert("RGB")
                img = img.resize((size, size))
                img.save(os.path.join(out_cls_path, img_name))
            except Exception as e:
                print(f"❌ Error resizing {img_name}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", required=True)
    parser.add_argument("--output_dir", required=True)
    parser.add_argument("--size", type=int, default=224)
    args = parser.parse_args()

    resize_images(args.input_dir, args.output_dir, args.size)
    print("✅ Resizing complete!")

