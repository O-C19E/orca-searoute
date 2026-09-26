import pytest
from unittest.mock import AsyncMock, patch
from services.hazard_detection import check_point_hazards

@pytest.mark.asyncio
async def test_detects_high_wave_hazard():
    mock_marine_response = AsyncMock()
    mock_marine_response.json = lambda: {"current": {"wave_height": 5.0}}
    mock_weather_response = AsyncMock()
    mock_weather_response.json = lambda: {"current": {"wind_speed_10m": 10, "visibility": 10000}}

    with patch("httpx.AsyncClient.get", side_effect=[mock_marine_response, mock_weather_response]):
        hazards = await check_point_hazards(10.0, 75.0, cumulative_km=5.0)

    assert len(hazards) == 1
    assert hazards[0]["type"] == "high_waves"
    assert hazards[0]["severity"] == "unsafe"

@pytest.mark.asyncio
async def test_no_hazard_when_conditions_calm():
    mock_marine = AsyncMock(); mock_marine.json = lambda: {"current": {"wave_height": 0.8}}
    mock_weather = AsyncMock(); mock_weather.json = lambda: {"current": {"wind_speed_10m": 15, "visibility": 10000}}

    with patch("httpx.AsyncClient.get", side_effect=[mock_marine, mock_weather]):
        hazards = await check_point_hazards(10.0, 75.0, cumulative_km=5.0)

    assert hazards == []

@pytest.mark.asyncio
async def test_dangerous_tier_above_six_metres():
    mock_marine = AsyncMock(); mock_marine.json = lambda: {"current": {"wave_height": 6.5}}
    mock_weather = AsyncMock(); mock_weather.json = lambda: {"current": {"wind_speed_10m": 10, "visibility": 10000}}

    with patch("httpx.AsyncClient.get", side_effect=[mock_marine, mock_weather]):
        hazards = await check_point_hazards(10.0, 75.0, cumulative_km=5.0)

    assert hazards[0]["severity"] == "dangerous"