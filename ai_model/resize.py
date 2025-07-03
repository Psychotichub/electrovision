from PIL import Image
import os

# 🔁 Base paths
base_input_path = 'E:/ElectroVision AI/ai_model/dataset/images'
base_output_path = 'E:/ElectroVision AI/ai_model/dataset/images_resized'
target_size = (1920, 1080)  # Or (640, 640) for YOLOv8 default

# 📂 Folders to process
folders = ['train', 'val']

for folder in folders:
    input_dir = os.path.join(base_input_path, folder)
    output_dir = os.path.join(base_output_path, folder)

    os.makedirs(output_dir, exist_ok=True)

    print(f"\n📂 Processing: {folder}")

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff')):
            try:
                img_path = os.path.join(input_dir, filename)
                img = Image.open(img_path)

                resized_img = img.resize(target_size, Image.Resampling.LANCZOS)

                resized_img.save(os.path.join(output_dir, filename))
                print(f"✅ Resized: {filename}")
            except Exception as e:
                print(f"❌ Failed to resize {filename}: {e}")
