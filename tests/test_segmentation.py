from services.segmentation import haversine_km, sample_route

def test_haversine_known_distance():
    # Mumbai to Kochi, roughly 1050km by great-circle — sanity check, not exact
    d = haversine_km(19.0760, 72.8777, 9.9312, 76.2673)
    assert 1000 < d < 1100

def test_haversine_same_point_is_zero():
    assert haversine_km(10.0, 75.0, 10.0, 75.0) == 0.0

def test_sample_route_includes_start_point():
    coords = [[75.0, 10.0], [75.1, 10.1], [75.2, 10.2]]
    points = sample_route(coords, interval_km=1)
    assert points[0]["lat"] == 10.0
    assert points[0]["lon"] == 75.0
    assert points[0]["cumulative_km"] == 0.0

def test_sample_route_respects_interval():
    # a long straight line, sampled coarsely should produce far fewer points than input coords
    coords = [[75.0 + i * 0.01, 10.0] for i in range(200)]
    points = sample_route(coords, interval_km=10)
    assert len(points) < len(coords)