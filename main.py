import pandas as pd
from src.constants import DATA_CSV


def main():
    try:
        count = int(input("Enter number of records to display: ").strip())
        df = pd.read_csv(DATA_CSV, nrows=count)

        for i, row in df.iterrows():
            print(f"Record {i + 1} ")
            print(f"Sender:  {row.get('sender')}")
            print(f"Subject: {row.get('subject')}")
            print(f"Label:   {row.get('label')}")
            body = " ".join(str(row.get('body', '')).split())
            print(f"Body:    {body[:150]}...")
            print("\n\n")

    except ValueError:
        print("Please enter a valid integer.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()