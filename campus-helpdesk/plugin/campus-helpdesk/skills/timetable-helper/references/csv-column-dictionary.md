# CSV Column Dictionary

This dictionary defines each column in `mock_timetable.csv`, its data type, valid values, and interpretation rules.

| Column Name | Data Type | Description | Valid Values & Format | Interpretation / Usage |
| :--- | :--- | :--- | :--- | :--- |
| `batch` | String | Academic cohort/section | E.g., `CS-A`, `CS-B` | Identifies which student group attends the lecture. Must match user batch. |
| `day` | String | Day of the academic week | `Monday`, `Tuesday`, `Wednesday`, `Thursday`, `Friday` | The day the class occurs. Academic sessions are not scheduled on weekends. |
| `start_time` | String | Class start timestamp | 24-hour format `HH:MM` (e.g. `09:00`, `11:15`, `13:00`, `14:00`) | Chronological sort key. Used to determine the start of a session. |
| `end_time` | String | Class end timestamp | 24-hour format `HH:MM` (e.g. `10:00`, `12:15`, `14:00`, `16:00`) | End of the class period. Gaps between end and next start denote breaks. |
| `subject_code`| String | Course registration code | Alphanumeric (e.g. `CS201`, `CS202`, `CS204`) | Primary academic catalog identifier. |
| `subject_name`| String | Full course title | Text (e.g. `Data Structures and Algorithms`, `Operating Systems`) | Descriptive course name presented in student responses. |
| `faculty` | String | Name of assigned instructor | E.g. `Prof. Raman`, `Dr. Sen`, `Dr. Verma`, `Prof. Nair` | Faculty member conducting the lecture or lab. |
| `room` | String | Designated physical space | E.g. `Room 101`, `Room 102`, `Lab 2` | Physical campus location where students must report. |
