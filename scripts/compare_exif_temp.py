import sys
from PIL import Image
import piexif
from pprint import pprint

def get_exif_dict(path):
    try:
        img = Image.open(path)
        exif_data = img.info.get('exif')
        if not exif_data:
            return {}
        exif_dict = piexif.load(exif_data)
        # Flatten all exif dicts into one for easier comparison
        flat = {}
        for ifd in exif_dict:
            if isinstance(exif_dict[ifd], dict):
                for tag, value in exif_dict[ifd].items():
                    tag_name = piexif.TAGS[ifd][tag]["name"] if tag in piexif.TAGS[ifd] else str(tag)
                    flat[f"{ifd}:{tag_name}"] = value
        return flat
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return {}

def compare_exif(exif1, exif2, ignore_keys=None):
    ignore_keys = set(ignore_keys or [])
    all_keys = set(exif1.keys()) | set(exif2.keys())
    for key in sorted(all_keys):
        if any(ig in key for ig in ignore_keys):
            continue
        v1 = exif1.get(key)
        v2 = exif2.get(key)
        if v1 != v2:
            print(f"DIFF: {key}\n  images: {v1}\n  images_resized: {v2}\n")

def main():
    orig = r"d:/bimba3d-re/bimba3d_backend/data/projects/04ebc646-61e5-4877-9635-d3ba1f325d3c/images/DJI_20260214192633_0455_T.jpeg"
    resized = r"d:/bimba3d-re/bimba3d_backend/data/projects/04ebc646-61e5-4877-9635-d3ba1f325d3c/images_resized/DJI_20260214192633_0455_T.jpeg"
    exif1 = get_exif_dict(orig)
    exif2 = get_exif_dict(resized)
    print("--- EXIF keys in original ---")
    pprint(sorted(exif1.keys()))
    print("--- EXIF keys in resized ---")
    pprint(sorted(exif2.keys()))
    print("\n--- Differences (ignoring size tags) ---")
    compare_exif(exif1, exif2, ignore_keys=["PixelXDimension", "PixelYDimension", "ImageWidth", "ImageLength"])

if __name__ == "__main__":
    main()
