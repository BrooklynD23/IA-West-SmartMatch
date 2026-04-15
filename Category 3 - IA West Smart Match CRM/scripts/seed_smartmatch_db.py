"""Create and seed the persistent smartmatch SQLite database from real CSV/JSON sources.

Idempotent: if smartmatch.db already exists and has tables, the script exits
without modifying the database unless --force is passed.

Usage:
    python scripts/seed_smartmatch_db.py
    python scripts/seed_smartmatch_db.py --force
"""

from __future__ import annotations

import argparse
import csv
import json
import sqlite3
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SMARTMATCH_DB_PATH = PROJECT_ROOT / "data" / "smartmatch.db"
DATA_DIR = PROJECT_ROOT / "data"


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

def create_schema(connection: sqlite3.Connection) -> None:
    """Create all tables in the smartmatch database."""
    connection.executescript(
        """
        CREATE TABLE specialists (
            name TEXT,
            board_role TEXT,
            metro_region TEXT,
            company TEXT,
            title TEXT,
            expertise_tags TEXT,
            initials TEXT
        );

        CREATE TABLE cpp_events (
            "Event / Program" TEXT,
            Category TEXT,
            "Recurrence (typical)" TEXT,
            "Host / Unit" TEXT,
            "Volunteer Roles (fit)" TEXT,
            "Primary Audience" TEXT,
            "Public URL" TEXT,
            "Point(s) of Contact (published)" TEXT,
            "Contact Email / Phone (published)" TEXT
        );

        CREATE TABLE cpp_courses (
            instructor TEXT,
            course TEXT,
            section TEXT,
            title TEXT,
            days TEXT,
            start_time TEXT,
            end_time TEXT,
            enrl_cap TEXT,
            mode TEXT,
            guest_lecture_fit TEXT
        );

        CREATE TABLE pipeline (
            event_name TEXT,
            speaker_name TEXT,
            match_score TEXT,
            rank TEXT,
            stage TEXT,
            stage_order TEXT
        );

        CREATE TABLE event_calendar (
            "IA Event Date" TEXT,
            Region TEXT,
            "Nearby Universities" TEXT,
            "Suggested Lecture Window" TEXT,
            "Course Alignment" TEXT
        );

        CREATE TABLE poc_contacts (
            name TEXT,
            email TEXT,
            org TEXT,
            role TEXT,
            comm_history TEXT
        );

        CREATE TABLE calendar_events (
            event_id TEXT,
            event_name TEXT,
            event_date TEXT,
            region TEXT,
            nearby_universities TEXT,
            suggested_lecture_window TEXT,
            course_alignment TEXT,
            coverage_status TEXT,
            coverage_label TEXT,
            coverage_ratio REAL,
            assigned_volunteers TEXT,
            assignment_count INTEGER,
            open_slots INTEGER,
            status_color TEXT
        );

        CREATE TABLE calendar_assignments (
            assignment_id TEXT,
            event_id TEXT,
            event_name TEXT,
            event_date TEXT,
            calendar_event_date TEXT,
            region TEXT,
            calendar_region TEXT,
            volunteer_name TEXT,
            speaker_name TEXT,
            volunteer_title TEXT,
            volunteer_company TEXT,
            speaker_region TEXT,
            stage TEXT,
            stage_order INTEGER,
            match_score REAL,
            rank INTEGER,
            travel_burden REAL,
            event_cadence REAL,
            recent_assignment_count INTEGER,
            days_since_last_assignment INTEGER,
            volunteer_fatigue REAL,
            recovery_status TEXT,
            recovery_label TEXT,
            coverage_status TEXT,
            coverage_label TEXT,
            status_color TEXT,
            status_tone TEXT,
            coverage_ratio REAL
        );

        CREATE TABLE qr_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payload_json TEXT NOT NULL
        );

        CREATE TABLE feedback_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payload_json TEXT NOT NULL
        );

        CREATE TABLE web_crawler_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            title TEXT,
            description TEXT,
            school_name TEXT,
            crawled_at TEXT NOT NULL,
            source TEXT NOT NULL,
            status TEXT NOT NULL
        );
        """
    )


