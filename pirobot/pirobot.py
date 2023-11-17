import time
import re
import json
import random
import os
from pprint import pprint
from telethon import TelegramClient, events
from dotenv import load_dotenv

def run_bot():
    # Load environment variables
    load_dotenv()

    # Telegram API credentials
    session = os.environ.get('TG_SESSION', 'printer')
    api_id = os.getenv("API_ID")
    api_hash = os.getenv("API_HASH")
    debug_mode = os.getenv("DEBUG_MODE", "").upper() == "TRUE"

    # Proxy configuration (if needed)
    proxy = None

    # Create and start the Telegram client
    client = TelegramClient(session, api_id, api_hash, proxy=proxy).start()

    # List to track users who have sent messages
    sender_list = []

    # Read quizzes from JSON file
    with open('quizzes.json') as json_file:
        quizzes = json.load(json_file)

    # Event handler for new messages
    @client.on(events.NewMessage)
    async def handle_new_message(event):
        try:
            me = await client.get_me()
        except AttributeError:
            me = None

        # Get information about the sender
        from_user = await event.get_sender()

        # Check conditions for auto-reply
        proceed_auto_reply = (
            not getattr(from_user, 'bot', False) if debug_mode else
            not getattr(from_user, 'bot', False) and (
                event.is_private or (me and re.search("@" + me.username, event.raw_text))
            )
        )

        if proceed_auto_reply:
            # If conditions met, prepare and send auto-reply
            if not getattr(from_user, 'bot', False) and event:
                time.sleep(1)  # Rate-limit automatic replies
                # print(time.asctime(), '-', event.message)
                user_id = from_user.id
                username = from_user.username
                date = event.date.strftime('%a %b %d %H:%M:%S %Y')
                message_sent_by_sender = event.message.message if event.message.message else ""

                # Print the formatted message
                print(
                    f"User name :- @{username if username else 'None'}\n"
                    f"#if username = None then\n"
                    f"User id :- {user_id}\n"
                    f"Date :- {date}\n"
                    f"Message :- {message_sent_by_sender}\n"
                )
                # Build auto-reply message
                message = ""
                sender_list.append(from_user.id)

                if sender_list.count(from_user.id) < 2:
                    message = (
                        f"**AUTO REPLY**\n\nHi @{from_user.username},\n\n"
                        f"I'm sorry, my boss is currently offline. Please wait for a moment.\n"
                        f"Feel free to check out [HK4CRPRASAD](https://github.com/hk4crprasad) while waiting."
                        f"\n\n**AUTO REPLY**"
                    )
                elif sender_list.count(from_user.id) < 3:
                    message = f"**AUTO REPLY**\n\nPlease be patient, @{from_user.username}, my boss is still offline 😒"
                elif sender_list.count(from_user.id) < 4:
                    message = f"**AUTO REPLY**\n\n@{from_user.username}, Please bear with us 😅"
                else:
                    # Select a random quiz
                    random_number = random.randint(0, len(quizzes) - 1)
                    question = quizzes[random_number]['question']
                    answer = quizzes[random_number]['answer']
                    message = (
                        f"**AUTO REPLY**\n\n@{from_user.username}, How about playing a guessing game? 😁\n"
                        f"{question}\n{answer}\n"
                    )

                if message:
                    await event.reply(message)

    # Start and run the Telegram client
    client.start()
    try:
        client.run_until_disconnected()
    except Exception as e:
        print(f"Error: {e}")
        # Handle any unexpected errors gracefully
    finally:
        # Cleanup or additional actions can be performed here if needed
        pass

