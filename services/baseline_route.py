import searoute as sr
from fastapi import HTTPException

def calculate_route(origin_lat, origin_lon, dest_lat, dest_lon):
    try:
        origin = [origin_lon, origin_lat]
        destination = [dest_lon, dest_lat]

        route = sr.searoute(origin, destination, units="km", append_orig_dest=True)

        length_km = route["properties"]["length"]
        duration = route["properties"].get("duration_hours")

        return {
            "success": True,
            "distance_km": round(length_km, 2),
            "distance_nautical_miles": round(length_km / 1.852, 2),
            "duration_hours": round(duration, 2) if duration else None,
            "coordinates": route["geometry"]["coordinates"],  # [lon, lat] list
            "geojson": route,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))