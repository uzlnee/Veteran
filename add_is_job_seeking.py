import os
import json

RECORDINGS_DIR = "/home/yujin/Veteran/recordings"

for folder in os.listdir(RECORDINGS_DIR):
    folder_path = os.path.join(RECORDINGS_DIR, folder)
    meta_path = os.path.join(folder_path, "metadata.json")
    if not os.path.isdir(folder_path) or not os.path.exists(meta_path):
        continue
    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # is_job_seeking을 false로 추가(또는 덮어쓰기)
        data["is_job_seeking"] = False
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Updated: {meta_path}")
    except Exception as e:
        print(f"Error updating {meta_path}: {e}")

