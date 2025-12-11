# Upgrade Guide: v1.0 → v1.1

## What Changed

Your integration has been completely modernized from a YAML-only integration to a full UI-configurable integration with proper device support.

### Major Improvements

✅ **UI Configuration** - Can now be added via Settings → Devices & Services
✅ **No More Restarts** - Changes apply instantly without HA restart
✅ **Device Grouping** - All 8 entities grouped under one "Stargazing Conditions" device
✅ **Options Flow** - Change settings after installation via "Configure" button
✅ **Individual Event Sensors** - 3 dedicated sensors for upcoming events (no more digging through attributes!)
✅ **"Add to Dashboard" Button** - Standard HA workflow now works
✅ **Backward Compatible** - Existing YAML configs still work

### New Entities (3 Added)

1. **Next Event** - Shows next astronomy event as main state
2. **Next Event 2** - Second upcoming event
3. **Next Event 3** - Third upcoming event

Each has attributes: `description`, `when`, `date`, `time`, `days_until`, `type`

## Migration Steps

### Option 1: Fresh Install (Recommended for New Users)

1. **Remove YAML config** (if you have one):
   ```yaml
   # Remove this from configuration.yaml:
   stargazing:
     notify_service: notify.mandalore
   ```

2. **Restart Home Assistant** once to clear old YAML config

3. **Add via UI**:
   - Go to Settings → Devices & Services
   - Click "Add Integration"
   - Search for "Stargazing Conditions"
   - Follow the setup wizard
   - Configure your notification service and thresholds

4. **Done!** All entities will be under one device now

### Option 2: Keep YAML Config (Legacy Support)

Your existing YAML configuration will continue to work! No changes needed.

**Current config in `configuration.yaml`:**
```yaml
stargazing:
  notify_service: notify.mandalore
  minimum_score_notify: 80
  minimum_cloudless: 95
  minimum_transparency: 70
  minimum_seeing: 65
```

This still works, but:
- You won't get the device grouping
- No UI options flow
- Entities use old naming (sensor.stargazing_* instead of sensor.stargazing_conditions_*)
- Still requires restart for config changes

## What You'll Notice

### Before (v1.0)
```
Integration: Stargazing Conditions
  (Shows error: "This integration cannot be added from the UI")

Entities (scattered):
  sensor.stargazing_quality_score
  sensor.stargazing_rating
  sensor.stargazing_optimal_start
  sensor.stargazing_optimal_end
  sensor.stargazing_upcoming_events
    └─ events hidden in attributes
```

### After (v1.1 with UI config)
```
Integration: Stargazing Conditions ⚙️ Configure
  Device: Stargazing Conditions
    └─ 8 Entities:
       - Quality (%)
       - Rating
       - Optimal Start
       - Optimal End
       - Upcoming Events (count)
       - Next Event ⭐ NEW
       - Next Event 2 ⭐ NEW
       - Next Event 3 ⭐ NEW
```

## Configuration Changes

### New UI Settings Available

When you add via UI or click "Configure" on existing installation:

| Setting | Default | Description |
|---------|---------|-------------|
| Notification Service | notify.mandalore | Your notification service |
| Minimum Score | 80 | Score threshold for notifications |
| Minimum Cloudless | 95 | Required cloudless % |
| Minimum Transparency | 70 | Required transparency % |
| Minimum Seeing | 65 | Required seeing % |
| ZIP Code | (optional) | For local astronomy events |

### Changing Settings Without Restart

1. Go to Settings → Devices & Services
2. Find "Stargazing Conditions"
3. Click "Configure" (gear icon)
4. Adjust any settings
5. Click Submit
6. Changes apply **immediately** - no restart needed!

## Dashboard Updates

### Old Way (v1.0)
```yaml
# Had to use complex templates to access attributes
{{ state_attr('sensor.stargazing_upcoming_events', 'events')[0].name }}
```

### New Way (v1.1)
```yaml
# Events are now direct entities!
{{ states('sensor.stargazing_conditions_next_event') }}
```

See [DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md) for complete examples.

## Troubleshooting

### Issue: "Integration already configured"

**Cause:** You're trying to add via UI while YAML config exists.

**Solution:** Choose one:
- Remove YAML config and restart, then add via UI
- OR keep YAML config (it works, just won't have UI features)

### Issue: Old entity names don't match new names

**Cause:** YAML config uses different entity naming than UI config.

**Naming differences:**

| YAML Config | UI Config |
|-------------|-----------|
| sensor.stargazing_quality | sensor.stargazing_conditions_quality |
| sensor.stargazing_rating | sensor.stargazing_conditions_rating |
| sensor.stargazing_next_event_1 | sensor.stargazing_conditions_next_event |

**Solution:**
1. Update your dashboards/automations with new entity names
2. OR stick with YAML config to keep old names

### Issue: Entities not showing under device

**Cause:** Using legacy YAML config.

**Solution:** Migrate to UI config (see Option 1 above).

### Issue: "Add to Dashboard" button missing

**Cause:** Using YAML config or old entity IDs.

**Solution:** Entities added via UI config will have the "Add to Dashboard" button.

## Rollback (If Needed)

If you encounter issues, you can rollback:

1. **Remove UI config entry:**
   - Settings → Devices & Services
   - Find "Stargazing Conditions"
   - Click three dots → Delete

2. **Restore old manifest.json:**
   ```json
   "config_flow": false
   ```

3. **Keep YAML config:**
   ```yaml
   stargazing:
     notify_service: notify.mandalore
   ```

4. **Restart Home Assistant**

## File Changes Summary

### New Files
- `config_flow.py` - UI configuration flow
- `strings.json` - UI text translations
- `UPGRADE_GUIDE.md` (this file)
- `DASHBOARD_GUIDE.md`

### Modified Files
- `__init__.py` - Added `async_setup_entry()` support
- `sensor.py` - Added device support + 3 new event sensors
- `manifest.json` - Changed `config_flow: false` → `config_flow: true`

### Unchanged Files
- `const.py`
- `scoring.py`
- `astronomy_events.py`
- `notifications.py`
- `services.yaml`

## Questions?

- See [README.md](README.md) for general documentation
- See [DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md) for dashboard examples
- File issues at: https://github.com/beaubeau/stargazing/issues
