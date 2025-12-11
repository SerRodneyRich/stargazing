# Installation & Setup Guide

## Prerequisites

- Home Assistant ≥2023.12.0
- AstroWeather integration installed and working
- Pushover service configured (`notify.mandalore`)

## Installation

### Step 1: Download Integration

Clone or download this repository:

```bash
git clone https://github.com/yourusername/stargazing.git
```

### Step 2: Copy to Home Assistant

```bash
cp -r stargazing /path/to/your/HA/config/custom_components/
```

**Example paths:**
- Docker: `/path/to/volumes/ha_config/_data/custom_components/`
- HAOS: Use File Manager add-on
- Supervised: `/usr/share/hassio/homeassistant/config/custom_components/`
- Core: `~/.homeassistant/custom_components/`

### Step 3: Configure

Add to `configuration.yaml`:

```yaml
stargazing:
  notify_service: notify.mandalore
```

### Step 4: Restart

Home Assistant → Settings → System → Restart

### Step 5: Verify

Developer Tools → States → Search "stargazing"

You should see:
- `sensor.stargazing_quality_score`
- `sensor.stargazing_rating`

## Configuration Options

```yaml
stargazing:
  # Pushover notification service (required)
  notify_service: notify.mandalore

  # Minimum score to notify (0-100)
  minimum_score_notify: 80

  # High standards thresholds
  minimum_cloudless: 95        # Mandatory cloudless %
  minimum_transparency: 70     # Transparency %
  minimum_seeing: 65           # Seeing %

  # Location for astronomy events
  zip_code: "88431"
```

## Testing

### Test Notification

1. Developer Tools → Services
2. Domain: `stargazing`
3. Service: `send_test_notification`
4. Call Service
5. Check Pushover app - should receive notification

### Check Current Score

Developer Tools → States → `sensor.stargazing_quality_score`

Shows 0-100 quality score based on current AstroWeather data.

### Manual Check

Developer Tools → Services → `stargazing.check_conditions_now`

Checks conditions and notifies if score ≥80.

## Troubleshooting

### Sensors not appearing?

1. Verify files in `/config/custom_components/stargazing/`
2. Check HA logs: Settings → System → Logs
3. Verify YAML syntax in configuration.yaml
4. Restart Home Assistant again

### Test notification fails?

1. Verify `notify.mandalore` exists: Developer Tools → States
2. Test Pushover directly:
   ```yaml
   service: notify.mandalore
   data:
     title: "Test"
     message: "Testing"
   ```
3. Check Pushover app permissions

### Score seems wrong?

1. Check AstroWeather is providing data
2. Verify individual sensor values
3. Review Developer Tools → States for astroweather entities
4. See CONFIG_EXAMPLES.md for threshold adjustments

## Dashboard Integration

Add to your Lovelace dashboard:

```yaml
type: entities
title: 🌟 Stargazing Conditions
entities:
  - sensor.stargazing_quality_score
  - sensor.stargazing_rating
  - sensor.astroweather_backyard_cloudless
  - sensor.astroweather_backyard_transparency

- type: horizontal-stack
  cards:
    - type: button
      name: Test
      tap_action:
        action: call-service
        service: stargazing.send_test_notification
    - type: button
      name: Check Now
      tap_action:
        action: call-service
        service: stargazing.check_conditions_now
```

## Next Steps

1. Add dashboard card for real-time monitoring
2. Create automations for daily checks
3. Adjust thresholds based on your experience
4. Track amazing nights in your observation log

## Support

See TROUBLESHOOTING.md for detailed help.
