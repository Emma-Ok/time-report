# time-report

This is a simple but very useful script for people like me who forget to report their hours on DevOps or other reporting platforms. This script helps you open a console every hour where you can write down the activity you were doing, so you can keep a record of everything you do during the day.

## Features

- 🕐 **Hourly Prompts**: Automatically prompts you every hour to log your activities
- 📝 **Simple Console Interface**: Easy-to-use text-based input
- 📅 **Daily Log Files**: Saves all entries to dated log files (e.g., `time_report_2026-02-01.log`)
- ⏱️ **Timestamped Entries**: Each entry includes an exact timestamp
- 🚀 **Easy to Use**: Just run the script and it does the rest

## Requirements

- Python 3.6 or higher (no additional dependencies required)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/Emma-Ok/time-report.git
cd time-report
```

2. Make the script executable (optional, on Unix/Linux/Mac):
```bash
chmod +x time_report.py
```

## Usage

### Run Continuously (Recommended)
This mode will prompt you every hour to log your activities:
```bash
python time_report.py
```

The script will:
1. Prompt you immediately for your current activity
2. Wait for one hour
3. Prompt you again
4. Repeat until you stop it (Ctrl+C)

### Log a Single Entry
If you just want to log one activity and exit:
```bash
python time_report.py --once
```

### Display Help
To see all available options:
```bash
python time_report.py --help
```

## Example

When you run the script, you'll see:
```
============================================================
⏰ TIME REPORT - Hourly Check-in
============================================================
Current time: 2026-02-01 14:32:15

What have you been working on this hour?
(Enter your activity below, press Enter when done)
------------------------------------------------------------
> Implemented the time report script and tested functionality

✓ Activity logged successfully to time_report_2026-02-01.log

⏳ Waiting for next hour...
Next check-in at: 15:32
```

## Log File Format

Activities are saved to a daily log file with the format: `time_report_YYYY-MM-DD.log`

Example log file content:
```
[2026-02-01 14:32:15] Implemented the time report script and tested functionality
[2026-02-01 15:32:20] Code review and bug fixes for the authentication module
[2026-02-01 16:32:18] Team meeting and sprint planning
```

## Tips

- Keep the script running in a terminal window throughout your workday
- Be consistent with your entries to build an accurate work log
- Review your log files at the end of the day for time reporting
- Use clear, concise descriptions of your activities

## Stopping the Script

Press `Ctrl+C` to stop the script gracefully. Your logged activities will be saved.

## License

This project is open source and available for anyone to use and modify.
