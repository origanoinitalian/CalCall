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
    await update.message.reply_text('Welcome to Calendar Bot! Hope you get an appointment!')

    # Ask for the target calendar ID
    await update.message.reply_text('Please provide the Google Calendar ID of the person you want to schedule appointments with.')
    context.user_data['waiting_for_calendar_id'] = True

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.message.from_user.id
    logger.info(f"Handling message from user {telegram_id}")

    if context.user_data.get('waiting_for_calendar_id'):
        # Save the Google Calendar ID
        target_calendar_id = update.message.text
        logger.info(f"User provided calendar ID: {target_calendar_id}")

        # Save or update the calendar ID
        create_or_update_user(telegram_id, target_calendar_id)
        await update.message.reply_text(f'Target Calendar ID "{target_calendar_id}" saved!')
        context.user_data['waiting_for_calendar_id'] = False

        # Ask for the desired date
        await update.message.reply_text('Please provide the desired date for the appointment (e.g., YYYY-MM-DD).')
        context.user_data['waiting_for_date'] = True

    elif context.user_data.get('waiting_for_date'):
        # Process the desired date
        desired_date = update.message.text
        logger.info(f"User provided date: {desired_date}")

        try:
            date_time = datetime.strptime(desired_date, '%Y-%m-%d')
            user = get_user(telegram_id)
            if user:
                logger.info(f"Creating event for calendar ID: {user.target_calendar_id}")
                # Create a Google Calendar event
                event = {
                    'summary': 'Appointment',
                    'description': 'Scheduled via Telegram Bot',
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
                created_event = create_calendar_event(user.target_calendar_id, event)
                logger.info(f"Event created: {created_event}")
                await update.message.reply_text(f'Appointment for "{desired_date}" created! Event ID: {created_event["id"]}')
            else:
                await update.message.reply_text('You have not set a calendar ID yet. Use /start to set one.')
        except ValueError:
            await update.message.reply_text('Invalid date format. Please use YYYY-MM-DD.')
        except Exception as e:
            logger.error(f"Error creating event: {e}")
            await update.message.reply_text('An error occurred while creating the event. Please try again.')

        # Reset the state
        context.user_data['waiting_for_date'] = False

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