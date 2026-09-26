from math import radians, sin, cos, sqrt, atan2

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat, dlon = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))

def sample_route(coordinates, interval_km):
    """coordinates: [lon, lat] pairs from searoute's geometry."""
    points = [{"lat": coordinates[0][1], "lon": coordinates[0][0], "cumulative_km": 0.0}]
    cumulative = 0.0
    last_sampled = 0.0
    for i in range(1, len(coordinates)):
        lon1, lat1 = coordinates[i - 1]
        lon2, lat2 = coordinates[i]
        cumulative += haversine_km(lat1, lon1, lat2, lon2)
        if cumulative - last_sampled >= interval_km:
            points.append({"lat": lat2, "lon": lon2, "cumulative_km": round(cumulative, 1)})
            last_sampled = cumulative
    return points