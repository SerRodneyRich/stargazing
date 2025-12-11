"""Stargazing quality scoring algorithm."""

import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

_LOGGER = logging.getLogger(__name__)


class StargazingScoringEngine:
    """Calculate stargazing quality score based on AstroWeather data."""

    def __init__(
        self,
        min_cloudless: float = 95,
        min_transparency: float = 70,
        min_seeing: float = 65,
    ):
        """Initialize scoring engine with thresholds.

        Args:
            min_cloudless: Minimum cloudless percentage (0-100)
            min_transparency: Minimum transparency percentage (0-100)
            min_seeing: Minimum seeing percentage (0-100)
        """
        self.min_cloudless = min_cloudless
        self.min_transparency = min_transparency
        self.min_seeing = min_seeing

    def calculate_score(self, astroweather_data: Dict) -> int:
        """Calculate stargazing quality score (0-100).

        High standards scoring:
        - Cloudless is mandatory (≥95%)
        - Transparency and seeing heavily weighted
        - Moon phase reduces score proportionally

        Args:
            astroweather_data: Data dict from AstroWeather entity attributes
                Expected keys:
                - cloudless_percentage (0-100)
                - transparency_percentage (0-100)
                - seeing_percentage (0-100)
                - calm_percentage (0-100)
                - moon_phase (0-100)
                - moon_icon (string: 'moon-new', 'moon-full', etc)

        Returns:
            Score 0-100
        """
        try:
            cloudless = float(astroweather_data.get("cloudless_percentage", 0))
            transparency = float(astroweather_data.get("transparency_percentage", 0))
            seeing = float(astroweather_data.get("seeing_percentage", 0))
            calm = float(astroweather_data.get("calm_percentage", 0))
            moon_phase = float(astroweather_data.get("moon_phase", 0))
            moon_icon = astroweather_data.get("moon_icon", "")

            # Mandatory threshold: cloudless ≥ minimum
            if cloudless < self.min_cloudless:
                return 0  # Not worth going out

            # Base score: 100 available points to distribute
            score = 0

            # Cloudless (30 points): Scales from 0 to 30 as cloudless goes from min to 100%
            cloudless_above_min = cloudless - self.min_cloudless
            max_cloudless_range = 100 - self.min_cloudless
            if max_cloudless_range > 0:
                cloudless_ratio = cloudless_above_min / max_cloudless_range
                score += min(30, cloudless_ratio * 35)  # Allow up to 30 pts
            else:
                score += 30

            # Transparency (25 points): Scale with your minimum
            if transparency >= self.min_transparency:
                transparency_ratio = (transparency - self.min_transparency) / (
                    100 - self.min_transparency
                )
                score += min(25, transparency_ratio * 28)
            else:
                # Below minimum, but still give partial credit
                score += (transparency / self.min_transparency) * 10

            # Seeing (20 points): Scale with your minimum
            if seeing >= self.min_seeing:
                seeing_ratio = (seeing - self.min_seeing) / (100 - self.min_seeing)
                score += min(20, seeing_ratio * 22)
            else:
                # Below minimum, but still give partial credit
                score += (seeing / self.min_seeing) * 8

            # Calm/Wind Stability (15 points)
            calm_ratio = calm / 100
            score += calm_ratio * 15

            # Moon penalty: Reduce score based on moon phase and visibility
            # Full moon = -10 pts, new moon = 0 penalty
            if "new" in moon_icon.lower() or "no-moon" in moon_icon.lower():
                moon_penalty = 0
            elif "full" in moon_icon.lower():
                moon_penalty = 10
            else:
                # Waxing/waning: penalty scales with phase
                moon_penalty = (moon_phase / 100) * 10

            score -= moon_penalty

            # Ensure score is in valid range
            final_score = max(0, min(100, score))

            _LOGGER.debug(
                f"Score calculation: cloudless={cloudless:.1f}%, "
                f"transparency={transparency:.1f}%, seeing={seeing:.1f}%, "
                f"calm={calm:.1f}%, moon_phase={moon_phase:.1f}% "
                f"-> score={final_score:.0f}/100"
            )

            return int(final_score)

        except (KeyError, ValueError, TypeError) as e:
            _LOGGER.error(f"Error calculating score: {e}")
            return 0

    def get_rating(self, score: int) -> str:
        """Get human-readable rating for score.

        Args:
            score: Quality score (0-100)

        Returns:
            Rating string: "EXCEPTIONAL", "AMAZING", "Good", or "Poor"
        """
        if score >= 90:
            return "EXCEPTIONAL"
        elif score >= 80:
            return "AMAZING"
        elif score >= 60:
            return "Good"
        else:
            return "Poor"

    def get_rating_emoji(self, score: int) -> str:
        """Get emoji for rating.

        Args:
            score: Quality score (0-100)

        Returns:
            Emoji string
        """
        rating = self.get_rating(score)
        return {
            "EXCEPTIONAL": "⭐",
            "AMAZING": "🌟",
            "Good": "✨",
            "Poor": "🌫️",
        }.get(rating, "❓")

    def calculate_optimal_viewing_window(
        self, sunset_time: datetime, sunrise_time: datetime
    ) -> Tuple[datetime, datetime]:
        """Calculate optimal viewing window from sunset to midnight.

        For high standards, recommend from astronomical dusk to midnight,
        but may extend based on conditions.

        Args:
            sunset_time: Time of sunset (civil)
            sunrise_time: Time of next sunrise

        Returns:
            Tuple of (start_time, end_time)
        """
        # Typical dark sky starts 30-40 mins after civil sunset (astronomical dusk)
        # For practical purposes: sunset + 45 minutes to midnight
        start_time = sunset_time + timedelta(minutes=45)

        # End at midnight or 1 hour before dawn, whichever is earlier
        midnight = sunset_time.replace(hour=0, minute=0, second=0) + timedelta(days=1)
        end_time = min(midnight, sunrise_time - timedelta(hours=1))

        return (start_time, end_time)

    def get_score_breakdown(self, astroweather_data: Dict) -> Dict:
        """Get detailed breakdown of score components.

        Args:
            astroweather_data: Data dict from AstroWeather

        Returns:
            Dict with component scores and explanations
        """
        cloudless = float(astroweather_data.get("cloudless_percentage", 0))
        transparency = float(astroweather_data.get("transparency_percentage", 0))
        seeing = float(astroweather_data.get("seeing_percentage", 0))
        calm = float(astroweather_data.get("calm_percentage", 0))
        moon_phase = float(astroweather_data.get("moon_phase", 0))

        breakdown = {
            "cloudless": {
                "value": cloudless,
                "threshold": self.min_cloudless,
                "status": "✓ OK" if cloudless >= self.min_cloudless else "✗ Too cloudy",
            },
            "transparency": {
                "value": transparency,
                "threshold": self.min_transparency,
                "status": "✓ Good" if transparency >= self.min_transparency else "⚠ Poor",
            },
            "seeing": {
                "value": seeing,
                "threshold": self.min_seeing,
                "status": "✓ Steady" if seeing >= self.min_seeing else "⚠ Turbulent",
            },
            "calm": {
                "value": calm,
                "threshold": 60,
                "status": "✓ Calm" if calm >= 60 else "⚠ Windy",
            },
            "moon_phase": {
                "value": moon_phase,
                "effect": "None"
                if moon_phase < 10 or moon_phase > 90
                else f"Slight interference ({moon_phase:.0f}%)",
            },
        }

        return breakdown
