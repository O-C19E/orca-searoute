from fastapi import FastAPI
from models import RouteRequest, SafeRouteRequest
from services.baseline_route import calculate_route
from services.safe_route import compute_safe_route

app = FastAPI(title="ORCA Sea Route Service")

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import searoute as sr

app = FastAPI(title="ORCA Sea Route Service")

class RouteRequest(BaseModel):
    origin_lat: float
    origin_lon: float
    dest_lat: float
    dest_lon: float

@app.get("/")
def health():
    return {"status": "ok", "service": "ORCA Sea Route"}

@app.post("/sea-route")
def sea_route_post(req: RouteRequest):
    return calculate_route(req.origin_lat, req.origin_lon, req.dest_lat, req.dest_lon)

@app.get("/sea-route")
def sea_route_get(origin_lat: float, origin_lon: float, dest_lat: float, dest_lon: float):
    return calculate_route(origin_lat, origin_lon, dest_lat, dest_lon)

@app.post("/safe-route")
async def safe_route(req: SafeRouteRequest):
    return await compute_safe_route(
        req.origin_lat, req.origin_lon, req.dest_lat, req.dest_lon, req.max_reroutes
    )
    return _calculate_route(
        req.origin_lat, req.origin_lon,
        req.dest_lat, req.dest_lon
    )

@app.get("/sea-route")
def sea_route_get(
    origin_lat: float = Query(...),
    origin_lon: float = Query(...),
    dest_lat: float = Query(...),
    dest_lon: float = Query(...),
):
    return _calculate_route(origin_lat, origin_lon, dest_lat, dest_lon)

def _calculate_route(origin_lat, origin_lon, dest_lat, dest_lon):
    try:
        # searoute needs [lon, lat]
        origin = [origin_lon, origin_lat]
        destination = [dest_lon, dest_lat]

        route = sr.searoute(
            origin,
            destination,
            units="km",
            append_orig_dest=True
        )

        length_km = route["properties"]["length"]
        duration = route["properties"].get("duration_hours")

        return {
            "success": True,
            "distance_km": round(length_km, 2),
            "distance_nautical_miles": round(length_km / 1.852, 2),
            "duration_hours": round(duration, 2) if duration else None,
            "coordinates": route["geometry"]["coordinates"],  # [lon, lat] list
            "geojson": route
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
