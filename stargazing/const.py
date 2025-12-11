"""Constants for Stargazing integration."""

DOMAIN = "stargazing"

# Default configuration
DEFAULT_NOTIFY_SERVICE = "notify.mandalore"
DEFAULT_MIN_SCORE = 80
DEFAULT_MIN_CLOUDLESS = 95
DEFAULT_MIN_TRANSPARENCY = 70
DEFAULT_MIN_SEEING = 65

# AstroWeather entity mappings
ASTROWEATHER_WEATHER = "weather.astroweather_backyard"
ASTROWEATHER_CLOUD_COVER = "sensor.astroweather_backyard_cloud_cover"
ASTROWEATHER_CLOUDLESS = "sensor.astroweather_backyard_cloudless"
ASTROWEATHER_SEEING = "sensor.astroweather_backyard_seeing_percentage"
ASTROWEATHER_TRANSPARENCY = "sensor.astroweather_backyard_transparency"
ASTROWEATHER_SEEING_RAW = "sensor.astroweather_backyard_seeing"
ASTROWEATHER_TRANSPARENCY_RAW = "sensor.astroweather_backyard_transparency"

# Sun timing
SUN_ENTITY = "sun.sun"
SUN_NEXT_SETTING = "sensor.sun_next_setting"
SUN_NEXT_DUSK = "sensor.sun_next_dusk"
SUN_NEXT_DAWN = "sensor.sun_next_dawn"

# Binary sensors for moon info
BINARY_DEEP_SKY_VIEW = "binary_sensor.astroweather_backyard_deep_sky_view"
BINARY_MOON_UP_DARKNESS = "binary_sensor.astroweather_backyard_moon_rises_during_darkness"

# Sensor entity names (created by this integration)
SENSOR_SCORE = f"{DOMAIN}_quality_score"
SENSOR_RATING = f"{DOMAIN}_rating"
SENSOR_OPTIMAL_START = f"{DOMAIN}_optimal_viewing_start"
SENSOR_OPTIMAL_END = f"{DOMAIN}_optimal_viewing_end"
SENSOR_NEXT_EXCEPTIONAL = f"{DOMAIN}_next_exceptional_night"
SENSOR_UPCOMING_EVENTS = f"{DOMAIN}_upcoming_astronomy_events"

# Rating thresholds
RATING_EXCEPTIONAL = "EXCEPTIONAL"
RATING_AMAZING = "AMAZING"
RATING_GOOD = "Good"
RATING_POOR = "Poor"

SCORE_EXCEPTIONAL = 90
SCORE_AMAZING = 80
SCORE_GOOD = 60

# Services
SERVICE_TEST_NOTIFY = "send_test_notification"
SERVICE_CHECK_NOW = "check_conditions_now"
SERVICE_REFRESH_EVENTS = "refresh_astronomy_events"

# Configuration keys
CONF_NOTIFY_SERVICE = "notify_service"
CONF_MIN_SCORE = "minimum_score_notify"
CONF_MIN_CLOUDLESS = "minimum_cloudless"
CONF_MIN_TRANSPARENCY = "minimum_transparency"
CONF_MIN_SEEING = "minimum_seeing"
CONF_ZIP_CODE = "zip_code"
CONF_CHECK_TIMES = "check_times"

# External APIs
IN_THE_SKY_API = "https://www.in-the-sky.org/data/events_api.json"
ASTRONOMY_API_BASE = "https://api.astronomyapi.com/api/v2"
NASA_API_BASE = "https://api.nasa.gov"

# Update intervals
UPDATE_INTERVAL_SCORE = 60  # Check conditions every 60 seconds
UPDATE_INTERVAL_EVENTS = 3600  # Check astronomy events hourly
