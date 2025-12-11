# Troubleshooting Guide

## Installation Issues

### Sensors Not Appearing

**Symptoms**: Restarted HA but sensors don't show in Developer Tools → States

**Solutions**:

1. **Check files copied correctly**
   ```bash
   ls -la /config/custom_components/stargazing/
   # Should show 12 files including __init__.py
   ```

2. **Check Home Assistant logs**
   - Settings → System → Logs
   - Search for "stargazing"
   - Look for error messages

3. **Verify YAML syntax**
   ```bash
   home-assistant --script check_config
   ```
   Should show no errors

4. **Try restart again**
   - Sometimes takes 2-3 restarts
   - Clear browser cache (Ctrl+Shift+Delete)
   - Try different browser

5. **Check Home Assistant version**
   - Settings → About
   - Requires ≥2023.12.0

### Configuration Not Loading

**Symptoms**: No sensors despite correct YAML

**Causes & Fixes**:

1. **YAML syntax error**
   ```yaml
   # ✓ Correct
   stargazing:
     notify_service: notify.mandalore

   # ✗ Wrong
   stargazing
     notify_service: notify.mandalore
   ```

2. **Indentation error**
   - Use spaces (not tabs)
   - 2-space indentation

3. **Typo in service name**
   - Should be: `notify.mandalore`
   - Check exact spelling

## Notification Issues

### Test Notification Not Working

**Symptoms**: Service call completes but no Pushover notification

**Troubleshooting**:

1. **Verify Pushover service exists**
   ```
   Developer Tools → States
   Search: "mandalore"
   Should show: notify.mandalore
   ```

2. **Test Pushover directly**
   ```yaml
   service: notify.mandalore
   data:
     title: "Test"
     message: "Testing Pushover directly"
   ```
   - If this works: Issue is with integration
   - If this fails: Issue is with Pushover setup

3. **Check Pushover app**
   - Is app open on phone?
   - Are notifications enabled?
   - Check notification settings

4. **Check HA logs**
   ```
   Settings → System → Logs
   Search: "notify" or "mandalore"
   ```
   Look for error messages

5. **Verify Bearer Token**
   - Pushover service needs valid HA token
   - Try regenerating token if old

### Not Getting Condition Notifications

**Symptoms**: Sensor works but no notifications when score ≥80

**Causes & Fixes**:

1. **Score below threshold**
   ```
   Developer Tools → States
   sensor.stargazing_quality_score
   ```
   - If < 80: Conditions not good enough (working as designed)
   - Check individual sensor values

2. **Notification throttling**
   - Only notifies once per hour per rating level
   - Wait 60 minutes for next notification

3. **Check thresholds**
   - Maybe your standards are too high
   - Review CONFIG_EXAMPLES.md
   - Lower thresholds if needed

4. **Verify service is running**
   ```
   Developer Tools → Services
   Stargazing: Check Conditions Now
   ```
   - Manually trigger condition check
   - Should notify if score ≥80

## Score/Rating Issues

### Score Always 0

**Symptoms**: Quality score always shows 0 (Poor)

**Causes**:

1. **Cloudless below 95%**
   - Check: `sensor.astroweather_backyard_cloudless`
   - If < 95%: Correctly shows 0
   - Not a bug!

2. **AstroWeather not providing data**
   ```
   Developer Tools → States
   weather.astroweather_backyard
   ```
   - Should show "Excellent" or similar
   - If unavailable: AstroWeather not working

3. **Thresholds too high**
   - Try lowering `minimum_cloudless` to 90
   - See CONFIG_EXAMPLES.md

### Score Seems Wrong

**Symptoms**: Score doesn't match perceived conditions

**Debug steps**:

1. **Check individual metrics**
   ```
   Developer Tools → States (search for):
   - astroweather_backyard_cloudless
   - astroweather_backyard_transparency
   - astroweather_backyard_seeing_percentage
   - astroweather_backyard_calm_percentage
   ```

2. **Compare to AstroWeather**
   - Open AstroWeather card
   - Compare values
   - Should match

3. **Check scoring algorithm**
   - Your standards: cloudless 95%, transparency 70%, seeing 65%
   - If any are below: Score reduced
   - If all above: Good score expected

