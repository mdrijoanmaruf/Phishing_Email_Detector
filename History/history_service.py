import os
import json
import uuid
from datetime import datetime


# History Service
class HistoryService:
    def __init__(self, json_path=None):
        if json_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.json_path = os.path.join(base_dir, "data", "history.json")
        else:
            self.json_path = json_path

        self._records = []
        self._load()

    # Storage & Loading
    def _load(self):
        if os.path.exists(self.json_path):
            try:
                with open(self.json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self._records = data
            except Exception as e:
                print(f"[HistoryService] Error loading history: {e}")
                self._records = []
        else:
            self._records = []
            self._save()

    def _save(self):
        os.makedirs(os.path.dirname(self.json_path), exist_ok=True)
        try:
            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump(self._records, f, indent=2)
        except Exception as e:
            print(f"[HistoryService] Error saving history: {e}")

    # Logging Methods
    def log_action(
        self,
        action,
        entity_type,
        entity_id,
        summary,
        details=None,
        actor="Administrator"
    ):
        entry = {
            "id": f"act-{uuid.uuid4().hex[:8]}",
            "timestamp": datetime.now().isoformat(),
            "action": action.upper(),
            "entity_type": entity_type.upper(),
            "entity_id": str(entity_id),
            "summary": summary,
            "details": details or {},
            "actor": actor
        }

        self._records.insert(0, entry)
        if len(self._records) > 1000:
            self._records = self._records[:1000]

        self._save()
        return entry

    def add(self, scan_result):
        entry = {
            "id": scan_result.get("id") or f"act-{uuid.uuid4().hex[:8]}",
            "timestamp": scan_result.get("timestamp") or datetime.now().isoformat(),
            "action": scan_result.get("action", "SCAN"),
            "entity_type": scan_result.get("entity_type", "EMAIL"),
            "entity_id": str(scan_result.get("entity_id", scan_result.get("id", ""))),
            "summary": scan_result.get("summary") or f"Scanned email: {scan_result.get('subject', '')[:50]}",
            "details": scan_result.get("details") or scan_result,
            "actor": scan_result.get("actor", "Administrator")
        }
        self._records.insert(0, entry)
        if len(self._records) > 1000:
            self._records = self._records[:1000]
        self._save()
        return entry

    # Query Methods
    def get_all(self, action=None, entity_type=None, limit=200):
        self._load()
        results = self._records

        if action and action.strip().upper() != "ALL":
            a_upper = action.strip().upper()
            results = [
                r for r in results
                if r.get("action", "").upper() == a_upper
                or a_upper in r.get("action", "").upper()
                or r.get("entity_type", "").upper() == a_upper
            ]

        if entity_type and entity_type.strip().upper() != "ALL":
            e_upper = entity_type.strip().upper()
            results = [r for r in results if r.get("entity_type", "").upper() == e_upper]

        return results[:limit]

    def get_by_id(self, log_id):
        for r in self._records:
            if str(r.get("id")) == str(log_id):
                return r
        return None

    # Deletion & Management
    def delete(self, log_id):
        initial_len = len(self._records)
        self._records = [r for r in self._records if str(r.get("id")) != str(log_id)]
        if len(self._records) < initial_len:
            self._save()
            return True
        return False

    def clear_all(self):
        self._records = []
        self._save()
        return True

    def count(self):
        return len(self._records)


# Singleton Instance
history_service = HistoryService()
