from shapely.geometry import LineString, Point

# Rough km-to-degrees conversion — accurate enough near India's latitudes (equator to ~25°N),
# NOT valid near the poles. Documented simplification, not a silent approximation.
KM_PER_DEGREE = 111.0

def leg_clears_hazards(coordinates, hazards, clearance_km):
    """coordinates: [lon, lat] pairs. hazards: list of {'lat','lon',...} dicts."""
    if not hazards:
        return True
    line = LineString(coordinates)
    clearance_deg = clearance_km / KM_PER_DEGREE
    for h in hazards:
        hazard_area = Point(h["lon"], h["lat"]).buffer(clearance_deg)
        if line.intersects(hazard_area):
            return False
    return True