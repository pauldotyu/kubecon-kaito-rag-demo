#!/usr/bin/env python3
"""
Download and parse KubeCon + CloudNativeCon 2025 schedule from ICS to JSON.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo
import requests


def download_ics(url: str) -> str:
    """Download ICS file from URL."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text


def parse_ics_datetime(dt_string: str) -> str:
    """Parse ICS datetime format and convert from UTC to Eastern Time."""
    if not dt_string:
        return ""

    # ICS format: YYYYMMDDTHHMMSSZ
    try:
        # Parse as UTC datetime
        dt_utc = datetime.strptime(dt_string, "%Y%m%dT%H%M%SZ")
        dt_utc = dt_utc.replace(tzinfo=ZoneInfo("UTC"))
        
        # Convert to Eastern Time (handles EST/EDT automatically)
        dt_eastern = dt_utc.astimezone(ZoneInfo("America/New_York"))
        
        return dt_eastern.isoformat()
    except ValueError:
        return dt_string


def unescape_ics_text(text: str) -> str:
    """Unescape ICS text (handle escaped commas, newlines, etc.)."""
    if not text:
        return ""

    # Replace escaped characters
    text = text.replace("\\,", ",")
    text = text.replace("\\;", ";")
    text = text.replace("\\n", "\n")
    text = text.replace("\\\\", "\\")

    return text.strip()


def parse_ics_to_json(ics_content: str) -> dict[str, Any]:
    """Parse ICS content to JSON structure."""
    lines = ics_content.split("\n")

    calendar_data = {"calendar": {"metadata": {}, "events": []}}

    current_event = None
    current_field = None

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # Parse calendar metadata
        if line.startswith("VERSION:"):
            calendar_data["calendar"]["metadata"]["version"] = line.split(":", 1)[1]
        elif line.startswith("X-WR-CALNAME:"):
            calendar_data["calendar"]["metadata"]["name"] = line.split(":", 1)[1]
        elif line.startswith("X-WR-CALDESC:"):
            calendar_data["calendar"]["metadata"]["description"] = line.split(":", 1)[1]
        elif line.startswith("METHOD:"):
            calendar_data["calendar"]["metadata"]["method"] = line.split(":", 1)[1]
        elif line.startswith("CALSCALE:"):
            calendar_data["calendar"]["metadata"]["calscale"] = line.split(":", 1)[1]
        elif line.startswith("PRODID:"):
            calendar_data["calendar"]["metadata"]["prodid"] = line.split(":", 1)[1]
        elif line.startswith("X-WR-TIMEZONE:"):
            calendar_data["calendar"]["metadata"]["timezone"] = line.split(":", 1)[1]

        # Parse events
        elif line == "BEGIN:VEVENT":
            current_event = {
                "uid": "",
                "dtstamp": "",
                "dtstart": "",
                "dtend": "",
                "summary": "",
                "description": "",
                "categories": [],
                "location": "",
                "sequence": 0,
                "url": "",
            }
            current_field = None

        elif line == "END:VEVENT" and current_event:
            # Clean up and add event
            current_event["description"] = unescape_ics_text(
                current_event["description"]
            )
            current_event["summary"] = unescape_ics_text(current_event["summary"])
            current_event["location"] = unescape_ics_text(current_event["location"])
            calendar_data["calendar"]["events"].append(current_event)
            current_event = None
            current_field = None

        elif current_event:
            # Handle multi-line fields (lines that start with space)
            if line.startswith(" ") and current_field:
                current_event[current_field] += line[1:]
            else:
                # Parse event fields
                if ":" in line:
                    field, value = line.split(":", 1)

                    if field == "UID":
                        current_event["uid"] = value
                        current_field = "uid"
                    elif field == "DTSTAMP":
                        current_event["dtstamp"] = parse_ics_datetime(value)
                        current_field = "dtstamp"
                    elif field == "DTSTART":
                        current_event["dtstart"] = parse_ics_datetime(value)
                        current_field = "dtstart"
                    elif field == "DTEND":
                        current_event["dtend"] = parse_ics_datetime(value)
                        current_field = "dtend"
                    elif field == "SUMMARY":
                        current_event["summary"] = value
                        current_field = "summary"
                    elif field == "DESCRIPTION":
                        current_event["description"] = value
                        current_field = "description"
                    elif field == "CATEGORIES":
                        current_event["categories"] = [
                            cat.strip() for cat in value.split(",")
                        ]
                        current_field = "categories"
                    elif field == "LOCATION":
                        current_event["location"] = value
                        current_field = "location"
                    elif field == "SEQUENCE":
                        current_event["sequence"] = int(value)
                        current_field = "sequence"
                    elif field == "URL":
                        current_event["url"] = value
                        current_field = "url"

    return calendar_data


def main():
    """Main function to download, parse, and save schedule."""
    ics_url = "https://kccncna2025.sched.com/all.ics"
    output_file = Path(__file__).parent / "output/schedule.json"

    # Try reading from local file before downloading
    ics_file = Path("all.ics")
    if ics_file.exists():
        print(f"Reading from {ics_file}...")
        ics_content = ics_file.read_text(encoding="utf-8")
    else:
        print(f"Downloading from {ics_url}...")
        ics_content = download_ics(ics_url)

    print("Parsing content...")
    calendar_data = parse_ics_to_json(ics_content)

    event_count = len(calendar_data["calendar"]["events"])
    print(f"Parsed {event_count} events")

    print(f"Saving to {output_file}...")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(calendar_data, f, indent=2, ensure_ascii=False)

    print("✓ Done!")
    print(f"  Events: {event_count}")
    print(f"  Output: {output_file}")


if __name__ == "__main__":
    main()
