import os
import sys
import json
import datetime
import logging
import typer
from dotenv import load_dotenv
from mastodon import Mastodon
from dataclasses import dataclass
import re
import hashlib

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

app = typer.Typer()

@dataclass
class Event:  # add fields as needed
    date: datetime.date
    venue: str
    link: str

@app.command()
def remind(event_files: list[str] = typer.Argument(..., help="List of event JSON files (use '-' to read from stdin)"), days_before: int = typer.Option(7, help="Send reminder N days before event")):
    """
    Send reminders exactly one week before the event date.
    If event_files is ['-'], events are read as a single JSON list from stdin.
    """
    mastodon = get_mastodon_client()
    today = datetime.datetime.now().date()
    for event in get_events_from_files(event_files):
        if event.date == today + datetime.timedelta(days=days_before):
            send_reminder(mastodon, event.date.strftime("%Y-%m-%d"), event.venue, event.link, days_before)

@app.command()
def announce(event_files: list[str] = typer.Argument(..., help="List of event JSON files (use '-' to read from stdin)")):
    """
    Announce upcoming events now.
    If event_files is ['-'], events are read as a single JSON list from stdin.
    """
    mastodon = get_mastodon_client()
    today = datetime.datetime.now().date()
    for event in get_events_from_files(event_files):
        if event.date >= today:
            send_new_event_announcement(mastodon, event.date.strftime("%Y-%m-%d"), event.venue, event.link)

@app.command()
def split_events(
    event_files: list[str] = typer.Argument(..., help="List of event JSON files (use '-' to read from stdin)"),
    output_folder: str = typer.Option(..., "--output-folder", "-o", help="Output folder for individual event files")
):
    """
    Split raw events from input files into individual JSON files in the output folder.
    Each file is named as <date>_<venue-normalized>_<hash>.json.
    If event_files is ['-'], events are read as a single JSON list from stdin.
    """

    os.makedirs(output_folder, exist_ok=True)
    for event in get_raw_events_from_files(event_files):
        date = event.get("date", "unknown")
        venue = event.get("venue", "unknown")
        # Normalize venue: lowercase, replace spaces with '-', remove non-alphanu
        normalized_venue = re.sub(r'[^a-z0-9]', '', venue.lower())[:15]
        # Simple hash: md5 of the event JSON string, first 6 chars
        event_str = json.dumps(event, sort_keys=True)
        event_hash = hashlib.md5(event_str.encode("utf-8")).hexdigest()[:6]
        filename = f"{date}_{event_hash}_{normalized_venue}.json"
        filepath = os.path.join(output_folder, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump([event], f, ensure_ascii=False, indent=2)
        logging.info(f"Wrote event to {filepath}")

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

def get_raw_events_from_files(file_paths: list[str]):
    if len(file_paths) == 1 and file_paths[0] == "-":
        # Read a single list of events from stdin
        data = json.load(sys.stdin)
        if not isinstance(data, list):
            raise ValueError("Input from stdin must be a JSON list of events.")
        yield from data
    else:
        for path in file_paths:
            with open(path) as json_file:
                data = json.load(json_file)
                yield from data

def get_events_from_files(file_paths: list[str]):
    for raw_event in get_raw_events_from_files(file_paths):
        date = datetime.datetime.strptime(raw_event["date"], "%Y-%m-%d").date()
        venue = raw_event["venue"]
        link = raw_event["link"]
        yield Event(date=date, venue=venue, link=link)

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
