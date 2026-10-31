"""
Phishing_Email_Detector_Server/History/history_service.py
Service for persisting and managing activity history and audit logs.
Records Add, Edit, Delete, View, and Blacklist actions into data/history.json.
"""

import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional


class HistoryService:
    """Manages audit and activity history records stored in JSON format."""

    def __init__(self, json_path: str = None):
        if json_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.json_path = os.path.join(base_dir, "data", "history.json")
        else:
            self.json_path = json_path

        self._records: List[Dict[str, Any]] = []
        self._load()

    def _load(self):
        """Load history records from JSON file."""
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
        """Save history records to JSON file."""
        os.makedirs(os.path.dirname(self.json_path), exist_ok=True)
        try:
            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump(self._records, f, indent=2)
        except Exception as e:
            print(f"[HistoryService] Error saving history: {e}")

    def log_action(
        self,
        action: str,
        entity_type: str,
        entity_id: str,
        summary: str,
        details: Optional[Dict[str, Any]] = None,
        actor: str = "Administrator"
    ) -> Dict[str, Any]:
        """
        Record an action into history.
        Actions: ADD, EDIT, DELETE, VIEW, BLACKLIST_ADD, BLACKLIST_REMOVE
        """
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

        # Prepend to front so newest activities show first
        self._records.insert(0, entry)
        # Keep maximum 1000 records
        if len(self._records) > 1000:
            self._records = self._records[:1000]

        self._save()
        return entry

    def add(self, scan_result: Dict[str, Any]) -> Dict[str, Any]:
        """Backward compatibility helper for recording entries."""
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

    def get_all(
        self,
        action: Optional[str] = None,
        entity_type: Optional[str] = None,
        limit: int = 200
    ) -> List[Dict[str, Any]]:
        """Return history records filtered by action or entity_type with limit."""
        # Always reload from file to ensure fresh synchronization
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

    def get_by_id(self, log_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a single history record by ID."""
        for r in self._records:
            if str(r.get("id")) == str(log_id):
                return r
        return None

    def delete(self, log_id: str) -> bool:
        """Delete a history record by ID."""
        initial_len = len(self._records)
        self._records = [r for r in self._records if str(r.get("id")) != str(log_id)]
        if len(self._records) < initial_len:
            self._save()
            return True
        return False

    def clear_all(self) -> bool:
        """Clear all history records."""
        self._records = []
        self._save()
        return True

    def count(self) -> int:
        """Return total number of history records."""
        return len(self._records)


# Singleton instance
history_service = HistoryService()
