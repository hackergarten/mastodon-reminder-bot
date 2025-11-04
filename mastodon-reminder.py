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
def add_location_hashtags(location):
    if "Dortmund" in location:
        return "#Dortmund"
    if "Stuttgart" in location:
        return "#Stuttgart"
    if "Basel" in location:
        return "#Basel"
    if "Lucerne" in location:
        return "#Lucerne"
    if "Zurich" in location or "Zürich" in location:
        return "#Zurich"
    return ""

def send_reminder(date, venue, location, link):
    d = datetime.datetime.strptime(date, "%Y-%m-%d")  # Adjust format if needed
    formatted_date = d.strftime("%d.%m.%y")
    tagged_location = add_location_hashtags(location)
    mastodon.toot(
        "📢 Reminder: Next #Hackergarten is in one week! 📢\n"
        f"Join us on the {formatted_date} at 18:00 at {venue} in {location}.\n\n"
        f"More info: {link}"
        f"{tagged_location}"
    )

with open("./events.json") as json_file:
    data = json.load(json_file)

    for event in data:
        # Convert date to datetime object
        event_date = datetime.datetime.strptime(event["date"], "%Y-%m-%d").date()
        today = datetime.datetime.now().date()

        # Check if event is one week away
        if (event_date - today).days == 7:
            send_reminder(event["date"], event["venue"], event["address"], event["links"][0]["url"])

        # If events are in the past break for loop
        if event_date < today:
            break
