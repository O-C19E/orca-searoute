import math

def compute_detour_candidates(hazard_lat, hazard_lon, bearing_deg, buffer_distances_km):
    """Returns candidate (lat, lon) points on both sides of the route's bearing,
    at each distance in buffer_distances_km, closest distances first."""
    candidates = []
    for buffer_km in buffer_distances_km:
        for side in (90, -90):
            perp_bearing = math.radians((bearing_deg + side) % 360)
            R = 6371.0
            lat1, lon1 = math.radians(hazard_lat), math.radians(hazard_lon)
            lat2 = math.asin(
                math.sin(lat1) * math.cos(buffer_km / R)
                + math.cos(lat1) * math.sin(buffer_km / R) * math.cos(perp_bearing)
            )
            lon2 = lon1 + math.atan2(
                math.sin(perp_bearing) * math.sin(buffer_km / R) * math.cos(lat1),
                math.cos(buffer_km / R) - math.sin(lat1) * math.sin(lat2),
            )
            candidates.append((math.degrees(lat2), math.degrees(lon2)))
    return candidates