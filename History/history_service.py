"""
Phishing_Email_Detector_Server/History/history_service.py
Service for persisting and managing past email scans.
"""

import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional


class HistoryService:
    """Manages scan history records stored in JSON format."""

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

    def add(self, scan_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Record a scan result into history.
        Prepends new scans to the top (newest first).
        """
        entry = {
            "id": scan_result.get("id") or uuid.uuid4().hex[:8],
            "timestamp": scan_result.get("timestamp") or datetime.now().isoformat(),
            "sender": scan_result.get("sender", ""),
            "domain": scan_result.get("domain", ""),
            "subject": scan_result.get("subject", ""),
            "body": scan_result.get("body", ""),
            "score": scan_result.get("score", 0),
            "verdict": scan_result.get("verdict", "SAFE"),
            "reasons": scan_result.get("reasons", []),
            "urls": scan_result.get("urls", []),
            "keywords_found": scan_result.get("keywords_found", [])
        }

        # Prepend to front so newest scans show first
        self._records.insert(0, entry)
        # Keep maximum 500 scans to prevent unbounded file growth
        if len(self._records) > 500:
            self._records = self._records[:500]

        self._save()
        return entry

    def get_all(self, verdict: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Return scans filtered by verdict (optional) with limit."""
        results = self._records
        if verdict and verdict.strip().upper() != "ALL":
            v_upper = verdict.strip().upper()
            results = [r for r in results if r.get("verdict", "").upper() == v_upper]

        return results[:limit]

    def get_by_id(self, scan_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a single scan result by ID."""
        for r in self._records:
            if str(r.get("id")) == str(scan_id):
                return r
        return None

    def delete(self, scan_id: str) -> bool:
        """Delete a scan record by ID."""
        initial_len = len(self._records)
        self._records = [r for r in self._records if str(r.get("id")) != str(scan_id)]
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

