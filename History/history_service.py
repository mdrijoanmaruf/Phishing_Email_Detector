import os
import json
import uuid
from datetime import datetime


class ActivityRecord:
    VALID_ACTIONS = ("ADD", "EDIT", "DELETE", "VIEW", "BLACKLIST_ADD", "BLACKLIST_REMOVE", "SCAN")
    VALID_ENTITIES = ("EMAIL", "BLACKLIST", "SYSTEM")

    def __init__(
        self,
        record_id=None,
        action="VIEW",
        entity_type="EMAIL",
        entity_id="",
        summary="",
        details=None,
        actor="Administrator",
        timestamp=None
    ):
        self.id = str(record_id) if record_id else f"act-{uuid.uuid4().hex[:8]}"
        self.action = str(action).strip().upper()
        self.entity_type = str(entity_type).strip().upper()
        self.entity_id = str(entity_id).strip()
        self.summary = str(summary).strip()
        self.details = details if isinstance(details, dict) else {}
        self.actor = str(actor).strip() if actor else "Administrator"
        self.timestamp = str(timestamp) if timestamp else datetime.now().isoformat()

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "action": self.action,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "summary": self.summary,
            "details": self.details,
            "actor": self.actor,
        }

    def __str__(self):
        return f"[ActivityRecord #{self.id}] {self.action} on {self.entity_type} #{self.entity_id} by {self.actor}"

class HistoryService:
    MAX_LOGS = 1000

    # Tuple
    ACTION_CATEGORIES = ("DATASET", "BLACKLIST", "ANALYTICS")

    def __init__(self, json_path=None):
        if json_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.json_path = os.path.join(base_dir, "data", "history.json")
        else:
            self.json_path = str(json_path)

        self._records = []
        self._log_ids = set()
        self._load()

    # File Handling: Load JSON with Exception Handling
    def _load(self):
        if os.path.exists(self.json_path):
            try:
                with open(self.json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        loaded_records = []
                        id_set = set()
                        # Loop: for loop parsing entries
                        for item in data:
                            if isinstance(item, dict):
                                rec_id = str(item.get("id", ""))
                                loaded_records.append(item)
                                if rec_id:
                                    id_set.add(rec_id)
                        self._records = loaded_records
                        self._log_ids = id_set
            except (FileNotFoundError, IOError, json.JSONDecodeError) as e:
                print(f"[HistoryService] Error loading history from {self.json_path}: {e}")
                self._records = []
                self._log_ids = set()
        else:
            self._records = []
            self._log_ids = set()
            self._save()

    def _save(self):
        os.makedirs(os.path.dirname(self.json_path), exist_ok=True)
        try:
            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump(self._records, f, indent=2)
        except (IOError, OSError) as e:
            print(f"[HistoryService] Error saving history: {e}")

    def log_action(
        self,
        action,
        entity_type,
        entity_id,
        summary,
        details=None,
        actor="Administrator"
    ):
        record = ActivityRecord(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            summary=summary,
            details=details,
            actor=actor
        )

        entry = record.to_dict()

        # Duplicate Identifier prevention using Set
        if entry["id"] in self._log_ids:
            entry["id"] = f"act-{uuid.uuid4().hex[:10]}"

        self._records.insert(0, entry)
        self._log_ids.add(entry["id"])

        while len(self._records) > self.MAX_LOGS:
            removed = self._records.pop()
            if isinstance(removed, dict) and "id" in removed:
                self._log_ids.discard(removed["id"])

        self._save()
        return entry

    def add(self, scan_result):
        if not isinstance(scan_result, dict):
            return {}

        rec_id = scan_result.get("id") or f"act-{uuid.uuid4().hex[:8]}"
        record = ActivityRecord(
            record_id=rec_id,
            action=scan_result.get("action", "SCAN"),
            entity_type=scan_result.get("entity_type", "EMAIL"),
            entity_id=str(scan_result.get("entity_id", scan_result.get("id", ""))),
            summary=scan_result.get("summary") or f"Scanned email: {str(scan_result.get('subject', ''))[:50]}",
            details=scan_result.get("details") or scan_result,
            actor=scan_result.get("actor", "Administrator"),
            timestamp=scan_result.get("timestamp")
        )
        entry = record.to_dict()

        self._records.insert(0, entry)
        self._log_ids.add(entry["id"])

        while len(self._records) > self.MAX_LOGS:
            removed = self._records.pop()
            if isinstance(removed, dict) and "id" in removed:
                self._log_ids.discard(removed["id"])

        self._save()
        return entry

    def get_all(self, action=None, entity_type=None, limit=200):
        self._load()
        results = self._records

        # Exception Handling: Non-numeric and out-of-range limit
        try:
            limit_int = int(limit)
            if limit_int < 1:
                limit_int = 200
            elif limit_int > self.MAX_LOGS:
                limit_int = self.MAX_LOGS
        except (ValueError, TypeError):
            limit_int = 200

        if action and str(action).strip().upper() != "ALL":
            a_upper = str(action).strip().upper()
            results = [
                r for r in results
                if r.get("action", "").upper() == a_upper
                or a_upper in r.get("action", "").upper()
                or r.get("entity_type", "").upper() == a_upper
            ]

        if entity_type and str(entity_type).strip().upper() != "ALL":
            e_upper = str(entity_type).strip().upper()
            results = [r for r in results if r.get("entity_type", "").upper() == e_upper]

        return results[:limit_int]

    def get_by_id(self, log_id):
        log_id_str = str(log_id).strip()
        if log_id_str not in self._log_ids:
            return None
        for r in self._records:
            if r.get("id") == log_id_str:
                return r
        return None

    def count(self):
        return len(self._records)

    def delete(self, log_id):
        log_id_str = str(log_id).strip()

        if log_id_str not in self._log_ids and not any(r.get("id") == log_id_str for r in self._records):
            return False, f"Record not found: Activity log #{log_id} does not exist"

        before_len = len(self._records)
        self._records = [r for r in self._records if r.get("id") != log_id_str]
        self._log_ids.discard(log_id_str)

        if len(self._records) < before_len:
            self._save()
            return True, f"Activity record #{log_id} successfully deleted"
        return False, f"Record not found: Activity log #{log_id} does not exist"

    # Clear All Operations
    def clear(self):
        total_cleared = len(self._records)
        self._records = []
        self._log_ids = set()
        self._save()
        return True, f"Successfully cleared all {total_cleared} audit logs"

    def clear_all(self):
        return self.clear()


history_service = HistoryService()
