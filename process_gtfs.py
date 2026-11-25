import requests
import zipfile
import io
import json

print("Downloading GTFS...")
url = "https://gtfs.mot.gov.il/gtfsfiles/israel-public-transportation.zip"
response = requests.get(url, timeout=180)
response.raise_for_status()

print("Extracting files...")
with zipfile.ZipFile(io.BytesIO(response.content)) as z:
    stops_content = z.read("stops.txt").decode("utf-8")
    routes_content = z.read("routes.txt").decode("utf-8")

print("Processing stops...")
stops = []
for line in stops_content.splitlines()[1:]:
    parts = line.split(",")
    if len(parts) >= 6:
        try:
            lat = float(parts[4])
            lon = float(parts[5])
            if 29 < lat < 34 and 34 < lon < 36:
                stops.append({
                    "id": parts[0],
                    "name": parts[2].strip('"'),
                    "lat": lat,
                    "lon": lon,
                    "code": parts[1] if len(parts) > 1 else None
                })
        except:
            pass

print("Processing routes...")
routes = []
for line in routes_content.splitlines()[1:]:
    parts = line.split(",")
    if len(parts) >= 4:
        try:
            routes.append({
                "id": parts[0],
                "short_name": parts[2].strip('"') if len(parts) > 2 else "",
                "long_name": parts[3].strip('"') if len(parts) > 3 else "",
                "agency": parts[1] if len(parts) > 1 else ""
            })
        except:
            pass

with open("stops.json", "w", encoding="utf-8") as f:
    json.dump(stops, f, ensure_ascii=False)

with open("routes.json", "w", encoding="utf-8") as f:
    json.dump(routes, f, ensure_ascii=False)

print(f"Done: {len(stops)} stops, {len(routes)} routes")
