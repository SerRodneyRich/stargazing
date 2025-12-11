"""Astronomy events fetcher for significant sky events."""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import requests

_LOGGER = logging.getLogger(__name__)


class AstronomyEventsFetcher:
    """Fetch astronomy events from various sources."""

    def __init__(self, latitude: float, longitude: float, zip_code: str = None):
        """Initialize fetcher with location.

        Args:
            latitude: Location latitude
            longitude: Location longitude
            zip_code: Optional ZIP code for reference
        """
        self.latitude = latitude
        self.longitude = longitude
        self.zip_code = zip_code
        self.events = []
        self.last_updated = None

    async def fetch_events(self, days_ahead: int = 30) -> List[Dict]:
        """Fetch all astronomy events for next N days.

        Args:
            days_ahead: Number of days to look ahead (default: 30)

        Returns:
            List of event dicts with name, description, datetime
        """
        events = []

        # Try various sources
        events.extend(await self._fetch_meteor_showers(days_ahead))
        events.extend(await self._fetch_planet_events(days_ahead))
        events.extend(await self._fetch_iss_passes(days_ahead))

        # Sort by datetime
        events.sort(key=lambda x: x.get("datetime", datetime.now()))

        self.events = events
        self.last_updated = datetime.now()

        _LOGGER.info(f"Fetched {len(events)} astronomy events")
        return events

    async def _fetch_meteor_showers(self, days_ahead: int) -> List[Dict]:
        """Fetch meteor shower events.

        Uses a static database of known meteor showers for this season.

        Args:
            days_ahead: Number of days ahead to check

        Returns:
            List of meteor shower events
        """
        try:
            # Hardcoded meteor showers for Dec 2025 - Jan 2026
            # (In production, would fetch from calendar API)
            today = datetime.now()
            end_date = today + timedelta(days=days_ahead)

            meteor_events = [
                {
                    "name": "Geminid Meteor Shower",
                    "description": "Peak rate: ~120 meteors/hour. Best in Dec 12-14 midnight hours.",
                    "datetime": datetime(2025, 12, 13, 2, 0),
                    "type": "meteor_shower",
                    "visible": True,
                },
                {
                    "name": "Ursid Meteor Shower",
                    "description": "Peak rate: ~10 meteors/hour. Best Dec 22-23.",
                    "datetime": datetime(2025, 12, 23, 2, 0),
                    "type": "meteor_shower",
                    "visible": True,
                },
                {
                    "name": "Quadrantid Meteor Shower",
                    "description": "Peak rate: ~120 meteors/hour. Best Jan 3-4.",
                    "datetime": datetime(2026, 1, 4, 2, 0),
                    "type": "meteor_shower",
                    "visible": False,  # Beyond lookhead
                },
            ]

            # Filter to date range
            return [e for e in meteor_events if today <= e["datetime"] <= end_date]

        except Exception as e:
            _LOGGER.error(f"Error fetching meteor showers: {e}")
            return []

    async def _fetch_planet_events(self, days_ahead: int) -> List[Dict]:
        """Fetch planetary visibility and conjunction events.

        Args:
            days_ahead: Number of days ahead

        Returns:
            List of planetary events
        """
        try:
            today = datetime.now()
            end_date = today + timedelta(days=days_ahead)

            planetary_events = [
                {
                    "name": "Jupiter at Opposition",
                    "description": "Jupiter at its closest to Earth. Best observation night of the year.",
                    "datetime": datetime(2025, 12, 15, 0, 0),
                    "type": "opposition",
                    "visible": True,
                },
                {
                    "name": "Saturn - Best Viewing",
                    "description": "Saturn well-positioned for observation. Evening visibility.",
                    "datetime": datetime(2025, 12, 18, 19, 0),
                    "type": "favorable_position",
                    "visible": True,
                },
                {
                    "name": "Venus Evening Star",
                    "description": "Venus visible as bright evening star, sets ~2 hours after sunset.",
                    "datetime": datetime(2025, 12, 20, 18, 30),
                    "type": "visibility",
                    "visible": True,
                },
            ]

            return [e for e in planetary_events if today <= e["datetime"] <= end_date]

        except Exception as e:
            _LOGGER.error(f"Error fetching planet events: {e}")
            return []

    async def _fetch_iss_passes(self, days_ahead: int) -> List[Dict]:
        """Fetch ISS pass predictions for location.

        Uses ISS-Above API which is free and doesn't require authentication.

        Args:
            days_ahead: Number of days ahead

        Returns:
            List of ISS pass events
        """
        try:
            # ISS-Above API for pass predictions
            url = "https://api.iss-above.com/v1/passes/latlong"
            params = {
                "lat": self.latitude,
                "lon": self.longitude,
                "category": "visible",
                "limit": 10,
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            events = []

            if "passes" in data:
                for pass_info in data["passes"]:
                    try:
                        # Parse ISS pass data
                        start_time = datetime.fromtimestamp(pass_info["startUTC"])
                        end_time = datetime.fromtimestamp(pass_info["endUTC"])

                        # Only include if within lookhead
                        if start_time <= datetime.now() + timedelta(days=days_ahead):
                            max_elevation = pass_info.get("maxElevation", 0)
                            brightness = pass_info.get("magnitude", 0)

                            events.append(
                                {
                                    "name": "ISS Pass - Bright Satellite",
                                    "description": (
                                        f"International Space Station pass. "
                                        f"Peak elevation: {max_elevation:.0f}° "
                                        f"(Magnitude: {brightness:.1f}). "
                                        f"Duration: {int((end_time - start_time).total_seconds() / 60)} min."
                                    ),
                                    "datetime": start_time,
                                    "type": "iss_pass",
                                    "visible": True,
                                    "max_elevation": max_elevation,
                                    "brightness": brightness,
                                }
                            )
                    except (KeyError, ValueError) as e:
                        _LOGGER.debug(f"Error parsing ISS pass: {e}")
                        continue

            _LOGGER.info(f"Fetched {len(events)} ISS passes")
            return events

        except requests.RequestException as e:
            _LOGGER.warning(f"Error fetching ISS passes: {e}")
            return []
        except Exception as e:
            _LOGGER.error(f"Error processing ISS passes: {e}")
            return []

    def get_next_event(self) -> Optional[Dict]:
        """Get next upcoming astronomy event.

        Returns:
            Event dict or None if no events
        """
        if not self.events:
            return None

        now = datetime.now()
        upcoming = [e for e in self.events if e.get("datetime", now) >= now]

        return upcoming[0] if upcoming else None

    def get_events_for_date(self, target_date: datetime) -> List[Dict]:
        """Get events for a specific date.

        Args:
            target_date: Date to look for events

        Returns:
            List of events on that date
        """
        target_start = target_date.replace(hour=0, minute=0, second=0)
        target_end = target_start + timedelta(days=1)

        return [
            e
            for e in self.events
            if target_start <= e.get("datetime", target_start) < target_end
        ]

    def format_events_summary(self, max_events: int = 3) -> str:
        """Format next events as readable string.

        Args:
            max_events: Maximum events to include

        Returns:
            Formatted string
        """
        if not self.events:
            return "No major events scheduled"

        now = datetime.now()
        upcoming = [e for e in self.events if e.get("datetime", now) >= now][
            :max_events
        ]

        if not upcoming:
            return "No upcoming events"

        lines = ["Upcoming Events:"]
        for event in upcoming:
            event_time = event.get("datetime", now)
            days_until = (event_time - now).days
            if days_until == 0:
                when = "Tonight"
            elif days_until == 1:
                when = "Tomorrow"
            else:
                when = f"in {days_until} days"

            lines.append(f"• {event.get('name', 'Event')}: {when}")

        return "\n".join(lines)
