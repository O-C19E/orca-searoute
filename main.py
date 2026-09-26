from fastapi import FastAPI, Query
from models import RouteRequest, SafeRouteRequest
from services.baseline_route import calculate_route
from services.safe_route import compute_safe_route

app = FastAPI(title="ORCA Sea Route Service")


@app.get("/")
def health():
    return {"status": "ok", "service": "ORCA Sea Route"}


@app.post("/sea-route")
def sea_route_post(req: RouteRequest):
    return calculate_route(req.origin_lat, req.origin_lon, req.dest_lat, req.dest_lon)


@app.get("/sea-route")
def sea_route_get(
    origin_lat: float = Query(...),
    origin_lon: float = Query(...),
    dest_lat: float = Query(...),
    dest_lon: float = Query(...),
):
    return calculate_route(origin_lat, origin_lon, dest_lat, dest_lon)


@app.post("/safe-route")
async def safe_route(req: SafeRouteRequest):
    return await compute_safe_route(
        req.origin_lat, req.origin_lon, req.dest_lat, req.dest_lon, req.max_reroutes
    )
