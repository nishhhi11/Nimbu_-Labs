---
name: timetable
description: Quick lookup for campus class schedules, lecture rooms, and timings by batch and day.
---

# Timetable Command

Execute timetable lookup for student schedules.

Usage:
```text
/timetable <batch> <day>
```

Example:
```text
/timetable CS-A Monday
```

When invoked:
1. Parse the requested batch and day from arguments.
2. If arguments are missing, prompt the user for their batch and day.
3. Query the timetable data via the `timetable-helper` skill or `timetable_lookup.py` script.
4. Output the schedule chronologically.