# ---------------------------------------------------------------------------
# CSV / JSON seeders
# ---------------------------------------------------------------------------

def _get_initials(name: str) -> str:
    """Return uppercase initials derived from a full name."""
    parts = name.split()
    return "".join(part[0].upper() for part in parts if part)


def seed_from_csv(connection: sqlite3.Connection) -> None:
    """Read real CSV and JSON data files and insert rows into the database."""

    # --- specialists -------------------------------------------------------
    specialists_path = DATA_DIR / "data_speaker_profiles.csv"
    with specialists_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        specialists = [
            {
                "name": row.get("Name", ""),
                "board_role": row.get("Board Role", ""),
                "metro_region": row.get("Metro Region", ""),
                "company": row.get("Company", ""),
                "title": row.get("Title", ""),
                "expertise_tags": row.get("Expertise Tags", ""),
                "initials": _get_initials(row.get("Name", "")),
            }
            for row in reader
        ]
    connection.executemany(
        """
        INSERT INTO specialists (
            name, board_role, metro_region, company, title, expertise_tags, initials
        ) VALUES (
            :name, :board_role, :metro_region, :company, :title, :expertise_tags, :initials
        )
        """,
        specialists,
    )
    print(f"  Inserted {len(specialists)} specialist rows from CSV.")

    # --- cpp_events --------------------------------------------------------
    cpp_events_path = DATA_DIR / "data_cpp_events_contacts.csv"
    with cpp_events_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        cpp_events = list(reader)
    connection.executemany(
        """
        INSERT INTO cpp_events (
            "Event / Program", Category, "Recurrence (typical)", "Host / Unit",
            "Volunteer Roles (fit)", "Primary Audience", "Public URL",
            "Point(s) of Contact (published)", "Contact Email / Phone (published)"
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        """,
        [
            (
                row.get("Event / Program", ""),
                row.get("Category", ""),
                row.get("Recurrence (typical)", ""),
                row.get("Host / Unit", ""),
                row.get("Volunteer Roles (fit)", ""),
                row.get("Primary Audience", ""),
                row.get("Public URL", ""),
                row.get("Point(s) of Contact (published)", ""),
                row.get("Contact Email / Phone (published)", ""),
            )
            for row in cpp_events
        ],
    )
    print(f"  Inserted {len(cpp_events)} cpp_events rows from CSV.")

    # --- cpp_courses -------------------------------------------------------
    cpp_courses_path = DATA_DIR / "data_cpp_course_schedule.csv"
    with cpp_courses_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        cpp_courses = [
            {
                "instructor": row.get("Instructor", ""),
                "course": row.get("Course", ""),
                "section": row.get("Section", ""),
                "title": row.get("Title", ""),
                "days": row.get("Days", ""),
                "start_time": row.get("Start Time", ""),
                "end_time": row.get("End Time", ""),
                "enrl_cap": row.get("Enrl Cap", ""),
                "mode": row.get("Mode", ""),
                "guest_lecture_fit": row.get("Guest Lecture Fit", ""),
            }
            for row in reader
        ]
    connection.executemany(
        """
        INSERT INTO cpp_courses (
            instructor, course, section, title, days, start_time, end_time,
            enrl_cap, mode, guest_lecture_fit
        ) VALUES (
            :instructor, :course, :section, :title, :days, :start_time, :end_time,
            :enrl_cap, :mode, :guest_lecture_fit
        )
        """,
        cpp_courses,
    )
    print(f"  Inserted {len(cpp_courses)} cpp_courses rows from CSV.")

    # --- event_calendar ----------------------------------------------------
    event_calendar_path = DATA_DIR / "data_event_calendar.csv"
    with event_calendar_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        event_calendar = list(reader)
    connection.executemany(
        """
        INSERT INTO event_calendar (
            "IA Event Date", Region, "Nearby Universities",
            "Suggested Lecture Window", "Course Alignment"
        ) VALUES (
            ?, ?, ?, ?, ?
        )
        """,
        [
            (
                row.get("IA Event Date", ""),
                row.get("Region", ""),
                row.get("Nearby Universities", ""),
                row.get("Suggested Lecture Window", ""),
                row.get("Course Alignment", ""),
            )
            for row in event_calendar
        ],
    )
    print(f"  Inserted {len(event_calendar)} event_calendar rows from CSV.")

    # --- pipeline ----------------------------------------------------------
    pipeline_path = DATA_DIR / "pipeline_sample_data.csv"
    with pipeline_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        pipeline_rows = list(reader)
    connection.executemany(
        """
        INSERT INTO pipeline (
            event_name, speaker_name, match_score, rank, stage, stage_order
        ) VALUES (
            :event_name, :speaker_name, :match_score, :rank, :stage, :stage_order
        )
        """,
        pipeline_rows,
    )
    print(f"  Inserted {len(pipeline_rows)} pipeline rows from CSV.")

    # --- poc_contacts ------------------------------------------------------
    poc_contacts_path = DATA_DIR / "poc_contacts.json"
    with poc_contacts_path.open(encoding="utf-8") as fh:
        poc_contacts = json.load(fh)
    connection.executemany(
        """
        INSERT INTO poc_contacts (name, email, org, role, comm_history)
        VALUES (:name, :email, :org, :role, :comm_history)
        """,
        [
            {
                "name": contact.get("name", ""),
                "email": contact.get("email", ""),
                "org": contact.get("org", ""),
                "role": contact.get("role", ""),
                "comm_history": json.dumps(contact.get("comm_history", [])),
            }
            for contact in poc_contacts
        ],
    )
    print(f"  Inserted {len(poc_contacts)} poc_contacts rows from JSON.")


