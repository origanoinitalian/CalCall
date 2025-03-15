import os
from dotenv import load_dotenv
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime, timedelta
from database import get_user, create_or_update_user
from google.oauth2 import service_account
from googleapiclient.discovery import build


# Load environment variables
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Google Calendar setup
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """Authenticate and return a Google Calendar API service."""
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('calendar', 'v3', credentials=credentials)
    return service

def create_calendar_event(calendar_id, event):
    """
    Create an event in the specified Google Calendar.
    :param calendar_id: The ID of the Google Calendar.
    :param event: A dictionary representing the event.
    """
    service = get_calendar_service()
    event = service.events().insert(calendarId=calendar_id, body=event).execute()
    return event
    

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Welcome the user
    await update.message.reply_text('Welcome to Calendar Call Bot! Hope you can get an appointment!')

    # Ask for the target calendar ID
    await update.message.reply_text('Please provide the Google Calendar ID of the person you want to schedule appointments with.')
    context.user_data['waiting_for_calendar_id'] = True


def validate_calendar_id(calendar_id):
    """Validate the calendar ID by attempting to retrieve its metadata."""
    try:
        service = get_calendar_service()
        calendar = service.calendars().get(calendarId=calendar_id).execute()
        logger.info(f"Calendar ID {calendar_id} is valid.")
        return True
    except Exception as e:
        logger.error(f"Invalid calendar ID: {e}")
        return False

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        logger.info("handle_message function triggered.")
        telegram_id = update.message.from_user.id
        logger.info(f"Handling message from user {telegram_id}")

        if context.user_data.get('waiting_for_calendar_id'):
            # Save the Google Calendar ID
            target_calendar_id = update.message.text
            logger.info(f"User provided calendar ID: {target_calendar_id}")

            # Validate the calendar ID
            if not validate_calendar_id(target_calendar_id):
                await update.message.reply_text('This calendar ID is not valid. Please provide a valid one, like "elonmusk@gmail.com".')
                return  # Exit the function if the calendar ID is invalid

            # Save or update the calendar ID
            create_or_update_user(telegram_id, target_calendar_id)
            logger.info(f"Target Calendar ID '{target_calendar_id}' saved for user {telegram_id}.")
            context.user_data['waiting_for_calendar_id'] = False

            # Ask for the desired date
            await update.message.reply_text('Please provide the desired date for the appointment (e.g., YYYY-MM-DD).')
            context.user_data['waiting_for_date'] = True
            logger.info("Waiting for date input from the user.")

        elif context.user_data.get('waiting_for_date'):
            # Process the desired date
            desired_date = update.message.text
            logger.info(f"User provided date: {desired_date}")

            try:
                # Parse the date
                date_time = datetime.strptime(desired_date, '%Y-%m-%d')
                logger.info(f"Parsed date: {date_time}")

                # Check if the date is in the past
                if date_time.date() < datetime.utcnow().date():
                    logger.info("User provided a date in the past.")
                    await update.message.reply_text("We're not time travelers here! Please give me a date that's today or in the future.")
                    return  # Exit the function if the date is invalid

                # Save the date and ask for the time
                context.user_data['desired_date'] = desired_date
                await update.message.reply_text('Please provide the desired time for the appointment (e.g., HH:MM in 24-hour format).')
                context.user_data['waiting_for_time'] = True
                context.user_data['waiting_for_date'] = False

            except ValueError:
                logger.error("Invalid date format provided by the user.")
                await update.message.reply_text('Invalid date format. Please use YYYY-MM-DD.')
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                await update.message.reply_text('An unexpected error occurred. Please try again.')

        elif context.user_data.get('waiting_for_time'):
            # Process the desired time
            desired_time = update.message.text
            logger.info(f"User provided time: {desired_time}")

            try:
                # Parse the time
                time_obj = datetime.strptime(desired_time, '%H:%M').time()
                logger.info(f"Parsed time: {time_obj}")

                # Combine date and time
                desired_date = context.user_data['desired_date']
                date_time = datetime.strptime(f"{desired_date} {desired_time}", '%Y-%m-%d %H:%M')
                logger.info(f"Combined date and time: {date_time}")

                # Check if the appointment is at least 5 hours in the future
                current_time = datetime.utcnow()
                time_difference = (date_time - current_time).total_seconds() / 3600  # Convert to hours
                logger.info(f"Time difference: {time_difference} hours")

                if time_difference < 5:
                    logger.info("User provided a time less than 5 hours in the future.")
                    await update.message.reply_text('The princess requires a minimum of 5 hours to prepare for your audience. 5 hours, minimum, before any appointments can be scheduled')
                    return  # Exit the function if the time is invalid

                # Save the date and time, and ask for the user's name
                context.user_data['date_time'] = date_time
                await update.message.reply_text('Please provide your name so the princess knows who is requesting the appointment.')
                context.user_data['waiting_for_name'] = True
                context.user_data['waiting_for_time'] = False

            except ValueError:
                logger.error("Invalid time format provided by the user.")
                await update.message.reply_text('Invalid time format. Please use HH:MM in 24-hour format.')
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                await update.message.reply_text('An unexpected error occurred. Please try again.')

        elif context.user_data.get('waiting_for_name'):
            # Process the user's name
            user_name = update.message.text
            logger.info(f"User provided name: {user_name}")

            # Save the name and create the event
            date_time = context.user_data['date_time']
            user = get_user(telegram_id)
            if user:
                logger.info(f"Creating event for calendar ID: {user.target_calendar_id}")
                # Create a Google Calendar event
                event = {
                    'summary': f'Appointment with {user_name}',
                    'description': f'Scheduled via Telegram Bot by {user_name}',
                    'start': {
                        'dateTime': date_time.isoformat(),
                        'timeZone': 'UTC',
                    },
                    'end': {
                        'dateTime': (date_time + timedelta(hours=1)).isoformat(),  # 1-hour appointment
                        'timeZone': 'UTC',
                    },
                }

                # Add the event to the user's Google Calendar
                try:
                    created_event = create_calendar_event(user.target_calendar_id, event)
                    logger.info(f"Event created: {created_event}")
                    await update.message.reply_text(f'Appointment for "{date_time.strftime("%Y-%m-%d %H:%M")}" with name "{user_name}" created!')
                except Exception as e:
                    logger.error(f"Error creating event: {e}")
                    await update.message.reply_text('An error occurred while creating the event. Please try again.')
            else:
                await update.message.reply_text('You have not set a calendar ID yet. Use /start to set one.')

            # Reset the state
            context.user_data['waiting_for_name'] = False

    except Exception as e:
        logger.error(f"Unexpected error in handle_message: {e}")
        await update.message.reply_text("An unexpected error occurred. Please try again.")


async def my_calendar_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.message.from_user.id
    user = get_user(telegram_id)

    if user:
        await update.message.reply_text(f'Your stored calendar ID is: {user.target_calendar_id}')
    else:
        await update.message.reply_text('You have not set a calendar ID yet. Use /start to set one.')

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CommandHandler("my_calendar_id", my_calendar_id))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()


