# Centralized thresholds — sourced from IMD Fishermen Warning criteria
# (see ORCA_Marine_Safety_Alert_Thresholds.pdf). Review periodically.

WAVE_UNSAFE_M = 4.0
WAVE_DANGEROUS_M = 6.0
WIND_UNSAFE_KMH = 45
VISIBILITY_UNSAFE_M = 1000

SEGMENT_INTERVAL_KM = 5       # hazard-check sampling density along the route
DETOUR_BUFFER_DISTANCES_KM = [15, 30, 50]  # tried in order, closest first
MAX_REROUTES_DEFAULT = 3
KM_PER_DEGREE = 111.0         # documented simplification — valid near India's latitudes, not near poles

OPEN_METEO_MARINE_URL = "https://marine-api.open-meteo.com/v1/marine"
OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
HTTP_TIMEOUT_SECONDS = 10