import re
class EmailRecord:
    VALID_LABELS = (0, 1)
    CATEGORY_TUPLE = ("Safe", "Phishing")
    REQUIRED_FIELDS = ("sender", "body")

    def __init__(
        self,
        record_id,
        sender,
        subject,
        body,
        label,
        date=None,
        receiver=None,
        urls=None,
    ):
        self.id = str(record_id) if record_id is not None else ""
        self.sender = str(sender).strip() if sender is not None else ""
        self.receiver = str(receiver).strip() if receiver is not None else ""
        self.subject = str(subject).strip() if subject is not None else ""
        self.body = str(body).strip() if body is not None else ""

        try:
            parsed_label = int(label)
            if parsed_label in self.VALID_LABELS:
                self.label = parsed_label
            else:
                self.label = 0
        except (ValueError, TypeError):
            self.label = 0

        self.date = str(date).strip() if date is not None else ""
        self.urls = self._parse_urls(urls)
        self.domain = self.get_domain()
        self.is_phishing = bool(self.label == 1)

    def _parse_urls(self, urls):
        if urls is None:
            return []
        elif isinstance(urls, list):
            cleaned_urls = []
            for item in urls:
                if isinstance(item, str) and item.strip():
                    cleaned_urls.append(item.strip())
            return cleaned_urls
        elif isinstance(urls, str):
            urls_str = urls.strip()
            if urls_str.startswith("[") and urls_str.endswith("]"):
                cleaned = urls_str.strip("[]").replace("'", "").replace('"', "")
                url_list = []
                for u in cleaned.split(","):
                    val = u.strip()
                    if val:
                        url_list.append(val)
                return url_list
            return [urls_str] if urls_str else []
        else:
            return []

    def get_domain(self):
        if not self.sender:
            return "unknown"
        match = re.search(r"@([a-zA-Z0-9.\-]+)", self.sender)
        if match:
            return match.group(1).strip(">").strip(")").lower()
        return "unknown"

    def validate(self):
        if not self.sender:
            return False, "Validation error: sender email is required"
        if not self.body:
            return False, "Validation error: email body content is required"
        if self.label not in self.VALID_LABELS:
            return False, f"Out-of-range value: label must be one of {self.VALID_LABELS}"
        return True, "Valid record"

    def to_dict(self):
        return {
            "id": self.id,
            "sender": self.sender,
            "receiver": self.receiver,
            "subject": self.subject,
            "body": self.body,
            "label": self.label,
            "label_text": self.CATEGORY_TUPLE[1] if self.label == 1 else self.CATEGORY_TUPLE[0],
            "date": self.date,
            "urls": self.urls,
            "domain": self.domain,
            "is_phishing": self.is_phishing,
        }

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            return cls("", "", "", "", 0)
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

    def __str__(self):
        return f"[EmailRecord #{self.id}] Sender: {self.sender} | Domain: {self.domain} | Phishing: {self.is_phishing}"

    def __repr__(self):
        return f"EmailRecord(id={self.id!r}, sender={self.sender!r}, label={self.label!r})"
