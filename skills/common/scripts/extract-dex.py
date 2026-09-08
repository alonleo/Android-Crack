import zipfile
from pathlib import Path

base = Path("/tmp/base.apk")
out = Path("/tmp/dex_files")
out.mkdir(exist_ok=True)

with zipfile.ZipFile(base) as z:
    for n in z.namelist():
        if n.startswith("classes") and n.endswith(".dex"):
            data = z.read(n)
            (out / n).write_bytes(data)
            print(f"提取: {n} ({len(data)//1024} KB)")

print("Done")
