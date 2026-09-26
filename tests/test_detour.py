from services.detour import compute_detour_candidates
from services.segmentation import haversine_km

def test_returns_two_candidates_per_distance():
    candidates = compute_detour_candidates(10.0, 75.0, bearing_deg=0, buffer_distances_km=[15, 30, 50])
    assert len(candidates) == 6

def test_candidates_are_on_opposite_sides():
    candidates = compute_detour_candidates(10.0, 75.0, bearing_deg=0, buffer_distances_km=[15])
    lat1, lon1 = candidates[0]
    lat2, lon2 = candidates[1]
    assert (lon1 - 75.0) * (lon2 - 75.0) < 0

def test_each_candidate_matches_its_requested_distance():
    candidates = compute_detour_candidates(10.0, 75.0, bearing_deg=0, buffer_distances_km=[15, 30, 50])
    expected_order = [15, 15, 30, 30, 50, 50]
    for (lat, lon), expected_km in zip(candidates, expected_order):
        d = haversine_km(10.0, 75.0, lat, lon)
        assert abs(d - expected_km) < 0.5

def test_candidates_shift_with_different_bearing():
    candidates_north = compute_detour_candidates(10.0, 75.0, bearing_deg=0, buffer_distances_km=[15])
    candidates_east = compute_detour_candidates(10.0, 75.0, bearing_deg=90, buffer_distances_km=[15])
    assert candidates_north != candidates_east

def test_single_distance_still_returns_two_candidates():
    candidates = compute_detour_candidates(10.0, 75.0, bearing_deg=0, buffer_distances_km=[15])
    assert len(candidates) == 2