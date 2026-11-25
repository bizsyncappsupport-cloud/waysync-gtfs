import requests
import zipfile
import io
import json
from collections import defaultdict

print("Downloading GTFS...")
url = "https://gtfs.mot.gov.il/gtfsfiles/israel-public-transportation.zip"
response = requests.get(url, timeout=300)
response.raise_for_status()

print("Extracting...")
with zipfile.ZipFile(io.BytesIO(response.content)) as z:
    stops_content = z.read("stops.txt").decode("utf-8")
    routes_content = z.read("routes.txt").decode("utf-8")
    trips_content = z.read("trips.txt").decode("utf-8")
    stop_times_content = z.read("stop_times.txt").decode("utf-8")

print("Processing stops...")
stops = []
stops_by_id = {}
for line in stops_content.splitlines()[1:]:
    parts = line.split(",")
    if len(parts) >= 6:
        try:
            lat = float(parts[4])
            lon = float(parts[5])
            if 29 < lat < 34 and 34 < lon < 36:
                stop = {
                    "id": parts[0],
                    "name": parts[2].strip('"'),
                    "lat": lat,
                    "lon": lon,
                    "code": parts[1] if len(parts) > 1 else None
                }
                stops.append(stop)
                stops_by_id[parts[0]] = stop
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
                "long_name": parts[3].strip('"') if len(parts) > 3 else ""
            })
        except:
            pass

print("Processing trips...")
trip_to_route = {}
for line in trips_content.splitlines()[1:50000]:
    parts = line.split(",")
    if len(parts) >= 3:
        trip_to_route[parts[2]] = parts[0]

print("Processing stop_times (sample)...")
route_stops = defaultdict(set)
count = 0
for line in stop_times_content.splitlines()[1:]:
    parts = line.split(",")
    if len(parts) >= 4:
        trip_id = parts[0]
        stop_id = parts[3]
        if trip_id in trip_to_route and stop_id in stops_by_id:
            route_id = trip_to_route[trip_id]
            route_stops[route_id].add(stop_id)
    count += 1
    if count > 500000:
        break

route_stops_list = {k: list(v)[:30] for k, v in route_stops.items()}

with open("stops.json", "w", encoding="utf-8") as f:
    json.dump(stops, f, ensure_ascii=False)

with open("routes.json", "w", encoding="utf-8") as f:
    json.dump(routes, f, ensure_ascii=False)

with open("route_stops.json", "w", encoding="utf-8") as f:
    json.dump(route_stops_list, f, ensure_ascii=False)

print(f"Done: {len(stops)} stops, {len(routes)} routes, {len(route_stops_list)} route-stop mappings")
