from services.geometry import leg_clears_hazards

def test_leg_clears_when_no_hazards():
    coords = [[75.0, 10.0], [75.5, 10.5]]
    assert leg_clears_hazards(coords, [], clearance_km=15) is True

def test_leg_fails_when_line_passes_through_hazard():
    coords = [[75.0, 10.0], [75.5, 10.5]]
    hazards = [{"lat": 10.25, "lon": 75.25}]  # sits directly on the line between the two points
    assert leg_clears_hazards(coords, hazards, clearance_km=15) is False

def test_leg_clears_when_hazard_is_far_away():
    coords = [[75.0, 10.0], [75.5, 10.5]]
    hazards = [{"lat": 20.0, "lon": 85.0}]  # far outside any reasonable clearance
    assert leg_clears_hazards(coords, hazards, clearance_km=15) is True

def test_leg_fails_when_hazard_is_near_but_not_on_the_line():
    # hazard sits just off the direct path, within clearance radius, should still be caught
    coords = [[75.0, 10.0], [75.5, 10.5]]
    hazards = [{"lat": 10.3, "lon": 75.2}]  # near but offset from the line
    assert leg_clears_hazards(coords, hazards, clearance_km=15) is False

def test_leg_clears_when_hazard_just_outside_clearance():
    coords = [[75.0, 10.0], [75.5, 10.5]]
    hazards = [{"lat": 20.0, "lon": 75.25}]  # roughly 1080km away, well beyond any small clearance
    assert leg_clears_hazards(coords, hazards, clearance_km=15) is True

def test_multiple_hazards_any_intersection_fails():
    coords = [[75.0, 10.0], [75.5, 10.5]]
    hazards = [
        {"lat": 20.0, "lon": 85.0},   # far, clear
        {"lat": 10.25, "lon": 75.25},  # on the line, should trigger failure
    ]
    assert leg_clears_hazards(coords, hazards, clearance_km=15) is False