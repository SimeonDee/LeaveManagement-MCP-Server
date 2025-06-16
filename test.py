from datetime import datetime, timedelta

current_date = datetime.now()
# Add 3 days
day_1 = (current_date + timedelta(days=2)).strftime("%Y-%m-%d")
day_2 = (current_date + timedelta(days=3)).strftime("%Y-%m-%d")
day_3 = (current_date + timedelta(days=4)).strftime("%Y-%m-%d")
print(day_1, day_2, day_3)
