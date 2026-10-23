"""rules.py - Campus booking rules, kept separate from the main system logic.

To add a new campus, just add a new entry to CAMPUS_RULES.
To add a new type of rule, add a check inside check_booking_rules().
"""

# Each campus has its own constraints (dictionary of dictionaries)
CAMPUS_RULES = {
    "Durban": {
        "max_hours": 2,      # maximum duration per booking
        "open": 8,           # earliest start hour (08:00)
        "close": 17,         # booking must end by this hour (17:00)
        "max_active": 3,     # max upcoming bookings per lecturer
    },
    "Johannesburg": {
        "max_hours": 3,
        "open": 7,
        "close": 20,
        "max_active": 5,
    },
    "Cape Town": {
        "max_hours": 4,
        "open": 9,
        "close": 16,
        "max_active": 2,
    },
}


def get_policy_text(campus_name):
    """Return a short sentence describing the booking policy of a campus."""
    r = CAMPUS_RULES[campus_name]
    return (f"{campus_name} policy: max {r['max_hours']}h per booking, "
            f"hours {r['open']:02d}:00 to {r['close']:02d}:00, "
            f"max {r['max_active']} upcoming bookings per lecturer")


def check_booking_rules(campus_name, start_hour, duration, active_count):
    """Check a booking against the campus rules.
    Returns an error message, or an empty string if the booking is allowed."""
    r = CAMPUS_RULES[campus_name]

    if duration < 1:
        return "Duration must be at least 1 hour."
    if duration > r["max_hours"]:
        return f"{campus_name} allows a maximum of {r['max_hours']} hours per booking."
    if start_hour < r["open"] or start_hour + duration > r["close"]:
        return (f"{campus_name} bookings must be between "
                f"{r['open']:02d}:00 and {r['close']:02d}:00.")
    if active_count >= r["max_active"]:
        return (f"{campus_name} allows only {r['max_active']} upcoming "
                f"bookings per lecturer.")
    return ""
