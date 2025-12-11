# Stargazing Conditions Integration

A custom Home Assistant integration that monitors stargazing conditions and notifies you when the stars will be amazing. Perfect for observers with high standards and access to excellent dark skies.

## Quick Start

### 1. Installation (60 seconds)

```bash
# Copy integration to HA config
cp -r custom_components/stargazing /path/to/your/Home Assistant/config/custom_components/
```

### 2. Configuration

Add to `configuration.yaml`:

```yaml
stargazing:
  notify_service: notify.mandalore
```

### 3. Restart

Restart Home Assistant in Settings → System → Restart

### 4. Test

Go to Developer Tools → Services → Stargazing: Send Test Notification

## What It Does

### Quality Scoring

Analyzes 5 factors to produce a 0-100 quality score:

| Factor | Weight | Your Standard |
|--------|--------|---|
| **Cloudless** | Mandatory | ≥95% |
| **Transparency** | 25 pts | ≥70% |
| **Seeing** | 20 pts | ≥65% |
| **Wind Calm** | 15 pts | ≥60% |
| **Cloud Bonus** | 30 pts | 95-100% |
| **Moon Penalty** | -10 pts | Varies |

### Ratings

- **EXCEPTIONAL** (90-100): Perfect conditions → Immediate notification
- **AMAZING** (80-89): Great night → Evening notification
- **Good** (60-79): Worth observing → Log only
- **Poor** (<60): Not recommended → Skip notification

### Current Real Data

With your settings, the test shows:

```
Cloudless:    100% ✓ OK
Transparency:  55% ⚠ Poor (below 70% threshold)
Seeing:        62% ⚠ Turbulent (below 65% threshold)
Wind Calm:     68% ✓ OK
Moon Phase:    50% (last quarter)

Score: 50/100 → Rating: Poor
```

Note: Today's conditions are below your high standards due to transparency and seeing. This is normal - great nights happen when all factors align.

## Entities Created

After installation, you'll have:

```
sensor.stargazing_quality_score          # 0-100%
sensor.stargazing_rating                  # EXCEPTIONAL/AMAZING/Good/Poor
sensor.stargazing_optimal_viewing_start   # Start time (e.g., 5:13 PM)
sensor.stargazing_optimal_viewing_end     # End time (e.g., 12:00 AM)
sensor.stargazing_next_exceptional_night # Date of next 90+ score
sensor.stargazing_upcoming_astronomy_events # List of events
```

## Services

### Send Test Notification

```yaml
service: stargazing.send_test_notification
```

Verifies Pushover integration is working.

**Try it:**
- Developer Tools → Services → Select "Stargazing: Send Test Notification" → Call Service
- Should receive notification on phone in seconds

### Check Conditions Now

```yaml
service: stargazing.check_conditions_now
```

Immediately check conditions and notify if score ≥80.

### Refresh Astronomy Events

```yaml
service: stargazing.refresh_astronomy_events
```

Fetch latest meteor showers, ISS passes, planetary events.

## Dashboard Integration

Add this card to your Lovelace dashboard:

```yaml
type: vertical-stack
title: 🌟 Stargazing Conditions
cards:
  - type: entities
    entities:
      - sensor.stargazing_quality_score
      - sensor.stargazing_rating
      - sensor.astroweather_backyard_cloudless
      - sensor.astroweather_backyard_transparency
      - sensor.astroweather_backyard_seeing_percentage

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
      - type: button
        name: Refresh
        tap_action:
          action: call-service
          service: stargazing.refresh_astronomy_events
```

## Configuration Reference

```yaml
stargazing:
  # Pushover service (required)
  notify_service: notify.mandalore

  # Minimum score to send notification (default: 80)
  minimum_score_notify: 80

  # High standards thresholds (all optional)
  minimum_cloudless: 95      # Require 95% clear
  minimum_transparency: 70   # Require 70% transparent
  minimum_seeing: 65         # Require 65% steady seeing

  # Your location (for event info)
  zip_code: "88431"
```

### Adjusting Standards

If you're getting too few notifications:

```yaml
# More lenient (for typical dark skies)
minimum_cloudless: 90
minimum_transparency: 60
minimum_seeing: 55
```

If notifications are too frequent:

```yaml
# Stricter (for perfectionism)
minimum_cloudless: 98
minimum_transparency: 80
minimum_seeing: 75
minimum_score_notify: 85
```

## Automation Examples

### Daily evening check

