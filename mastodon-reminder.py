import datetime
import json
import os

from dotenv import load_dotenv
from mastodon import Mastodon

load_dotenv()

mastodon = Mastodon(
    api_base_url=os.getenv("MASTODON_API_BASE_URL"),
    client_id=os.getenv("MASTODON_CLIENT_ID"),
    client_secret=os.getenv("MASTODON_CLIENT_SECRET"),
    access_token=os.getenv("MASTODON_ACCESS_TOKEN"),
)


def send_reminder(date, location, link):
    mastodon.toot(
        "📢 Reminder: Next Hackergarten is in one week! 📢\n"
        f"Join us on the {date} at 18:00 at the {location}.\n\n"
        f"More info: {link}"
    )


with open("./events.json") as json_file:
    data = json.load(json_file)

    for event in data:
        # Convert date to datetime object
        event_date = datetime.datetime.strptime(event["date"], "%Y-%m-%d").date()
        today = datetime.datetime.now().date()

        # Check if event is one week away
        if (event_date - today).days == 7:
            send_reminder(event["date"], event["venue"], event["links"][0]["url"])

        # If events are in the past break for loop
        if event_date < today:
            break
