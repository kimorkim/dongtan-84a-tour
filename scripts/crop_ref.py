from PIL import Image
import os

img = Image.open("references/layout/original/84A.jpg")
out_dir = "references/layout/crops"
os.makedirs(out_dir, exist_ok=True)
w, h = img.size

# 1. Kitchen & Dining (center top)
crop_kitchen = img.crop((int(w * 0.30), int(h * 0.05), int(w * 0.55), int(h * 0.55)))
crop_kitchen.save(os.path.join(out_dir, "crop_ref_kitchen.png"))

# 2. Living Room (center bottom)
crop_living = img.crop((int(w * 0.28), int(h * 0.45), int(w * 0.60), int(h * 0.90)))
crop_living.save(os.path.join(out_dir, "crop_ref_living.png"))

# 3. Master Bed & Bath (left)
crop_master = img.crop((int(w * 0.04), int(h * 0.05), int(w * 0.35), int(h * 0.90)))
crop_master.save(os.path.join(out_dir, "crop_ref_master.png"))

# 4. Bedrooms 2 & 3 & Foyer (right)
crop_right = img.crop((int(w * 0.50), int(h * 0.05), int(w * 0.96), int(h * 0.90)))
crop_right.save(os.path.join(out_dir, "crop_ref_right.png"))

print("Cropped 4 reference sections successfully!")
