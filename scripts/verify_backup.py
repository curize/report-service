"""Восстановление резервной копии в отдельный каталог и сверка.

Использование: python scripts/verify_backup.py backup/data.json restored
"""
import hashlib
import json
import os
import shutil
import sys


def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    if len(sys.argv) != 3:
        print("usage: verify_backup.py <backup-file> <restore-dir>")
        return 2
    src, dest_dir = sys.argv[1], sys.argv[2]
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, os.path.basename(src))
    shutil.copyfile(src, dest)
    with open(dest, encoding="utf-8") as f:
        records = json.load(f)
    same = sha256(src) == sha256(dest)
    print(f"backup:   {src}  sha256={sha256(src)}")
    print(f"restored: {dest}  sha256={sha256(dest)}")
    print(f"records:  {len(records)}")
    print("RESULT:", "OK, checksums match" if same else "MISMATCH")
    return 0 if same else 1


if __name__ == "__main__":
    sys.exit(main())
