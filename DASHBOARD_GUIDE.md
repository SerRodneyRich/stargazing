# Dashboard Guide - Simple "Add to Dashboard" Method

Now that the integration is properly configured with device support, you can easily add entities to your dashboard using the standard Home Assistant UI.

## Quick Add to Dashboard (Recommended)

1. **Go to Settings → Devices & Services**
2. **Find "Stargazing Conditions"** in your integrations list
3. **Click on it** to see all 8 entities grouped together
4. **Click on any entity** (e.g., "Quality", "Rating", "Next Event")
5. **Click the cogwheel icon** in the top right
6. **Click "Add to Dashboard"** button
7. **Select your dashboard** and area
8. Done! The card is automatically created

## Available Entities (All Under One Device)

After setup, you'll have these entities grouped under "Stargazing Conditions":

### Core Sensors
- **Quality** - Quality score (0-100%)
- **Rating** - Text rating (EXCEPTIONAL/AMAZING/Good/Poor)
- **Optimal Start** - When to start observing tonight
- **Optimal End** - When viewing window ends

### Event Sensors (NEW!)
- **Next Event** - Next astronomy event (name shown as state)
- **Next Event 2** - Second upcoming event
- **Next Event 3** - Third upcoming event
- **Upcoming Events** - Total count of events (with all events in attributes)

Each event sensor shows:
- **State**: Event name (e.g., "Geminid Meteor Shower")
- **Attributes**:
  - `description`: Full event details
  - `when`: "Tonight" / "Tomorrow" / "In X days"
  - `date`: Formatted date
  - `time`: Formatted time
  - `days_until`: Number of days
  - `type`: Event type (meteor_shower, iss_pass, etc.)

## Simple Entity Card Examples

### Option 1: Automatic Entity Card
Just add any sensor using "Add to Dashboard" - Home Assistant will create an appropriate card automatically.

### Option 2: Manual Entities Card (No Custom Cards Needed)

```yaml
type: entities
title: Stargazing Tonight
entities:
  - entity: sensor.stargazing_conditions_quality
  - entity: sensor.stargazing_conditions_rating
  - entity: sensor.stargazing_conditions_next_event
    secondary_info: last-changed
  - entity: sensor.stargazing_conditions_next_event_2
  - entity: sensor.stargazing_conditions_next_event_3
```

### Option 3: Glance Card

```yaml
type: glance
title: Sky Conditions
entities:
  - entity: sensor.stargazing_conditions_quality
    name: Quality
  - entity: sensor.stargazing_conditions_rating
    name: Rating
  - entity: sensor.stargazing_conditions_optimal_start
    name: Start Time
```

### Option 4: Individual Event Card with Details

```yaml
type: entity
entity: sensor.stargazing_conditions_next_event
attribute: description
name: Next Astronomy Event
```

### Option 5: Simple Markdown Card for Events

```yaml
type: markdown
content: |
  ## Upcoming Astronomy Events

  **{{ states('sensor.stargazing_conditions_next_event') }}**
  {{ state_attr('sensor.stargazing_conditions_next_event', 'when') }}
  {{ state_attr('sensor.stargazing_conditions_next_event', 'description') }}

  **{{ states('sensor.stargazing_conditions_next_event_2') }}**
  {{ state_attr('sensor.stargazing_conditions_next_event_2', 'when') }}

  **{{ states('sensor.stargazing_conditions_next_event_3') }}**
  {{ state_attr('sensor.stargazing_conditions_next_event_3', 'when') }}
```

## Entity Naming Convention

With the new device-based structure, entity names follow this pattern:

**Legacy (YAML config):**
- `sensor.stargazing_quality`
- `sensor.stargazing_rating`
- `sensor.stargazing_next_event_1`

**New (UI config):**
- `sensor.stargazing_conditions_quality`
- `sensor.stargazing_conditions_rating`
- `sensor.stargazing_conditions_next_event`

All entities are grouped under the "Stargazing Conditions" device for easy organization.

## Why This Is Better

✅ **No custom cards required** - Works with standard HA cards
✅ **Events visible as entities** - Not buried in attributes
✅ **"Add to Dashboard" button works** - Standard HA UI workflow
✅ **Organized by device** - All sensors grouped together
✅ **Auto-discovery** - HA suggests relevant cards automatically
✅ **Mobile-friendly** - Standard cards work on HA mobile app

## Advanced: Using Attributes in Templates

Each event sensor has rich attributes you can use in template cards:

```yaml
type: markdown
content: |
  {% set event = 'sensor.stargazing_conditions_next_event' %}
  {% if states(event) != 'No event scheduled' %}
  ## 🌟 {{ states(event) }}

  **When:** {{ state_attr(event, 'when') }}
  **Date:** {{ state_attr(event, 'date') }}
  **Time:** {{ state_attr(event, 'time') }}

  {{ state_attr(event, 'description') }}
  {% endif %}
```

## Refreshing Events

Use the service call button or call the service manually:

```yaml
service: stargazing.refresh_astronomy_events
```

This fetches the latest events (meteor showers, ISS passes, planetary events) and updates all event sensors.
