#!/usr/bin/env python3
"""
timetable_lookup.py
Query utility for the Campus Helpdesk Timetable Helper skill.
Loads mock timetable data and provides deterministic filtering and lookup.
"""

import csv
import sys
from pathlib import Path
from typing import List, Dict, Optional

# Default dataset location relative to this script
DEFAULT_CSV_PATH = Path(__file__).resolve().parent.parent / "references" / "mock_timetable.csv"


def load_timetable(csv_path: Optional[Path] = None) -> List[Dict[str, str]]:
    path = csv_path or DEFAULT_CSV_PATH
    if not path.exists():
        raise FileNotFoundError(f"Timetable CSV file not found at: {path}")

    records = []
    with open(path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append({k.strip(): v.strip() for k, v in row.items()})
    return records


def query_timetable(
    records: List[Dict[str, str]],
    batch: Optional[str] = None,
    day: Optional[str] = None,
    subject: Optional[str] = None,
    faculty: Optional[str] = None,
    room: Optional[str] = None
) -> List[Dict[str, str]]:
    results = []
    for r in records:
        if batch and r.get("batch", "").lower() != batch.strip().lower():
            continue
        if day and r.get("day", "").lower() != day.strip().lower():
            continue
        if subject:
            sub_query = subject.strip().lower()
            code_match = sub_query in r.get("subject_code", "").lower()
            name_match = sub_query in r.get("subject_name", "").lower()
            if not (code_match or name_match):
                continue
        if faculty and faculty.strip().lower() not in r.get("faculty", "").lower():
            continue
        if room and room.strip().lower() != r.get("room", "").lower():
            continue
        results.append(r)

    # Sort results chronologically by start_time
    results.sort(key=lambda x: x.get("start_time", "00:00"))
    return results


def format_results(results: List[Dict[str, str]]) -> str:
    if not results:
        return "No matching timetable records found."

    lines = []
    lines.append(f"Found {len(results)} matching class(es):")
    lines.append("-" * 75)
    header = f"{'Batch':<8} {'Day':<10} {'Time':<15} {'Subject':<28} {'Room':<10} {'Faculty'}"
    lines.append(header)
    lines.append("-" * 75)

    for r in results:
        time_slot = f"{r.get('start_time')}-{r.get('end_time')}"
        subj = f"{r.get('subject_code')} ({r.get('subject_name')[:18]}...)" if len(r.get('subject_name', '')) > 20 else f"{r.get('subject_code')} {r.get('subject_name')}"
        lines.append(
            f"{r.get('batch', ''):<8} {r.get('day', ''):<10} {time_slot:<15} {subj:<28} {r.get('room', ''):<10} {r.get('faculty', '')}"
        )
    return "\n".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Query campus timetable mock dataset.")
    parser.add_argument("--batch", type=str, help="Batch code, e.g., CS-A, CS-B")
    parser.add_argument("--day", type=str, help="Day of week, e.g., Monday, Tuesday")
    parser.add_argument("--subject", type=str, help="Subject name or code, e.g., CS201 or Algorithms")
    parser.add_argument("--faculty", type=str, help="Faculty name, e.g., Raman")
    parser.add_argument("--room", type=str, help="Room/Lab name, e.g., 'Room 101'")

    args = parser.parse_args()

    try:
        data = load_timetable()
        matches = query_timetable(
            records=data,
            batch=args.batch,
            day=args.day,
            subject=args.subject,
            faculty=args.faculty,
            room=args.room
        )
        print(format_results(matches))
    except Exception as e:
        print(f"Error executing timetable lookup: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

