import os
import json
import datetime
import logging
import typer
from dotenv import load_dotenv
from mastodon import Mastodon
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

app = typer.Typer()

@dataclass
class Event:
    date: datetime.date
    venue: str
    link: str

@app.command()
def remind(event_files: list[str] = typer.Argument(..., help="List of event JSON files"), days_before: int = typer.Option(7, help="Send reminder N days before event")):
    """Send reminders exactly one week before the event date."""
    mastodon = get_mastodon_client()
    today = datetime.datetime.now().date()
    for event in get_events_from_files(event_files):
        if event.date == today + datetime.timedelta(days=days_before):
            send_reminder(mastodon, event.date.strftime("%Y-%m-%d"), event.venue, event.link, days_before)

@app.command()
def announce(event_files: list[str] = typer.Argument(..., help="List of event JSON files")):
    """Announce upcoming events now."""
    mastodon = get_mastodon_client()
    today = datetime.datetime.now().date()
    for event in get_events_from_files(event_files):
        if event.date >= today:
            send_new_event_announcement(mastodon, event.date.strftime("%Y-%m-%d"), event.venue, event.link)

def get_mastodon_client():
    mapping = (
        ("api_base_url", "MASTODON_API_BASE_URL"),
        ("client_id", "MASTODON_CLIENT_ID"),
        ("client_secret", "MASTODON_CLIENT_SECRET"),
        ("access_token", "MASTODON_ACCESS_TOKEN")
    )
    load_dotenv()
    params = {key: os.getenv(value) for key, value in mapping}
    missing = [value for key, value in mapping if not params.get(key)]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    return Mastodon(**params)

def get_events_from_files(file_paths: list[str]):
    for path in file_paths:
        with open(path) as json_file:
            data = json.load(json_file)
            for event in data:
                yield Event(
                    date=datetime.datetime.strptime(event["date"], "%Y-%m-%d").date(),
                    venue=event["venue"],
                    link=event["links"][0]["url"]
                )

def send_reminder(mastodon, date, location, link, days_before):
    message = (
        f"\ud83d\udce2 Reminder: Next Hackergarten is in {days_before} days! \ud83d\udce2\n"
        f"Join us on the {date} at 18:00 at the {location}.\n\n"
        f"More info: {link}"
    )
    mastodon.toot(message)
    logging.info(f"Sent reminder for {date} at {location}: {link}")

def send_new_event_announcement(mastodon, date, location, link):
    message = (
        "\U0001F389 New Hackergarten Event Announced! \U0001F389\n"
        f"Join us on the {date} at 18:00 at the {location}.\n\n"
        f"More info: {link}"
    )
    mastodon.toot(message)
    logging.info(f"Announced new event for {date} at {location}: {link}")

if __name__ == "__main__":
    app()
