import os
import math
from typing import Dict, Any, List, Optional
import pandas as pd

from Dataset.email_record import EmailRecord


class DatasetService:
    """Manages the in-memory email records loaded from CSV using pandas."""

    def __init__(self, csv_path: Optional[str] = None):
        if csv_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            csv_path = os.path.join(base_dir, "data", "data.csv")

        self.csv_path = csv_path
        self._records: List[EmailRecord] = []
        self._ids: set = set()
        self._is_loaded = False
        self.load_data()

    def load_data(self) -> None:
        """Load dataset from CSV using pandas and convert to EmailRecord objects."""
        if not os.path.exists(self.csv_path):
            self._records = []
            self._ids = set()
            self._is_loaded = True
            return

        # Read CSV with pandas, handling broken/bad lines safely
        df = pd.read_csv(self.csv_path, on_bad_lines="skip")
        
        # Clean nulls
        df = df.fillna("")

        raw_records = df.to_dict(orient="records")
        loaded_records: List[EmailRecord] = []
        id_set = set()

        for idx, row in enumerate(raw_records):
            rec_id = str(idx + 1)
            record = EmailRecord(
                record_id=rec_id,
                sender=row.get("sender", ""),
                subject=row.get("subject", ""),
                body=row.get("body", ""),
                label=row.get("label", 0),
                date=row.get("date", ""),
                receiver=row.get("receiver", ""),
                urls=row.get("urls", []),
            )
            loaded_records.append(record)
            id_set.add(rec_id)

        self._records = loaded_records
        self._ids = id_set
        self._is_loaded = True

    def get_total_count(self) -> int:
        return len(self._records)

    def get_paginated(
        self,
        page: int = 1,
        per_page: int = 20,
        return_all: bool = False,
    ) -> Dict[str, Any]:
        """
        Return paginated list of email records.
        If return_all is True, return all records without pagination.
        """
        total = len(self._records)

        if return_all:
            return {
                "success": True,
                "total": total,
                "page": 1,
                "per_page": total,
                "total_pages": 1,
                "data": [r.to_dict() for r in self._records],
            }

        # Validate pagination parameters
        page = max(1, page)
        per_page = max(1, min(per_page, 200))  # Cap per_page at 200 for client safety

        total_pages = math.ceil(total / per_page) if total > 0 else 1
        page = min(page, total_pages) if total_pages > 0 else 1

        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_records = self._records[start_idx:end_idx]

        return {
            "success": True,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "count": len(page_records),
            "data": [r.to_dict() for r in page_records],
        }

    def get_record_by_id(self, record_id: str) -> Optional[EmailRecord]:
        """Lookup a record by its unique ID."""
        for r in self._records:
            if r.id == str(record_id):
                return r
        return None


# Singleton instance
dataset_service = DatasetService()
