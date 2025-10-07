#!/usr/bin/env python3
"""
Format KubeCon schedule JSON into document format for indexing.
"""

import json
import re
import unicodedata
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


# Constants
COMPANY_SUFFIXES = frozenset(
    {
        "Inc.",
        "Inc",
        "LLC",
        "LLC.",
        "Ltd",
        "Ltd.",
        "Corp",
        "Corp.",
        "Co.",
        "Co",
        "LP",
        "LP.",
        "LLP",
        "LLP.",
        "PLC",
        "PLC.",
    }
)

EXCLUDED_CATEGORIES = frozenset(
    {
        "REGISTRATION",
        "CNCF-HOSTED CO-LOCATED EVENTS",
        "SPONSOR-HOSTED CO-LOCATED EVENT",
        "PROJECT OPPORTUNITIES",
    }
)


# Data classes for type safety
@dataclass
class Location:
    """Structured location data."""

    building: str | None = None
    level: str | None = None
    room: str | None = None

    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in asdict(self).items() if v is not None}

    def to_text(self) -> str:
        """Convert to human-readable text."""
        parts = []
        if self.building:
            parts.append(f"Building {self.building}")
        if self.level:
            parts.append(f"Level {self.level}")
        if self.room:
            parts.append(self.room)
        return " | ".join(parts)


@dataclass
class Speaker:
    """Structured speaker data."""

    name: str
    title: str | None = None
    company: str | None = None

    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in asdict(self).items() if v is not None}

    def to_text(self) -> str:
        """Convert to human-readable text."""
        parts = [self.name]
        if self.title:
            parts.append(self.title)
        if self.company:
            parts.append(f"from {self.company}")
        return " ".join(parts)


def to_ascii(text: str) -> str:
    """
    Convert text to ASCII, removing or replacing non-ASCII characters.

    Args:
        text: Input text that may contain non-ASCII characters

    Returns:
        ASCII-only version of the text
    """
    if not text:
        return ""

    # Normalize unicode to closest ASCII equivalents
    normalized = unicodedata.normalize("NFKD", text)
    return normalized.encode("ascii", "ignore").decode("ascii")


def parse_location(location: str) -> Location | None:
    """
    Parse location string into structured components.

    Handles format: "Building B | Level 4 | B406b-407, Atlanta, GA, USA"

    Args:
        location: Raw location string

    Returns:
        Location object or None if parsing fails
    """
    if not location:
        return None

    # Remove city/state suffix
    location = re.split(r",\s*Atlanta", location)[0].strip()

    # Parse pipe-separated components
    parts = [part.strip() for part in location.split("|")]

    loc = Location()
    for part in parts:
        if part.lower().startswith("building "):
            loc.building = part[9:].strip()  # Remove "Building "
        elif part.lower().startswith("level "):
            loc.level = part[6:].strip()  # Remove "Level "
        elif part:
            loc.room = part

    return loc if any([loc.building, loc.level, loc.room]) else None


def normalize_company_name(parts: list[str], start_idx: int) -> str:
    """
    Normalize company name, handling suffixes like "Inc."

    Args:
        parts: List of comma-separated parts
        start_idx: Starting index for company name

    Returns:
        Normalized company name
    """
    if start_idx >= len(parts):
        return ""

    company_parts = parts[start_idx:]

    # If last part is a suffix, join last two parts
    if len(company_parts) >= 2 and company_parts[-1] in COMPANY_SUFFIXES:
        return f"{company_parts[-2]}, {company_parts[-1]}"

    return company_parts[-1] if company_parts else ""


def parse_speaker_entry(entry: str) -> Speaker | None:
    """
    Parse a single speaker entry.

    Handles formats:
    - "Name, Company"
    - "Name, Title, Company"
    - "Name, Company, Inc."

    Args:
        entry: Speaker string

    Returns:
        Speaker object or None if parsing fails
    """
    entry = entry.strip()
    if not entry:
        return None

    # No commas = just a name
    if "," not in entry:
        return Speaker(name=entry)

    parts = [p.strip() for p in entry.split(",")]

    if len(parts) == 2:
        # "Name, Company"
        return Speaker(name=parts[0], company=parts[1])

    # 3+ parts: check for company suffix
    if parts[-1] in COMPANY_SUFFIXES:
        # Company includes suffix: "Name, [Title,] Company, Inc."
        company = f"{parts[-2]}, {parts[-1]}"
        name = parts[0]
        title = ", ".join(parts[1:-2]) if len(parts) > 3 else None
        return Speaker(name=name, title=title, company=company)

    # No suffix: "Name, Title, Company" or "Name, Title1, Title2, Company"
    return Speaker(
        name=parts[0],
        title=", ".join(parts[1:-1]) if len(parts) > 2 else None,
        company=parts[-1],
    )


