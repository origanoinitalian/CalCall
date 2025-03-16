from database import get_user, create_or_update_user

# Test create_or_update_user
telegram_id = "avishanabdinezhad"  # Replace with a real telegram_id
target_calendar_id = "avishanabdinejad@gmail.com"

# Save the calendar ID
create_or_update_user(telegram_id, target_calendar_id)
print(f"Saved calendar ID: {target_calendar_id}")

# Retrieve the calendar ID
user = get_user(telegram_id)
if user:
    print(f"Retrieved calendar ID: {user.target_calendar_id}")
else:
    print("User not found.")