import asyncio
import math

import config
from services.baseline_route import calculate_route
from services.segmentation import sample_route, haversine_km
from services.hazard_detection import check_point_hazards
from services.detour import compute_detour_candidates
from services.geometry import leg_clears_hazards

async def compute_safe_route(origin_lat, origin_lon, dest_lat, dest_lon, max_reroutes=None):
    max_reroutes = max_reroutes if max_reroutes is not None else config.MAX_REROUTES_DEFAULT

    route = calculate_route(origin_lat, origin_lon, dest_lat, dest_lon)
    coords = route["coordinates"]
    reroutes_attempted = 0
    all_hazards = []
    status = "safe"

    # Hazards at the origin or destination are surfaced as explicit warnings,
    # not treated as a reason to refuse routing. A vessel already at a
    # hazardous position still needs a route away from it, not a refusal.
    origin_hazard_warning = None
    destination_hazard_warning = None

    while reroutes_attempted < max_reroutes:
        sample_points = sample_route(coords, config.SEGMENT_INTERVAL_KM)
        results = await asyncio.gather(
            *[check_point_hazards(p["lat"], p["lon"], p["cumulative_km"]) for p in sample_points]
        )
        hazards = [h for group in results for h in group]

        if not hazards:
            status = "safe" if reroutes_attempted == 0 else "rerouted"
            break

        all_hazards.extend(hazards)

        if origin_hazard_warning is None:
            origin_hazards_now = [
                h for h in hazards
                if haversine_km(origin_lat, origin_lon, h["lat"], h["lon"]) < config.DETOUR_BUFFER_DISTANCES_KM[0]
            ]
            if origin_hazards_now:
                origin_hazard_warning = {
                    "message": "Hazardous conditions detected at the current/starting position. This route heads away from your current location as quickly as possible.",
                    "hazards": origin_hazards_now,
                }

        if destination_hazard_warning is None:
            dest_hazards_now = [
                h for h in hazards
                if haversine_km(dest_lat, dest_lon, h["lat"], h["lon"]) < config.DETOUR_BUFFER_DISTANCES_KM[0]
            ]
            if dest_hazards_now:
                destination_hazard_warning = {
                    "message": "Hazardous conditions detected at the destination. Conditions may change before arrival — verify before proceeding.",
                    "hazards": dest_hazards_now,
                }

        worst = hazards[0]

        idx = min(range(len(coords) - 1), key=lambda i: haversine_km(coords[i][1], coords[i][0], worst["lat"], worst["lon"]))
        lon1, lat1 = coords[idx]
        lon2, lat2 = coords[idx + 1]
        bearing = math.degrees(math.atan2(lon2 - lon1, lat2 - lat1))

        candidates = compute_detour_candidates(worst["lat"], worst["lon"], bearing, config.DETOUR_BUFFER_DISTANCES_KM)

        valid_option = None
        for detour_lat, detour_lon in candidates:
            leg1 = calculate_route(origin_lat, origin_lon, detour_lat, detour_lon)
            leg2 = calculate_route(detour_lat, detour_lon, dest_lat, dest_lon)

            clearance_km = config.DETOUR_BUFFER_DISTANCES_KM[0]
            if leg_clears_hazards(leg1["coordinates"], [worst], clearance_km) and \
               leg_clears_hazards(leg2["coordinates"], [worst], clearance_km):
                total_km = leg1["distance_km"] + leg2["distance_km"]
                if valid_option is None or total_km < valid_option["total_km"]:
                    valid_option = {"coords": leg1["coordinates"] + leg2["coordinates"][1:], "total_km": total_km}
                break

        if valid_option is None:
            status = "hazards_remaining"
            break

        coords = valid_option["coords"]
        reroutes_attempted += 1
        status = "rerouted"
    else:
        status = "hazards_remaining"

    return {
        "success": True,
        "status": status,
        "route": {"coordinates": coords},
        "hazards": all_hazards,
        "origin_hazard_warning": origin_hazard_warning,
        "destination_hazard_warning": destination_hazard_warning,
        "reroute_summary": {
            "reroutes_attempted": reroutes_attempted,
            "hazards_detected": len(all_hazards),
        },
    }
