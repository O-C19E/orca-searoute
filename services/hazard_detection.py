import httpx
import config
import asyncio

async def check_point_hazards(lat, lon, cumulative_km):
    async with httpx.AsyncClient(timeout=config.HTTP_TIMEOUT_SECONDS) as client:
        marine, weather = await asyncio.gather(
            client.get(f"{config.OPEN_METEO_MARINE_URL}?latitude={lat}&longitude={lon}&current=wave_height&timezone=auto"),
            client.get(f"{config.OPEN_METEO_FORECAST_URL}?latitude={lat}&longitude={lon}&current=wind_speed_10m,visibility&timezone=auto"),
        )

    wave_height = marine.json().get("current", {}).get("wave_height")
    wind_speed = weather.json().get("current", {}).get("wind_speed_10m")
    visibility = weather.json().get("current", {}).get("visibility")

    hazards = []
    if wave_height is not None and wave_height >= config.WAVE_UNSAFE_M:
        hazards.append({
            "type": "high_waves",
            "severity": "unsafe" if wave_height < config.WAVE_DANGEROUS_M else "dangerous",
            "lat": lat, "lon": lon, "value": wave_height,
            "threshold": config.WAVE_UNSAFE_M, "cumulative_km": cumulative_km,
        })
    if wind_speed is not None and wind_speed >= config.WIND_UNSAFE_KMH:
        hazards.append({
            "type": "high_wind", "severity": "unsafe",
            "lat": lat, "lon": lon, "value": wind_speed,
            "threshold": config.WIND_UNSAFE_KMH, "cumulative_km": cumulative_km,
        })
    if visibility is not None and visibility < config.VISIBILITY_UNSAFE_M:
        hazards.append({
            "type": "low_visibility", "severity": "unsafe",
            "lat": lat, "lon": lon, "value": visibility,
            "threshold": config.VISIBILITY_UNSAFE_M, "cumulative_km": cumulative_km,
        })
    return hazards