#!/usr/bin/env python3
"""
Time Report Script
A simple script that prompts you every hour to log your activities.
"""

import time
import datetime
import os
import sys


def get_log_filename():
    """Generate log filename based on current date."""
    today = datetime.date.today()
    return f"time_report_{today.strftime('%Y-%m-%d')}.log"


def log_activity(activity, log_file):
    """Save the activity to the log file with timestamp."""
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {activity}\n")
    print(f"✓ Activity logged successfully to {log_file}")


def prompt_for_activity():
    """Prompt user to enter their current activity."""
    print("\n" + "="*60)
    print("⏰ TIME REPORT - Hourly Check-in")
    print("="*60)
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"Current time: {timestamp}")
    print("\nWhat have you been working on this hour?")
    print("(Enter your activity below, press Enter when done)")
    print("-"*60)
    
    try:
        activity = input("> ").strip()
        if activity:
            return activity
        else:
            print("⚠ No activity entered. Skipping this entry.")
            return None
    except (KeyboardInterrupt, EOFError):
        print("\n⚠ Input cancelled.")
        return None


def run_continuous():
    """Run the time reporter continuously, prompting every hour."""
    print("="*60)
    print("TIME REPORT SCRIPT STARTED")
    print("="*60)
    print("This script will prompt you every hour to log your activities.")
    print("Press Ctrl+C to stop the script.")
    print("="*60)
    
    # Prompt immediately on start
    log_file = get_log_filename()
    print(f"\nLog file for today: {log_file}\n")
    
    activity = prompt_for_activity()
    if activity:
        log_activity(activity, log_file)
    
    try:
        while True:
            # Wait for 1 hour (3600 seconds)
            print("\n⏳ Waiting for next hour...")
            print(f"Next check-in at: {(datetime.datetime.now() + datetime.timedelta(hours=1)).strftime('%H:%M')}")
            time.sleep(3600)
            
            # Update log file in case date changed
            log_file = get_log_filename()
            
            activity = prompt_for_activity()
            if activity:
                log_activity(activity, log_file)
    except KeyboardInterrupt:
        print("\n\n" + "="*60)
        print("TIME REPORT SCRIPT STOPPED")
        print("="*60)
        print("Your activities have been saved. Have a great day!")
        sys.exit(0)


def run_single_entry():
    """Run a single entry mode for testing or manual logging."""
    log_file = get_log_filename()
    print(f"Log file: {log_file}\n")
    
    activity = prompt_for_activity()
    if activity:
        log_activity(activity, log_file)
        return True
    return False


def display_help():
    """Display usage information."""
    help_text = """
Time Report Script - Usage
===========================

This script helps you track your hourly activities.

Usage:
    python time_report.py [OPTIONS]

Options:
    (no options)  - Run continuously, prompting every hour
    --once        - Log a single entry and exit
    --help        - Display this help message

Examples:
    python time_report.py              # Run continuously
    python time_report.py --once       # Log one entry
    python time_report.py --help       # Show help

Log files are saved as: time_report_YYYY-MM-DD.log
"""
    print(help_text)


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "--help" or arg == "-h":
            display_help()
        elif arg == "--once":
            run_single_entry()
        else:
            print(f"Unknown option: {arg}")
            print("Use --help for usage information")
            sys.exit(1)
    else:
        run_continuous()


if __name__ == "__main__":
    main()
