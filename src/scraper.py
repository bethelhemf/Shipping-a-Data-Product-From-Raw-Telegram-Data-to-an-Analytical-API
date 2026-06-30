import os
import json
import logging
import asyncio
from datetime import datetime
from telethon import TelegramClient, errors
from dotenv import load_dotenv  # <--- Added this

# --- SECURE CREDENTIALS ---
load_dotenv()
# We use os.getenv and convert API_ID to an integer
API_ID = int(os.getenv('TG_API_ID'))
API_HASH = os.getenv('TG_API_HASH')

# List of channels to scrape
CHANNELS = [
    'chemedethiopia',  
    'lobeliacomedics', 
    'TikvahPharma',    
]

# Setup Logging
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, 'scraping.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
# Also print logs to the terminal
console = logging.StreamHandler()
logging.getLogger('').addHandler(console)

class TelegramScraper:
    def __init__(self):
        # Initialize the client
        self.client = TelegramClient('kara_session', API_ID, API_HASH)

    async def setup_folders(self, channel_name, date_str):
        """Creates the partitioned directory structure."""
        image_path = f"data/raw/images/{channel_name}"
        json_path = f"data/raw/telegram_messages/{date_str}"
        os.makedirs(image_path, exist_ok=True)
        os.makedirs(json_path, exist_ok=True)
        return image_path, json_path

    async def scrape_channel(self, channel_username):
        logging.info(f"--- Starting scrape: {channel_username} ---")
        try:
            channel_data = []
            async for message in self.client.iter_messages(channel_username, limit=100):
                date_str = message.date.strftime('%Y-%m-%d')
                image_dir, json_dir = await self.setup_folders(channel_username, date_str)

                image_path = None
                if message.photo:
                    try:
                        image_filename = f"{message.id}.jpg"
                        image_path = os.path.join(image_dir, image_filename)
                        if not os.path.exists(image_path):
                            await self.client.download_media(message.photo, file=image_path)
                    except Exception as media_err:
                        logging.warning(f"Failed to download media for msg {message.id}: {media_err}")

                msg_data = {
                    "message_id": message.id,
                    "channel_name": channel_username,
                    "message_date": message.date.isoformat(),
                    "message_text": message.text or "",
                    "has_media": message.photo is not None,
                    "image_path": image_path,
                    "views": message.views or 0,
                    "forwards": message.forwards or 0
                }
                channel_data.append(msg_data)

            # SAVE JSON
            json_file_path = os.path.join(json_dir, f"{channel_username}.json")
            with open(json_file_path, 'w', encoding='utf-8') as f:
                json.dump(channel_data, f, indent=4, ensure_ascii=False)
            
            logging.info(f"Done! Saved {len(channel_data)} messages for {channel_username}")

        except errors.FloodWaitError as e:
            logging.error(f"Telegram Rate Limit hit! Must wait {e.seconds} seconds.")
        except errors.UsernameInvalidError:
            logging.error(f"Channel username {channel_username} does not exist.")
        except Exception as e:
            logging.error(f"Unexpected error in {channel_username}: {str(e)}")

            # Save the JSON file for this channel
            json_file_path = os.path.join(json_dir, f"{channel_username}.json")
            with open(json_file_path, 'w', encoding='utf-8') as f:
                json.dump(channel_data, f, indent=4, ensure_ascii=False)
            
            logging.info(f"Done! Saved {len(channel_data)} messages for {channel_username}")

        except Exception as e:
            logging.error(f"Error in {channel_username}: {str(e)}")

    async def run(self):
        async with self.client:
            # Check if we are authorized
            if not await self.client.is_user_authorized():
                print("Logging in for the first time...")
                # It will ask for your phone number in the terminal
                # Use international format: +2519...
            
            for channel in CHANNELS:
                await self.scrape_channel(channel)

if __name__ == "__main__":
    scraper = TelegramScraper()
    asyncio.run(scraper.run())