def extract_speakers(summary: str) -> list[Speaker]:
    """
    Extract speakers from event summary.

    Uses a simplified approach:
    1. Split on " - " to get speaker section
    2. Split on ";" for different company groups
    3. Use "&" as speaker separator, handling shared companies
    4. Parse individual entries

    Args:
        summary: Event summary string

    Returns:
        List of Speaker objects
    """
    if not summary or " - " not in summary:
        return []

    # Extract speaker section after the dash
    speaker_section = summary.split(" - ", 1)[1].strip()

    # Handle semicolon-separated groups
    if ";" in speaker_section:
        speakers = []
        for group in speaker_section.split(";"):
            speakers.extend(_parse_speaker_group(group.strip()))
        return speakers

    return _parse_speaker_group(speaker_section)


def _parse_speaker_group(group: str) -> list[Speaker]:
    """
    Parse a group of speakers (no semicolons).

    Handles:
    - Multiple speakers with shared company: "Name1 & Name2, Company"
    - Multiple speakers with separate details: "Name1, Co1 & Name2, Co2"

    Args:
        group: Speaker group string

    Returns:
        List of Speaker objects
    """
    # Split by "&"
    entries = [e.strip() for e in group.split(" & ")]

    # Check if this is a shared company pattern
    # Heuristic: If last entry has comma(s) and others don't, it's shared
    if len(entries) > 1:
        last_has_comma = "," in entries[-1]
        others_have_commas = any("," in e for e in entries[:-1])

        # Shared company: "Name1 & Name2 & Name3, Company"
        if last_has_comma and not others_have_commas:
            company = normalize_company_name(entries[-1].split(","), 1)
            names = entries[:-1] + [entries[-1].split(",")[0].strip()]
            return [Speaker(name=name, company=company) for name in names]

    # Parse each entry individually
    speakers = []
    for entry in entries:
        speaker = parse_speaker_entry(entry)
        if speaker:
            speakers.append(speaker)

    return speakers


def format_event_to_document(event: dict[str, Any]) -> dict[str, Any]:
    """
    Transform a single event into document format.

    Args:
        event: Event object from schedule.json

    Returns:
        Document object with text and metadata
    """
    summary = to_ascii(event.get("summary", ""))

    # Extract title (before " - ")
    title = summary.split(" - ")[0].strip() if " - " in summary else summary

    # Start with description as main text
    description = to_ascii(event.get("description", ""))

    # Parse structured data
    speakers = extract_speakers(summary)
    location = parse_location(event.get("location", ""))
    categories = [to_ascii(cat) for cat in event.get("categories", [])]

    # Build metadata
    metadata = {
        "title": title,
        "description": description,
        "url": event.get("url", ""),
        "uid": event.get("uid", ""),
        "start": event.get("dtstart", ""),
        "end": event.get("dtend", ""),
        "categories": categories,
    }

    # Add optional structured data
    if location:
        metadata["location"] = location.to_dict()
    if speakers:
        metadata["speakers"] = [s.to_dict() for s in speakers]

    # Enhance description with searchable text
    text_parts = [description] if description else []

    if speakers:
        speaker_text = "Speakers: " + ", ".join(s.to_text() for s in speakers) + "."
        text_parts.append(speaker_text)

    if location:
        text_parts.append(f"Location: {location.to_text()}.")

    if categories:
        text_parts.append(f"Categories: {', '.join(categories)}.")

    return {"text": " ".join(text_parts), "metadata": metadata}


def format_schedule_for_indexing(
    schedule_file: Path, output_file: Path, index_name: str = "schedule_index"
) -> dict[str, Any]:
    """
    Read schedule.json and format it for document indexing.

    Args:
        schedule_file: Path to input schedule.json
        output_file: Path to output formatted JSON
        index_name: Name of the index

    Returns:
        Formatted document structure
    """
    # Read schedule data
    with open(schedule_file, "r", encoding="utf-8") as f:
        schedule_data = json.load(f)

    events = schedule_data.get("calendar", {}).get("events", [])

    # Filter out excluded categories
    session_events = [
        event
        for event in events
        if not any(cat in EXCLUDED_CATEGORIES for cat in event.get("categories", []))
    ]

    # Transform events into documents
    documents = [format_event_to_document(event) for event in session_events]

    # Create output structure
    output_data = {"index_name": index_name, "documents": documents}

    # Write to output file
    with open(output_file, "w", encoding="ascii") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=True)

    return output_data


def main():
    """Main function to format schedule data."""
    schedule_file = Path(__file__).parent / "output/schedule.json"
    output_file = Path(__file__).parent / "output/schedule_index.json"
    index_name = "schedule_index"

    if not schedule_file.exists():
        print(f"❌ Error: {schedule_file} not found")
        print("Run parse_schedule.py first to generate schedule.json")
        return

    print(f"Reading schedule from {schedule_file}...")
    result = format_schedule_for_indexing(schedule_file, output_file, index_name)

    document_count = len(result["documents"])

    print(f"✓ Formatted {document_count} events into documents")
    print(f"✓ Saved to {output_file}")

    # Show sample document
    if document_count > 0:
        print("\nSample document:")
        print(json.dumps(result["documents"][0], indent=2))


if __name__ == "__main__":
    main()