4. **Verify moon phase**
   - Full moon reduces score
   - Check moon phase value
   - New moon has no penalty

## AstroWeather Issues

### AstroWeather Not Providing Data

**Symptoms**: weather.astroweather_backyard unavailable

**Not an integration issue**, but verify:

1. **AstroWeather installed**
   - Settings → Devices & Services
   - Search "AstroWeather"
   - Should be there

2. **AstroWeather configured**
   - Check coordinates
   - Valid location set
   - Integration enabled

3. **AstroWeather working**
   - Check main weather forecast
   - Should show condition and data

## Dashboard Issues

### Dashboard Card Not Showing

**Symptoms**: Added card to dashboard but it's blank

**Solutions**:

1. **Check entity exists**
   ```
   Developer Tools → States
   sensor.stargazing_quality_score
   Should exist
   ```

2. **Correct entity ID in card**
   ```yaml
   # ✓ Correct
   entity: sensor.stargazing_quality_score

   # ✗ Wrong
   entity: stargazing_quality_score
   ```

3. **Card type compatible**
   - Simple entities card works
   - Custom cards may need separate installation

4. **Syntax error in YAML**
   - Validate YAML syntax
   - Check indentation

## Service Issues

### Services Not Showing

**Symptoms**: stargazing services don't appear in Developer Tools

**Causes**:

1. **Integration not loaded**
   - Check logs for errors
   - Restart HA

2. **Services not registered**
   - Check `services.yaml` file exists
   - Verify syntax

3. **Restart needed**
   - Services register on startup
   - Try restarting again

### Service Call Fails

**Symptoms**: Service call shows error

**Debug**:

1. **Check error message in logs**
2. **Verify entity exists** if service uses entities
3. **Check Pushover connected** for notification services
4. **Try simpler service first** (test_notification)

## Performance Issues

### High CPU Usage

**Symptoms**: Integration causing CPU spike

**Unlikely**, but if occurs:

1. **Check update frequency**
   - Default: 60 seconds
   - May increase if events being fetched
   - Should not cause high CPU

2. **Check Home Assistant logs**
   - May indicate other issues

3. **Restart integration**
   - Restart Home Assistant
   - Clears any stuck loops

### Memory Issues

**Symptoms**: HA memory growing

**Unlikely**, but check:

1. **Event caching**
   - Events cached for 1 hour
   - Should clean up automatically

2. **Sensor history**
   - If keeping long history, may use memory
   - Check HA database settings

## Common Error Messages

### "notify.mandalore not found"

**Cause**: Pushover service not configured

**Fix**: Set up Pushover in Home Assistant first

### "weather.astroweather_backyard unavailable"

**Cause**: AstroWeather integration not working

**Fix**: Check AstroWeather setup

### "YAML error in configuration.yaml"

**Cause**: Syntax error in stargazing config

**Fix**: Check indentation and colons

### "Integration not loading"

**Cause**: Python error in integration code

**Fix**: Check logs for specific error

## Getting Help

**Before reporting issues**:

1. Check this troubleshooting guide
2. Review Home Assistant logs
3. Verify AstroWeather is working
4. Confirm Pushover service exists
5. Test notification manually

**Information to provide**:
- Home Assistant version
- Integration version
- Configuration (no secrets)
- Specific error message
- Home Assistant logs excerpt

## Advanced Debugging

### Enable Debug Logging

Add to `configuration.yaml`:

```yaml
logger:
  logs:
    custom_components.stargazing: debug
```

Restart and check logs.

### Test Directly

Use test script:

```bash
python3 src/test_stargazing_integration.py
```

Shows current state and any errors.

## When Nothing Works

1. **Uninstall completely**
   - Remove from custom_components/
   - Restart HA
   - Check removed from states

2. **Reinstall fresh**
   - Copy files again
   - Fresh configuration
   - Restart

3. **Check prerequisites**
   - HA version ≥2023.12.0
   - AstroWeather working
   - Pushover configured

4. **Check logs one more time**
   - Often error message explains issue

Still stuck? Check integration README for additional resources.
