def test_google_calendar_auth():
    try:
        service = get_calendar_service()
        print("Google Calendar authentication successful!")
        return True
    except Exception as e:
        print(f"Google Calendar authentication failed: {e}")
        return False

# Call the test function
if __name__ == '__main__':
    if test_google_calendar_auth():
        print("Proceeding to start the bot...")
        main()
    else:
        print("Fix the Google Calendar authentication issue before starting the bot.")