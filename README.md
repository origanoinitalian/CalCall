# CalCall

## Table of Contents
- [Description](#description)
- [Features](#features)
- [Setup](#setup)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)

## Description
CalCall is a Telegram bot that helps users schedule appointments by interacting with Google Calendar. It allows users to specify a date and time, and the bot creates an event in the specified Google Calendar.



## Features
- Schedule appointments with a specific Google Calendar ID.
- Validate appointment dates and times.
- Ensure appointments are scheduled at least 5 hours in advance.
- Store user data (e.g., calendar IDs) in a database.

## Setup
Follow these steps to set up and run CalCall on your local machine.

### Prerequisites
- Python 3.8 or higher
- A Telegram bot token (get it from [BotFather](https://core.telegram.org/bots#botfather))
- A Google Cloud Service Account credentials file (follow [this guide](https://developers.google.com/workspace/guides/create-credentials#service-account) to create one)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/origanoinitalian/CalCall.git

2. Navigate to the project folder:
    ```bash
    cd CalCall

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt

4. Create a .env file in the project root and add the following environment variables:
    ```plaintext
    # .env.example
    TELEGRAM_BOT_TOKEN=your-telegram-bot-token
    SERVICE_ACCOUNT_FILE=path/to/service-account-file.json
    DATABASE_URL=sqlite:///path/to/your/database.db

Replace your-telegram-bot-token with your actual Telegram bot token.

Replace path/to/service-account-file.json with the path to your Google Cloud Service Account credentials file.

Replace path/to/your/database.db with the path to your SQLite database file 


5. Run the bot:
    ```bash
    python bot.py
    



### **3. Keep Your `.env` File Private**
- **Never commit your `.env` file to GitHub**. It contains sensitive information like your bot token and database URL.
- Ensure your `.env` file is listed in your `.gitignore` file to prevent accidental commits:
  ```plaintext
  # Ignore environment variables
  .env


Usage

Once the bot is running, interact with it on Telegram:

    Start the bot by sending /start.

    Provide the Google Calendar ID of the person you want to schedule appointments with.

    Enter the desired date (e.g., 2023-10-15).

    Enter the desired time (e.g., 14:00).

    Provide your name so the recipient knows who is requesting the appointment.

The bot will create an event in the specified Google Calendar and confirm the appointment.



### Contributing

Contributions are welcome! If you'd like to contribute, please follow these steps:

1. Fork the repository.

2. Create a new branch for your feature or bugfix:
    ```bash
    git checkout -b feature/your-feature-name

3. Commit your changes:
    ```bash
    git commit -m "Add your commit message here"

4. Push to the branch:
    ```bash
    git push origin feature/your-feature-name

5. Open a pull request and describe your changes.



## Troubleshooting

### Bot Not Responding
- Ensure your `.env` file is correctly configured.
- Check that your Telegram bot token is valid.

### Google Calendar API Errors
- Ensure your Google Cloud Service Account credentials file is valid and has the necessary permissions.
- Verify that the calendar ID you provided is correct.