```yaml
automation:
  - alias: "Stargazing - Daily check"
    trigger:
      platform: time
      at: "18:00:00"
    action:
      service: stargazing.check_conditions_now
```

### Notify on exceptional conditions

```yaml
automation:
  - alias: "Stargazing - Exceptional alert"
    trigger:
      platform: numeric_state
      entity_id: sensor.stargazing_quality_score
      above: 90
    action:
      service: notify.mandalore
      data:
        title: "⭐ EXCEPTIONAL STARGAZING"
        message: "Perfect conditions - get outside!"
        priority: 1
```

### Track best nights

```yaml
automation:
  - alias: "Stargazing - Log amazing night"
    trigger:
      platform: numeric_state
      entity_id: sensor.stargazing_quality_score
      above: 80
    action:
      service: logbook.log
      data:
        name: Stargazing
        message: "Score {{ states('sensor.stargazing_quality_score') }}/100"
        entity_id: sensor.stargazing_quality_score
```

## Troubleshooting

### No sensors appearing?

1. Check logs: Settings → System → Logs → Search "stargazing"
2. Verify YAML syntax: `home-assistant --script check_config`
3. Restart Home Assistant

### Test notification doesn't work?

1. Verify service exists: Developer Tools → States → Search "notify"
2. Test Pushover directly:
   ```yaml
   service: notify.mandalore
   data:
     title: "Test"
     message: "Testing"
   ```
3. Check Pushover app is set up in Home Assistant

### Score seems wrong?

1. Check individual sensors:
   - Developer Tools → States
   - Search "astroweather" or "cloudless", "transparency", etc

2. Verify AstroWeather integration:
   - State: `weather.astroweather_backyard`
   - Should show "Excellent" or similar

3. Review breakdown in sensor attributes:
   - Click sensor → View Attributes
   - See detailed scoring

## Data Sources

This integration requires:

- **weather.astroweather_backyard** - Cloud cover, transparency, seeing, moon info
- **sun.sun** - Sunset/sunrise times
- **Internet connection** - For astronomy events API

All data is read-only (no modifications to HA).

## Testing

A test script is included:

```bash
cd src
python3 test_stargazing_integration.py
```

Shows current score, breakdown, viewing window, and events.

## Performance

- **Condition Checks**: Every 60 seconds
- **Event Updates**: Every 60 minutes
- **Notification Frequency**: Max 1 per hour per rating level (prevents spam)
- **CPU Impact**: Negligible (<1%)

## Notes

### For Dark Sky Enthusiasts

Your standards (95% cloudless, 70% transparency, 65% seeing) are appropriate for:
- Deep sky observation (galaxies, nebulae, star clusters)
- Planetary detail work
- Astrophotography
- Visual limiting magnitude >6

Great nights (score ≥80) will be rare but valuable.

### Moon Phase Effects

- New moon phase: Best for deep sky
- Full moon phase: Challenges for faint objects
- Moon below horizon: Always ideal

### Best Stargazing Windows

- **Evening**: Dusk (astronomical twilight) to midnight
- **Morning**: 2 AM to dawn
- **Best**: 2-4 AM (darkest, most stable air typically)

Integration assumes sunset-to-midnight window; you can adjust in automations.

## Astronomy Events

Automatically notified about:
- **Meteor Showers**: Geminids (Dec), Quadrantids (Jan), etc.
- **Planets**: Opposition, conjunction, favorable positions
- **ISS Passes**: Bright satellite passes from your location
- **Comets/Events**: Major sky events when available

## Future Enhancements

Planned:
- Historical tracking ("Best nights are...")
- 7-day forecast score
- Integration with observation logs
- ML predictions based on patterns
- Mobile app push notifications

## Support

For issues:
1. Check Home Assistant logs
2. Verify AstroWeather data is available
3. Test individual components (test button)
4. Review configuration in YAML

## Credits

Built as part of HALink project using:
- Home Assistant
- AstroWeather integration (for sky conditions)
- ISS-Above API (for satellite passes)
- Pushover (for notifications)

---

**Current Test Results:**
```
✓ Integration tested with real Home Assistant data
✓ Scoring engine working correctly
✓ Current score: 50/100 (transparency and seeing below standards)
✓ Optimal viewing window: 5:13 PM - 12:00 AM
✓ Astronomy events: Geminid shower Dec 13
✓ Ready for installation
```

**Version**: 1.0.0
**Last Tested**: Dec 11, 2025
**HA Requirements**: ≥2023.12.0
