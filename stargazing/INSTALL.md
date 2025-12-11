# Quick Installation Guide

## 1. Copy the Integration

```bash
# From your HALink directory
cp -r custom_components/stargazing /path/to/your/Home Assistant/config/custom_components/

# Example if HA config is in Docker:
docker cp custom_components/stargazing <container-id>:/config/custom_components/
```

## 2. Add Configuration

Add to your `configuration.yaml`:

```yaml
stargazing:
  notify_service: notify.mandalore
  minimum_score_notify: 80
```

## 3. Restart Home Assistant

- **UI**: Settings → System → Restart
- **CLI**: `homeassistant --runner restart`
- **Docker**: `docker restart <container-id>`

## 4. Verify Installation

- Go to Developer Tools → States
- Search for "stargazing" or "sensor.stargazing"
- You should see:
  - `sensor.stargazing_quality_score`
  - `sensor.stargazing_rating`
  - Other sensors

## 5. Test the Integration

1. Go to Developer Tools → Services
2. Select `stargazing.send_test_notification`
3. Click "Call Service"
4. You should receive a Pushover notification

## 6. Add to Dashboard (Optional)

1. Go to your dashboard and click the pencil (edit)
2. Add new card → Raw Configuration
3. Paste the card YAML from `stargazing-dashboard.yaml`
4. Save

## Troubleshooting

### Sensors not appearing?

1. Check Home Assistant logs:
   ```
   Settings → System → Logs
   ```
   Look for "stargazing" errors

2. Verify configuration.yaml syntax:
   ```bash
   home-assistant --script check_config
   ```

3. Try removing and re-adding to configuration.yaml

### Test notification fails?

1. Verify `notify.mandalore` exists:
   - Developer Tools → States
   - Search for "mandalore"

2. Test Pushover directly:
   ```yaml
   service: notify.mandalore
   data:
     title: "Test"
     message: "Testing"
   ```

3. Check Pushover app is configured correctly in Home Assistant

### Still having issues?

1. Check integration requirements are met:
   - AstroWeather integration working
   - Sun integration (built-in)
   - Pushover service configured

2. Look for Python errors in logs

3. Restart Home Assistant completely

## Next Steps

- Read [STARGAZING_INTEGRATION.md](../../STARGAZING_INTEGRATION.md) for full documentation
- Create automations to check conditions automatically
- Add dashboard cards for visualization
- Configure custom score thresholds if desired

## Support

If problems persist:
1. Check logs for specific error messages
2. Verify all requirements are installed
3. Make sure Home Assistant version ≥ 2023.12.0
