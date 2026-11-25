import requests
import zipfile
import io
import json

print("Downloading GTFS...")
url = "https://gtfs.mot.gov.il/gtfsfiles/israel-public-transportation.zip"
response = requests.get(url, timeout=120)
response.raise_for_status()

print("Extracting stops.txt...")
with zipfile.ZipFile(io.BytesIO(response.content)) as z:
    with z.open("stops.txt") as f:
        lines = f.read().decode("utf-8").splitlines()

stops = []
for line in lines[1:101]:
    parts = line.split(",")
    if len(parts) >= 6:
        try:
            stops.append({
                "id": parts[0],
                "name": parts[2].strip('"'),
                "lat": float(parts[4]),
                "lon": float(parts[5]),
                "code": parts[1] if len(parts) > 1 else None
            })
        except:
            pass

with open("stops_sample.json", "w", encoding="utf-8") as f:
    json.dump(stops, f, ensure_ascii=False, indent=2)

print(f"Processed {len(stops)} stops")