def _seed_constant_tables(connection: sqlite3.Connection) -> None:
    """Seed tables that have no CSV source using constants from seed_demo_db."""
    # Import here to avoid circular issues and to keep constants in one place.
    sys.path.insert(0, str(PROJECT_ROOT))
    from scripts.seed_demo_db import (  # type: ignore[import]
        CALENDAR_ASSIGNMENTS,
        CALENDAR_EVENTS,
        FEEDBACK_STATS,
        QR_STATS,
    )

    # calendar_events
    connection.executemany(
        """
        INSERT INTO calendar_events (
            event_id, event_name, event_date, region, nearby_universities,
            suggested_lecture_window, course_alignment, coverage_status,
            coverage_label, coverage_ratio, assigned_volunteers,
            assignment_count, open_slots, status_color
        ) VALUES (
            :event_id, :event_name, :event_date, :region, :nearby_universities,
            :suggested_lecture_window, :course_alignment, :coverage_status,
            :coverage_label, :coverage_ratio, :assigned_volunteers,
            :assignment_count, :open_slots, :status_color
        )
        """,
        [
            {
                **record,
                "nearby_universities": json.dumps(record["nearby_universities"]),
                "assigned_volunteers": json.dumps(record["assigned_volunteers"]),
            }
            for record in CALENDAR_EVENTS
        ],
    )
    print(f"  Inserted {len(CALENDAR_EVENTS)} calendar_events rows from constants.")

    # calendar_assignments
    connection.executemany(
        """
        INSERT INTO calendar_assignments (
            assignment_id, event_id, event_name, event_date, calendar_event_date,
            region, calendar_region, volunteer_name, speaker_name, volunteer_title,
            volunteer_company, speaker_region, stage, stage_order, match_score, rank,
            travel_burden, event_cadence, recent_assignment_count,
            days_since_last_assignment, volunteer_fatigue, recovery_status,
            recovery_label, coverage_status, coverage_label, status_color,
            status_tone, coverage_ratio
        ) VALUES (
            :assignment_id, :event_id, :event_name, :event_date, :calendar_event_date,
            :region, :calendar_region, :volunteer_name, :speaker_name, :volunteer_title,
            :volunteer_company, :speaker_region, :stage, :stage_order, :match_score, :rank,
            :travel_burden, :event_cadence, :recent_assignment_count,
            :days_since_last_assignment, :volunteer_fatigue, :recovery_status,
            :recovery_label, :coverage_status, :coverage_label, :status_color,
            :status_tone, :coverage_ratio
        )
        """,
        CALENDAR_ASSIGNMENTS,
    )
    print(f"  Inserted {len(CALENDAR_ASSIGNMENTS)} calendar_assignments rows from constants.")

    # qr_stats
    connection.execute(
        "INSERT INTO qr_stats (payload_json) VALUES (?)",
        (json.dumps(QR_STATS, sort_keys=True),),
    )
    print("  Inserted 1 qr_stats row from constants.")

    # feedback_stats
    connection.execute(
        "INSERT INTO feedback_stats (payload_json) VALUES (?)",
        (json.dumps(FEEDBACK_STATS, sort_keys=True),),
    )
    print("  Inserted 1 feedback_stats row from constants.")

    # web_crawler_events (demo seed so UI shows URLs before first crawl)
    crawler_seed = [
        (
            "https://www.cpp.edu/cba/digital-innovation/what-we-do/ai-hackathon.shtml",
            "www.cpp.edu",
            "Seed URL: https://www.cpp.edu/cba/digital-innovation/what-we-do/ai-hackathon.shtml",
            "www.cpp.edu",
            "2026-04-14T00:00:00Z",
            "seed",
            "found",
        ),
        (
            "https://www.cpp.edu/cba/ai-hackathon/index.shtml",
            "www.cpp.edu",
            "Seed URL: https://www.cpp.edu/cba/ai-hackathon/index.shtml",
            "www.cpp.edu",
            "2026-04-14T00:00:00Z",
            "seed",
            "found",
        ),
        (
            "https://www.insightsassociation.org/ai-hackathon",
            "www.insightsassociation.org",
            "Seed URL: https://www.insightsassociation.org/ai-hackathon",
            "www.insightsassociation.org",
            "2026-04-14T00:00:00Z",
            "seed",
            "found",
        ),
        (
            "https://www.insightsassociation.org/itc",
            "www.insightsassociation.org",
            "Seed URL: https://www.insightsassociation.org/itc",
            "www.insightsassociation.org",
            "2026-04-14T00:00:00Z",
            "seed",
            "found",
        ),
        (
            "https://www.insightsassociation.org/ia-west-summit",
            "www.insightsassociation.org",
            "Seed URL: https://www.insightsassociation.org/ia-west-summit",
            "www.insightsassociation.org",
            "2026-04-14T00:00:00Z",
            "seed",
            "found",
        ),
    ]
    connection.executemany(
        """
        INSERT INTO web_crawler_events (
            url, title, description, school_name, crawled_at, source, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        crawler_seed,
    )
    print(f"  Inserted {len(crawler_seed)} web_crawler_events rows from constants.")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main(*, force: bool = False) -> None:
    """Seed smartmatch.db from real CSV/JSON data files.

    If the database already exists and has tables, this function exits early
    unless force=True is passed.
    """
    SMARTMATCH_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    if SMARTMATCH_DB_PATH.exists() and not force:
        # Check if already seeded
        connection = sqlite3.connect(str(SMARTMATCH_DB_PATH))
        try:
            row = connection.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
            ).fetchone()
            count = row[0] if row else 0
        finally:
            connection.close()

        if count > 0:
            print(
                f"smartmatch.db already seeded ({count} tables). Use --force to reseed."
            )
            return

    if force and SMARTMATCH_DB_PATH.exists():
        SMARTMATCH_DB_PATH.unlink()
        print("Removed existing smartmatch.db (--force mode).")

    print(f"Creating smartmatch.db at: {SMARTMATCH_DB_PATH}")
    connection = sqlite3.connect(str(SMARTMATCH_DB_PATH))
    try:
        create_schema(connection)
        print("Schema created.")
        seed_from_csv(connection)
        _seed_constant_tables(connection)
        connection.commit()
    except Exception:
        connection.close()
        # Remove partial DB to avoid corrupted state
        if SMARTMATCH_DB_PATH.exists():
            SMARTMATCH_DB_PATH.unlink()
        raise
    finally:
        connection.close()

    print(f"smartmatch.db seeded successfully: {SMARTMATCH_DB_PATH}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Seed the smartmatch persistent database from real CSV/JSON files."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Delete and re-create smartmatch.db even if it already exists.",
    )
    args = parser.parse_args()
    main(force=args.force)
