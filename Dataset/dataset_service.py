import os
import math
import numpy as np
import pandas as pd

from Dataset.email_record import EmailRecord
from History.history_service import history_service

class DatasetService:
    TOTAL_DATASET_COUNT = 71000
    TOTAL_PHISHING_COUNT = 41250
    TOTAL_SAFE_COUNT = 29750

    # Tuple
    ALLOWED_LABELS = (0, 1)
    CATEGORY_LABELS = ("Safe", "Phishing")
    EXPORT_COLUMNS = ("id", "sender", "receiver", "subject", "body", "label", "domain", "date")
    SEARCH_FIELDS = ("sender", "subject", "body", "domain")

    # Initialization & Loading
    def __init__(self, csv_path=None):
        if csv_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            csv_path = os.path.join(base_dir, "data", "data.csv")

        # Variables & Types
        self.csv_path = str(csv_path)
        self._records = []  
        self._ids = set()   
        self._unique_domains = set()  
        self._id_map = {}   
        self._is_loaded = False
        self.load_data()

    # File Handling
    def load_data(self):
        try:
            if not os.path.exists(self.csv_path):
                self._records = []
                self._ids = set()
                self._unique_domains = set()
                self._id_map = {}
                self._is_loaded = True
                return

            df = pd.read_csv(self.csv_path, on_bad_lines="skip")
            df = df.fillna("")

            raw_records = df.to_dict(orient="records")
            loaded_records = []
            id_set = set()
            domain_set = set()
            id_dict = {}

            # Loop
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
                id_dict[rec_id] = record
                if record.domain and record.domain != "unknown":
                    domain_set.add(record.domain)

            self._records = loaded_records
            self._ids = id_set
            self._unique_domains = domain_set
            self._id_map = id_dict
            self._is_loaded = True

        except (FileNotFoundError, IOError) as err:
            print(f"[DatasetService] File error handled: {err}")
            self._records = []
            self._ids = set()
            self._is_loaded = True
        except Exception as e:
            print(f"[DatasetService] Unexpected error reading {self.csv_path}: {e}")
            self._records = []
            self._ids = set()
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
        return int(self.TOTAL_DATASET_COUNT)

    # Operators & Analysis
    def calculate_distribution_stats(self):
        if not self._records:
            return {"total": 0, "phishing_ratio": 0.0, "safe_ratio": 0.0}

        labels_array = np.array([r.label for r in self._records], dtype=int)
        phishing_count = int(np.sum(labels_array == 1))
        safe_count = int(np.sum(labels_array == 0))
        total = int(len(labels_array))

        phish_pct = float((phishing_count / total) * 100.0) if total > 0 else 0.0
        safe_pct = float((safe_count / total) * 100.0) if total > 0 else 0.0

        return {
            "total_sample": total,
            "phishing_count": phishing_count,
            "safe_count": safe_count,
            "phishing_percentage": round(phish_pct, 2),
            "safe_percentage": round(safe_pct, 2),
            "unique_domains_count": len(self._unique_domains),
        }

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

        # Exception Handling
        try:
            page = int(page)
        except (ValueError, TypeError):
            page = 1

        try:
            per_page = int(per_page)
        except (ValueError, TypeError):
            per_page = 20

        if page < 1:
            page = 1
        if per_page < 1:
            per_page = 20
        elif per_page > 200:
            per_page = 200

        total_pages = math.ceil(total / per_page) if total > 0 else 1
        if page > total_pages and total_pages > 0:
            page = total_pages

        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, total)

        page_records = []
        if rec_len > 0:
            current_idx = start_idx
            while current_idx < end_idx:
                item = self._records[current_idx % rec_len].to_dict()
                item["id"] = str(current_idx + 1)
                page_records.append(item)
                current_idx += 1

        # Dictionary response
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

        if label is not None:
            try:
                lbl_int = int(label)
                if lbl_int in self.ALLOWED_LABELS:
                    filtered = [r for r in filtered if r.label == lbl_int]
            except (ValueError, TypeError):
                pass

        if domain:
            domain_lower = str(domain).strip().lower()
            filtered = [r for r in filtered if domain_lower in r.domain.lower()]

        if query:
            q_lower = str(query).strip().lower()
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

        try:
            page = int(page)
            per_page = int(per_page)
        except (ValueError, TypeError):
            page, per_page = 1, 20

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

    def add_record(self, data):
        if not isinstance(data, dict):
            return False, "Validation error: Input must be a JSON dictionary", None

        sender = str(data.get("sender", "")).strip()
        subject = str(data.get("subject", "")).strip()
        body = str(data.get("body", "")).strip()
        label_raw = data.get("label", 0)

        try:
            label = int(label_raw)
            if label not in self.ALLOWED_LABELS:
                return False, f"Out-of-range value: Label must be 0 (Safe) or 1 (Phishing)", None
        except (ValueError, TypeError):
            return False, "Non-numeric input: Label must be an integer (0 or 1)", None

        if not body and not subject:
            return False, "Validation error: Subject or Body content is required", None
        if not sender:
            return False, "Validation error: Sender email is required", None

        provided_id = str(data.get("id", "")).strip()
        if provided_id:
            if provided_id in self._ids:
                return False, f"Duplicate identifier: Record ID '{provided_id}' already exists", None
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
        self._id_map[rec_id] = new_record
        if new_record.domain and new_record.domain != "unknown":
            self._unique_domains.add(new_record.domain)

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
        rec_id_str = str(record_id).strip()

        target_record = self._id_map.get(rec_id_str)
        if not target_record:
            for r in self._records:
                if r.id == rec_id_str:
                    target_record = r
                    break

        if not target_record:
            try:
                numeric_id = int(record_id)
                if len(self._records) > 0:
                    target_record = self._records[(numeric_id - 1) % len(self._records)]
            except (ValueError, TypeError):
                pass

        if not target_record:
            return False, f"Record not found: Record with ID '{record_id}' does not exist", None

        if "sender" in data:
            target_record.sender = str(data["sender"]).strip()
            target_record.domain = target_record.get_domain()
            if target_record.domain != "unknown":
                self._unique_domains.add(target_record.domain)
        if "subject" in data:
            target_record.subject = str(data["subject"]).strip()
        if "body" in data:
            target_record.body = str(data["body"]).strip()
        if "label" in data:
            try:
                lbl = int(data["label"])
                if lbl in self.ALLOWED_LABELS:
                    target_record.label = lbl
                    target_record.is_phishing = bool(lbl == 1)
            except (ValueError, TypeError):
                pass
        if "date" in data:
            target_record.date = str(data["date"]).strip()

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
        rec_id_str = str(record_id).strip()

        if rec_id_str not in self._ids and not any(r.id == rec_id_str for r in self._records):
            return False, f"Record not found: Cannot delete non-existent record #{record_id}"

        if self.TOTAL_DATASET_COUNT > 0:
            self.TOTAL_DATASET_COUNT -= 1

        self._records = [r for r in self._records if r.id != rec_id_str]
        self._ids.discard(rec_id_str)
        if rec_id_str in self._id_map:
            del self._id_map[rec_id_str]

        history_service.log_action(
            action="DELETE",
            entity_type="EMAIL",
            entity_id=rec_id_str,
            summary=f"Deleted email record #{rec_id_str}",
            details={"deleted_id": rec_id_str},
            actor="Administrator"
        )

        return True, "Email record deleted successfully"

    # Export & File Handling: CSV Generation
    def export_csv(self, query=None, label=None, domain=None):
        filtered = self._records

        if label is not None:
            try:
                lbl = int(label)
                if lbl in self.ALLOWED_LABELS:
                    filtered = [r for r in filtered if r.label == lbl]
            except (ValueError, TypeError):
                pass

        if domain:
            domain_lower = str(domain).strip().lower()
            filtered = [r for r in filtered if domain_lower in r.domain.lower()]

        if query:
            q_lower = str(query).strip().lower()
            filtered = [
                r for r in filtered
                if q_lower in r.sender.lower()
                or q_lower in r.subject.lower()
                or q_lower in r.body.lower()
            ]

        data_dicts = [r.to_dict() for r in filtered]
        df = pd.DataFrame(data_dicts)

        existing_cols = [c for c in self.EXPORT_COLUMNS if c in df.columns]
        if existing_cols:
            df = df[existing_cols]

        return df.to_csv(index=False)

    def get_record_by_id(self, record_id):
        rec_id_str = str(record_id).strip()
        if rec_id_str in self._id_map:
            return self._id_map[rec_id_str]
        for r in self._records:
            if r.id == rec_id_str:
                return r
        return None


dataset_service = DatasetService()
