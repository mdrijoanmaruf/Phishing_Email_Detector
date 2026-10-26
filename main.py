"""
main.py
Entry point for PhishGuard project.
Currently prompts user for number of records and displays them from the CSV file.
"""

import os
import sys
import pandas as pd
from src.constants import DATA_CSV


def show_data():
    """Prompt the user for the number of records to display from the dataset."""
    if not os.path.exists(DATA_CSV):
        print(f"Error: Dataset file not found at '{DATA_CSV}'.")
        return

    while True:
        try:
            user_input = input("How many records would you like to display? (or 'q' to quit): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            return

        if user_input.lower() in ("q", "quit", "exit"):
            print("Exiting.")
            return

        if not user_input.isdigit() or int(user_input) <= 0:
            print("Please enter a valid positive integer (e.g., 5).")
            continue

        num_records = int(user_input)
        break

    try:
        print(f"\nLoading {num_records} record(s) from '{DATA_CSV}'...\n")
        # Load only the requested number of rows for optimal performance
        df = pd.read_csv(DATA_CSV, nrows=num_records)

        if df.empty:
            print("The CSV file is empty.")
            return

        for idx, row in df.iterrows():
            print("=" * 80)
            print(f"Record #{idx + 1}")
            print(f"  Sender:   {row.get('sender', 'N/A')}")
            print(f"  Receiver: {row.get('receiver', 'N/A')}")
            print(f"  Date:     {row.get('date', 'N/A')}")
            print(f"  Subject:  {row.get('subject', 'N/A')}")
            
            label_val = row.get("label", "N/A")
            if label_val == 1:
                label_str = "1 (PHISHING)"
            elif label_val == 0:
                label_str = "0 (SAFE)"
            else:
                label_str = str(label_val)
            print(f"  Label:    {label_str}")
            print(f"  URLs:     {row.get('urls', 'N/A')}")
            
            body = str(row.get("body", "")).strip()
            # Show a neat preview of the body
            preview = body[:300] + ("..." if len(body) > 300 else "")
            print(f"  Body Preview:\n    {preview.replace(chr(10), chr(10) + '    ')}")

        print("=" * 80)
        print(f"\nSuccessfully displayed {len(df)} record(s).\n")

    except Exception as e:
        print(f"Error reading dataset: {e}")


if __name__ == "__main__":
    show_data()