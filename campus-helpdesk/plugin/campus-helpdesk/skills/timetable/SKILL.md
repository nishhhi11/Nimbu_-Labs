---
name: timetable
description: Provides quick access to campus timetables, class schedules, rooms, and lecture timings via the /timetable slash command.
---

# Timetable Slash Command

This skill enables the `/timetable` slash command in Antigravity for student schedule lookups.

## Usage
Trigger directly in chat via:
```text
/timetable
```
Or with specific batch and day arguments:
```text
/timetable CS-A Monday
```

## Behavior
1. Parses requested batch and day parameters.
2. If parameters are omitted, asks the student for their batch (`CS-A` or `CS-B`) and weekday.
3. Retrieves class schedules strictly from `data/timetable.csv`.
4. Outputs timetable results sorted chronologically.

