# Configuration Examples

## Minimal Configuration (Start Here)

```yaml
stargazing:
  notify_service: notify.mandalore
```

This uses default thresholds optimized for high dark sky areas.

## Standard Configuration

```yaml
stargazing:
  notify_service: notify.mandalore
  minimum_score_notify: 80
  minimum_cloudless: 95
  minimum_transparency: 70
  minimum_seeing: 65
  zip_code: "88431"
```

## More Lenient (Get More Notifications)

For areas with less ideal conditions:

```yaml
stargazing:
  notify_service: notify.mandalore
  minimum_score_notify: 70
  minimum_cloudless: 90
  minimum_transparency: 60
  minimum_seeing: 55
```

## Very Strict (Perfectionists Only)

For when you only want exceptional nights:

```yaml
stargazing:
  notify_service: notify.mandalore
  minimum_score_notify: 85
  minimum_cloudless: 98
  minimum_transparency: 80
  minimum_seeing: 75
```

## Alternative Notification Services

### Native App (iOS/Android)

```yaml
stargazing:
  notify_service: notify.mobile_app_iphone
```

### Telegram

```yaml
stargazing:
  notify_service: notify.telegram
```

### Discord

```yaml
stargazing:
  notify_service: notify.discord
```

## Location Customization

Set your location for accurate astronomy events:

```yaml
stargazing:
  notify_service: notify.mandalore
  zip_code: "88431"        # Your ZIP code
```

Or approximate by coordinates (if needed):

```yaml
# This gets extracted from AstroWeather automatically
# Override if needed in advanced cases
```

## Understanding the Thresholds

### minimum_cloudless: 95

- **Mandatory minimum** to even consider observing
- Below 95%: Score automatically becomes 0
- 95-100%: Bonus points for clearer skies
- Your high dark sky area needs this standard

### minimum_transparency: 70

- Atmosphere clarity for faint objects
- Below 70%: Reduced points
- 70-100%: Good transparency
- Combined with seeing, indicates air quality

### minimum_seeing: 65

- Atmospheric steadiness for detail
- Below 65%: Reduced points
- 65-100%: Good atmospheric stability
- Important for planetary observation

### minimum_score_notify: 80

- Threshold for notifications
- Below: No notification (log only)
- 80-89: "AMAZING" notification
- 90-100: "EXCEPTIONAL" immediate notification

## Notification Frequency Expectations

With standard configuration (88431 area):

```
EXCEPTIONAL (90-100):  2-3x per month
AMAZING (80-89):       1-2x per week
Good (60-79):          Log only
Poor (<60):            Most nights
```

With lenient configuration:

```
EXCEPTIONAL (90-100):  1x per week
AMAZING (80-89):       2-3x per week
Good (60-79):          Log only
Poor (<60):            Many nights
```

With strict configuration:

```
EXCEPTIONAL (90-100):  1-2x per month
AMAZING (80-89):       Few per month
Good (60-79):          Log only
Poor (<60):            Most nights
```

## Testing Your Configuration

After changing configuration:

1. Restart Home Assistant
2. Check current score: Developer Tools → States → `sensor.stargazing_quality_score`
3. Note the score and rating
4. Adjust if needed and repeat

## Migration from Another System

If migrating from different thresholds:

1. Note your old thresholds
2. Set to those in configuration.yaml
3. Observe notification frequency
4. Adjust up or down based on preference
5. Leave for 2-4 weeks to find optimal point

## YAML Syntax Tips

Ensure proper YAML formatting:

```yaml
# ✓ Correct
stargazing:
  notify_service: notify.mandalore
  minimum_score_notify: 80

# ✗ Wrong (no colon after notify_service)
stargazing:
  notify_service notify.mandalore

# ✗ Wrong (inconsistent indentation)
stargazing:
notify_service: notify.mandalore
```

Validate YAML: Use online YAML validators or `home-assistant --script check_config`

## Advanced: Per-Night Configuration

Want different thresholds for different times?

Create automation:
```yaml
automation:
  - alias: "Stargazing - Relax standards on weekends"
    trigger:
      platform: time
      at: "18:00:00"
    condition:
      - condition: time
        weekday:
          - fri
          - sat
    action:
      # You could dynamically adjust here
      - service: stargazing.check_conditions_now
```

(This is advanced - standard config is recommended)

## Common Issues & Solutions

### Getting too many notifications?

Raise thresholds:
```yaml
minimum_score_notify: 85
minimum_transparency: 75
minimum_seeing: 70
```

### Not getting any notifications?

Lower thresholds:
```yaml
minimum_score_notify: 70
minimum_transparency: 60
minimum_seeing: 55
```

### Score is always 0?

Check `minimum_cloudless`:
```yaml
minimum_cloudless: 90  # Lower if your area usually < 95%
```

### Not getting events?

Verify zip_code:
```yaml
zip_code: "88431"  # Check your actual ZIP
```

## Example: Desert Observatory

```yaml
stargazing:
  notify_service: notify.mandalore
  minimum_score_notify: 80
  minimum_cloudless: 98        # Very strict
  minimum_transparency: 75     # High quality
  minimum_seeing: 70
  zip_code: "88401"
```

## Example: Suburban Observer

```yaml
stargazing:
  notify_service: notify.mandalore
  minimum_score_notify: 70
  minimum_cloudless: 85        # More lenient
  minimum_transparency: 60
  minimum_seeing: 55
  zip_code: "10001"
```

## Next: Automations

See integration documentation for automation examples using your configuration.
