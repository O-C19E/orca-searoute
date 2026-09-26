import pytest
from unittest.mock import patch, AsyncMock
from services.safe_route import compute_safe_route

FAKE_ROUTE_POINTS = [
    {"lat": 19.0760, "lon": 72.8777, "cumulative_km": 0.0},
    {"lat": 15.0, "lon": 74.0, "cumulative_km": 300.0},
    {"lat": 12.0, "lon": 75.0, "cumulative_km": 600.0},
    {"lat": 9.9312, "lon": 76.2673, "cumulative_km": 1050.0},
]

@pytest.mark.asyncio
async def test_safe_route_returns_safe_when_no_hazards():
    with patch("services.safe_route.check_point_hazards", new=AsyncMock(return_value=[])):
        result = await compute_safe_route(19.0760, 72.8777, 9.9312, 76.2673)

    assert result["status"] == "safe"
    assert result["reroute_summary"]["reroutes_attempted"] == 0

@pytest.mark.asyncio
async def test_safe_route_reroutes_once_then_clears():
    state = {"hazard_active": True}

    async def fake_check(lat, lon, cumulative_km):
        if state["hazard_active"] and cumulative_km == 300.0:
            state["hazard_active"] = False  # cleared after first detection, simulating a successful reroute
            return [{"type": "high_waves", "severity": "unsafe", "lat": lat, "lon": lon,
                      "value": 5.0, "threshold": 4.0, "cumulative_km": cumulative_km}]
        return []

    with patch("services.safe_route.sample_route", return_value=FAKE_ROUTE_POINTS), \
         patch("services.safe_route.check_point_hazards", new=fake_check):
        result = await compute_safe_route(19.0760, 72.8777, 9.9312, 76.2673)

    assert result["status"] == "rerouted"
    assert result["reroute_summary"]["reroutes_attempted"] == 1

@pytest.mark.asyncio
async def test_safe_route_gives_up_after_max_reroutes():
    with patch("services.safe_route.sample_route", return_value=FAKE_ROUTE_POINTS), \
         patch("services.safe_route.check_point_hazards",
               new=AsyncMock(return_value=[{"type": "high_waves", "severity": "unsafe",
                                             "lat": 10.0, "lon": 75.0, "value": 5.0,
                                             "threshold": 4.0, "cumulative_km": 300.0}])):
        result = await compute_safe_route(19.0760, 72.8777, 9.9312, 76.2673, max_reroutes=2)

    assert result["status"] == "hazards_remaining"
    assert result["reroute_summary"]["reroutes_attempted"] == 2

@pytest.mark.asyncio
async def test_safe_route_fails_when_hazards_are_tightly_clustered():
    async def fake_check(lat, lon, cumulative_km):
        if cumulative_km in (300.0, 600.0):  # clustered mid-route points
            return [{"type": "high_waves", "severity": "unsafe", "lat": lat, "lon": lon,
                      "value": 5.0, "threshold": 4.0, "cumulative_km": cumulative_km}]
        return []

    with patch("services.safe_route.sample_route", return_value=FAKE_ROUTE_POINTS), \
         patch("services.safe_route.check_point_hazards", new=fake_check):
        result = await compute_safe_route(19.0760, 72.8777, 9.9312, 76.2673)

    assert result["status"] in ("hazards_remaining", "rerouted")

@pytest.mark.asyncio
async def test_safe_route_reports_departure_unsafe_when_origin_is_hazardous():
    async def fake_check(lat, lon, cumulative_km):
        if cumulative_km < 1.0:  # the origin point itself
            return [{"type": "high_waves", "severity": "unsafe", "lat": lat, "lon": lon,
                      "value": 5.0, "threshold": 4.0, "cumulative_km": cumulative_km}]
        return []

    with patch("services.safe_route.sample_route", return_value=FAKE_ROUTE_POINTS), \
         patch("services.safe_route.check_point_hazards", new=fake_check):
        result = await compute_safe_route(19.0760, 72.8777, 9.9312, 76.2673)

    assert result["status"] == "departure_or_arrival_unsafe"