import os, shutil, random, argparse

def split_data(input_dir, output_train, output_val, split=0.2):
    classes = os.listdir(input_dir)
    for cls in classes:
        cls_path = os.path.join(input_dir, cls)
        if not os.path.isdir(cls_path):
            continue

        images = os.listdir(cls_path)
        random.shuffle(images)

        split_idx = int(len(images) * (1 - split))
        train_imgs = images[:split_idx]
        val_imgs = images[split_idx:]

        # Train folder
        train_cls_path = os.path.join(output_train, cls)
        os.makedirs(train_cls_path, exist_ok=True)
        for img in train_imgs:
            shutil.copy(os.path.join(cls_path, img), os.path.join(train_cls_path, img))

        # Val folder
        val_cls_path = os.path.join(output_val, cls)
        os.makedirs(val_cls_path, exist_ok=True)
        for img in val_imgs:
            shutil.copy(os.path.join(cls_path, img), os.path.join(val_cls_path, img))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", default="data/raw")
    parser.add_argument("--output_train", default="data/train")
    parser.add_argument("--output_val", default="data/val")
    parser.add_argument("--split", type=float, default=0.2)
    args = parser.parse_args()

    split_data(args.input_dir, args.output_train, args.output_val, args.split)
    print("✅ Dataset split complete!")

