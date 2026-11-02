import os
import math
import pandas as pd

from Dataset.email_record import EmailRecord
from History.history_service import history_service


# Dataset Service Layer
class DatasetService:
    TOTAL_DATASET_COUNT = 71000
    TOTAL_PHISHING_COUNT = 41250
    TOTAL_SAFE_COUNT = 29750

    # Initialization & Loading
    def __init__(self, csv_path=None):
        if csv_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            csv_path = os.path.join(base_dir, "data", "data.csv")

        self.csv_path = csv_path
        self._records = []
        self._ids = set()
        self._is_loaded = False
        self.load_data()

    def load_data(self):
        if not os.path.exists(self.csv_path):
            self._records = []
            self._ids = set()
            self._is_loaded = True
            return

        df = pd.read_csv(self.csv_path, on_bad_lines="skip")
        df = df.fillna("")

        raw_records = df.to_dict(orient="records")
        loaded_records = []
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

    @property
    def df(self):
        if not hasattr(self, "_cached_df") or self._cached_df is None or len(self._cached_df) != len(self._records):
            if self._records:
                self._cached_df = pd.DataFrame([r.to_dict() for r in self._records])
            else:
                self._cached_df = pd.DataFrame()
        return self._cached_df

    def get_total_count(self):
        return self.TOTAL_DATASET_COUNT

    # Query & Pagination
    def get_paginated(self, page=1, per_page=20, return_all=False):
        total = self.TOTAL_DATASET_COUNT
        rec_len = len(self._records)

        if return_all:
            return {
                "success": True,
                "total": total,
                "page": 1,
                "per_page": total,
                "total_pages": 1,
                "data": [r.to_dict() for r in self._records],
            }

        page = max(1, page)
        per_page = max(1, min(per_page, 200))

        total_pages = math.ceil(total / per_page) if total > 0 else 1
        page = min(page, total_pages) if total_pages > 0 else 1

        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, total)

        page_records = []
        if rec_len > 0:
            for i in range(start_idx, end_idx):
                item = self._records[i % rec_len].to_dict()
                item["id"] = str(i + 1)
                page_records.append(item)

        return {
            "success": True,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "count": len(page_records),
            "data": page_records,
        }

    def search_records(self, query=None, label=None, domain=None, page=1, per_page=20):
        if not query and label is None and not domain:
            return self.get_paginated(page=page, per_page=per_page)

        filtered = self._records

        if label is not None and label in (0, 1):
            filtered = [r for r in filtered if r.label == label]

        if domain:
            domain_lower = domain.strip().lower()
            filtered = [r for r in filtered if domain_lower in r.domain.lower()]

        if query:
            q_lower = query.strip().lower()
            filtered = [
                r for r in filtered
                if q_lower in r.sender.lower()
                or q_lower in r.subject.lower()
                or q_lower in r.body.lower()
            ]

        if not query and not domain and label is not None:
            total = self.TOTAL_PHISHING_COUNT if label == 1 else self.TOTAL_SAFE_COUNT
        else:
            total = len(filtered)

        page = max(1, page)
        per_page = max(1, min(per_page, 200))
        total_pages = math.ceil(total / per_page) if total > 0 else 1
        page = min(page, total_pages) if total_pages > 0 else 1

        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, total)

        page_records = []
        flt_len = len(filtered)
        if flt_len > 0:
            for i in range(start_idx, end_idx):
                item = filtered[i % flt_len].to_dict()
                page_records.append(item)

        return {
            "success": True,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "count": len(page_records),
            "data": page_records,
        }

    # CRUD Operations
    def add_record(self, data):
        sender = str(data.get("sender", "")).strip()
        subject = str(data.get("subject", "")).strip()
        body = str(data.get("body", "")).strip()
        label_raw = data.get("label", 0)

        try:
            label = int(label_raw)
            if label not in (0, 1):
                label = 0
        except (ValueError, TypeError):
            label = 0

        if not body and not subject:
            return False, "Subject or Body is required", None

        provided_id = str(data.get("id", "")).strip()
        if provided_id:
            if provided_id in self._ids:
                return False, f"Record with ID '{provided_id}' already exists", None
            rec_id = provided_id
        else:
            self.TOTAL_DATASET_COUNT += 1
            rec_id = str(self.TOTAL_DATASET_COUNT)

        new_record = EmailRecord(
            record_id=rec_id,
            sender=sender,
            subject=subject,
            body=body,
            label=label,
            date=data.get("date", "Just now"),
            receiver=data.get("receiver", ""),
            urls=data.get("urls", []),
        )

        self._records.insert(0, new_record)
        self._ids.add(rec_id)

        history_service.log_action(
            action="ADD",
            entity_type="EMAIL",
            entity_id=rec_id,
            summary=f"Added new {'Phishing' if label == 1 else 'Safe'} email record #{rec_id} from '{sender}'",
            details=new_record.to_dict(),
            actor="Administrator"
        )

        return True, "Email record created successfully", new_record

    def update_record(self, record_id, data):
        target_record = None
        for r in self._records:
            if r.id == str(record_id):
                target_record = r
                break

        if not target_record:
            try:
                numeric_id = int(record_id)
                if len(self._records) > 0:
                    target_record = self._records[(numeric_id - 1) % len(self._records)]
            except ValueError:
                pass

        if not target_record:
            return False, f"Record with ID '{record_id}' not found", None

        if "sender" in data:
            target_record.sender = str(data["sender"])
            target_record.domain = target_record.get_domain()
        if "subject" in data:
            target_record.subject = str(data["subject"])
        if "body" in data:
            target_record.body = str(data["body"])
        if "label" in data:
            try:
                lbl = int(data["label"])
                if lbl in (0, 1):
                    target_record.label = lbl
            except (ValueError, TypeError):
                pass
        if "date" in data:
            target_record.date = str(data["date"])

        history_service.log_action(
            action="EDIT",
            entity_type="EMAIL",
            entity_id=record_id,
            summary=f"Updated email record #{record_id} ('{target_record.subject[:50]}')",
            details=data,
            actor="Administrator"
        )

        return True, "Email record updated successfully", target_record

    def delete_record(self, record_id):
        rec_id_str = str(record_id)
        
        if self.TOTAL_DATASET_COUNT > 0:
            self.TOTAL_DATASET_COUNT -= 1

        self._records = [r for r in self._records if r.id != rec_id_str]
        self._ids.discard(rec_id_str)

        history_service.log_action(
            action="DELETE",
            entity_type="EMAIL",
            entity_id=rec_id_str,
            summary=f"Deleted email record #{rec_id_str}",
            details={"deleted_id": rec_id_str},
            actor="Administrator"
        )

        return True, "Email record deleted successfully"

    # Export & Lookup
    def export_csv(self, query=None, label=None, domain=None):
        filtered = self._records

        if label is not None and label in (0, 1):
            filtered = [r for r in filtered if r.label == label]

        if domain:
            domain_lower = domain.strip().lower()
            filtered = [r for r in filtered if domain_lower in r.domain.lower()]

        if query:
            q_lower = query.strip().lower()
            filtered = [
                r for r in filtered
                if q_lower in r.sender.lower()
                or q_lower in r.subject.lower()
                or q_lower in r.body.lower()
            ]

        data_dicts = [r.to_dict() for r in filtered]
        df = pd.DataFrame(data_dicts)
        
        export_cols = ["id", "sender", "receiver", "subject", "body", "label", "domain", "date"]
        existing_cols = [c for c in export_cols if c in df.columns]
        if existing_cols:
            df = df[existing_cols]

        return df.to_csv(index=False)

    def get_record_by_id(self, record_id):
        for r in self._records:
            if r.id == str(record_id):
                return r
        return None


# Singleton Instance
dataset_service = DatasetService()
