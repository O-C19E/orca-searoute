from services.baseline_route import calculate_route

def test_calculate_route_returns_expected_shape():
    result = calculate_route(19.0760, 72.8777, 9.9312, 76.2673)  # Mumbai -> Kochi
    assert result["success"] is True
    assert result["distance_km"] > 0
    assert len(result["coordinates"]) >= 2
    assert result["coordinates"][0] is not None