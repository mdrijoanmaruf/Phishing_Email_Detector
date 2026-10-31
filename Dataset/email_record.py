import re
from typing import Any, Dict, List, Optional


class EmailRecord:
    """Represents a single email record in the dataset."""

    def __init__(
        self,
        record_id: str,
        sender: str,
        subject: str,
        body: str,
        label: int,
        date: Optional[str] = None,
        receiver: Optional[str] = None,
        urls: Optional[Any] = None,
    ):
        self.id = str(record_id)
        self.sender = str(sender) if sender is not None else ""
        self.receiver = str(receiver) if receiver is not None else ""
        self.subject = str(subject) if subject is not None else ""
        self.body = str(body) if body is not None else ""
        self.label = int(label) if label in (0, 1, "0", "1") else 0
        self.date = str(date) if date is not None else ""
        self.urls = self._parse_urls(urls)
        self.domain = self.get_domain()

    def _parse_urls(self, urls: Any) -> List[str]:
        """Normalize urls into a list of strings."""
        if urls is None:
            return []
        if isinstance(urls, list):
            return [str(u) for u in urls]
        # In data.csv, urls might be an integer count or comma-separated string
        if isinstance(urls, (int, float)):
            return []
        if isinstance(urls, str):
            urls_str = urls.strip()
            if urls_str.startswith("[") and urls_str.endswith("]"):
                cleaned = urls_str.strip("[]").replace("'", "").replace('"', "")
                return [u.strip() for u in cleaned.split(",") if u.strip()]
            return [urls_str] if urls_str else []
        return []

    def get_domain(self) -> str:
        """Extract sender domain using regular expression."""
        if not self.sender:
            return "unknown"
        match = re.search(r"@([a-zA-Z0-9.\-]+)", self.sender)
        if match:
            # Strip trailing punctuation or brackets
            return match.group(1).strip(">").strip(")").lower()
        return "unknown"

    def to_dict(self) -> Dict[str, Any]:
        """Convert EmailRecord to a plain Python dictionary for JSON serialization."""
        return {
            "id": self.id,
            "sender": self.sender,
            "receiver": self.receiver,
            "subject": self.subject,
            "body": self.body,
            "label": self.label,
            "label_text": "Phishing" if self.label == 1 else "Safe",
            "date": self.date,
            "urls": self.urls,
            "domain": self.domain,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EmailRecord":
        """Instantiate an EmailRecord from a dictionary."""
        return cls(
            record_id=data.get("id", ""),
            sender=data.get("sender", ""),
            subject=data.get("subject", ""),
            body=data.get("body", ""),
            label=data.get("label", 0),
            date=data.get("date", ""),
            receiver=data.get("receiver", ""),
            urls=data.get("urls", []),
        )

    def __str__(self) -> str:
        return f"[EmailRecord #{self.id}] Sender: {self.sender} | Domain: {self.domain} | Label: {self.label}"

    def __repr__(self) -> str:
        return f"EmailRecord(id={self.id!r}, sender={self.sender!r}, label={self.label!r})"
