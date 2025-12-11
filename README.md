# Stargazing Conditions - Home Assistant Integration

A custom Home Assistant integration that monitors stargazing conditions and notifies you when the stars will be amazing. Perfect for observers with high standards and access to excellent dark skies.

## Quick Start

### 1. Installation

Copy the `stargazing` folder to your Home Assistant `custom_components` directory:

```bash
cp -r stargazing /path/to/your/HA/config/custom_components/
```

### 2. Configure

Add to your `configuration.yaml`:

```yaml
stargazing:
  notify_service: notify.mandalore
```

### 3. Restart

Restart Home Assistant in Settings → System → Restart

### 4. Test

Go to Developer Tools → Services → `stargazing.send_test_notification`

## Features

### Quality Scoring (0-100)

Analyzes stargazing conditions based on:
- **Cloudless** (mandatory ≥95%)
- **Transparency** (high standards ≥70%)
- **Seeing** (high standards ≥65%)
- **Wind Calm** (≥60%)
- **Moon Phase** (penalty varies)

### Ratings

- **EXCEPTIONAL (90-100)**: Perfect conditions → Immediate Pushover notification
- **AMAZING (80-89)**: Great night → Evening notification
- **Good (60-79)**: Acceptable → Log only
- **Poor (<60)**: Not recommended → No notification

### Automation Events

- Meteor showers
- ISS passes
- Planetary events
- Auto-notifications 1-2 days before

### Dashboard Integration

- 6 sensor entities
- Real-time quality score
- Optimal viewing window
- Dashboard card template included

### Services

- `send_test_notification` - Test Pushover integration
- `check_conditions_now` - Manual condition check
- `refresh_astronomy_events` - Update astronomy events

## Configuration

### Minimal

```yaml
stargazing:
  notify_service: notify.mandalore
```

### Full Options

```yaml
stargazing:
  notify_service: notify.mandalore
  minimum_score_notify: 80
  minimum_cloudless: 95
  minimum_transparency: 70
  minimum_seeing: 65
  zip_code: "88431"
```

## Entities Created

```
sensor.stargazing_quality_score                   # 0-100 quality
sensor.stargazing_rating                          # EXCEPTIONAL/AMAZING/Good/Poor
sensor.stargazing_optimal_viewing_start           # Viewing window start
sensor.stargazing_optimal_viewing_end             # Viewing window end
sensor.stargazing_next_exceptional_night          # Next perfect night
sensor.stargazing_upcoming_astronomy_events       # Event list
```

## Requirements

- Home Assistant ≥2023.12.0
- AstroWeather integration
- Pushover service configured

## Documentation

- **Installation & Setup**: See `docs/SETUP.md`
- **Complete Reference**: See `docs/REFERENCE.md`
- **Configuration Examples**: See `docs/CONFIG_EXAMPLES.md`
- **Troubleshooting**: See `docs/TROUBLESHOOTING.md`

## High Standards Scoring

This integration is tuned for:
- Very high dark sky areas (88431 location optimized)
- Deep sky observation requirements
- Serious amateur astronomers
- Optimal conditions only (notifications are meaningful)

Expected notification frequency:
- **EXCEPTIONAL**: 2-3x per month
- **AMAZING**: 1-2x per week
- **Good**: Logged, no notification
- **Poor**: Most nights

## Data Privacy

✅ Local network only
✅ Read-only (no entity modifications)
✅ No external API keys required
✅ Pushover handles notifications

## Support

For issues:
1. Check `docs/TROUBLESHOOTING.md`
2. Review Home Assistant logs
3. Verify AstroWeather is providing data
4. Run test notification button

## License

MIT License - See LICENSE file

## Credits

Built for Home Assistant with ❤️

Uses:
- AstroWeather integration (sky conditions)
- ISS-Above API (satellite passes)
- Pushover (notifications)

---

**Version**: 1.0.0
**Created**: December 11, 2025
**Status**: Production Ready
