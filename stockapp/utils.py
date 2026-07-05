from datetime import date

# -------------------------------
# Seasons
# -------------------------------
SEASON_MONTHS = {
    "Winter": [12, 1, 2],
    "Spring": [3, 4, 5],
    "Summer": [6, 7, 8],
    "Autumn": [9, 10, 11],
}

def get_current_season(month):
    for season, months in SEASON_MONTHS.items():
        if month in months:
            return season
    return None

# -------------------------------
# Festivals
# -------------------------------
FESTIVALS = [
    {"name": "Diwali", "month": 11, "days": [5, 6, 7, 8, 9, 10]},
    {"name": "Christmas", "month": 12, "days": [20, 21, 22, 23, 24, 25]},
    {"name": "Pongal", "month": 1, "days": [13, 14, 15]},
    {"name": "Eid", "month": 4, "days": [9, 10, 11]},
]

def get_upcoming_festival(today=None, days_ahead=7):
    """
    Returns the upcoming festival info if it's within the next 'days_ahead' days.
    """
    if today is None:
        today = date.today()

    for fest in FESTIVALS:
        for fest_day in fest["days"]:
            fest_date = date(today.year, fest["month"], fest_day)
            delta_days = (fest_date - today).days
            if 0 <= delta_days <= days_ahead:
                return {"name": fest["name"], "days_left": delta_days}
    return None
