# Using the Stargazing Card

## After Restarting Home Assistant

After you restart HA with the updated integration:

### 1. Add the Card Resource (One-Time Setup)

Go to: **Settings → Dashboards → Resources (top right menu) → Add Resource**

- **URL**: `/hacsfiles/stargazing/stargazing-card.js`
- **Resource type**: `JavaScript Module`
- Click **Create**

### 2. Add the Card to Your Dashboard

1. Go to any dashboard
2. Click **Edit Dashboard** (top right)
3. Click **Add Card**
4. Search for **"Stargazing Card"** in the card picker
5. Click it
6. The card will appear with your stargazing data!

## What the Card Shows

- **Quality Score** (0-100%) in a colored circle
- **Rating** (EXCEPTIONAL/AMAZING/Good/Poor) with emoji
- **Viewing Window** - Start and end times for tonight
- **Upcoming Events** - Next 3 astronomy events with full summaries

## Event Display

Events now show as: **"Geminid Meteor Shower - Tomorrow at 02:00 AM"**

All event details (description, type, days until) are in the attributes if you need them for automations.

## Troubleshooting

**Card doesn't appear in picker:**
- Make sure you added the resource (step 1)
- Clear browser cache (Ctrl+F5)
- Check browser console for errors

**"Entity not found" error:**
- Make sure integration is configured via UI (Settings → Devices & Services)
- Check that entities exist: `sensor.stargazing_conditions_quality`

**Only 5 entities instead of 8:**
- Remove the integration
- Delete custom_components/stargazing/__pycache__
- Restart HA
- Re-add integration via UI
