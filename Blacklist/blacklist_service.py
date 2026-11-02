import os
import json
import re
from datetime import datetime

from History.history_service import history_service


class BlacklistDomain:
    HIGH_RISK_EXTENSIONS = (".xyz", ".cc", ".top", ".club", ".work", ".kim", ".country", ".tk")
    DEFAULT_PENALTY = 40

    def __init__(self, domain, added_at=None, penalty=None):
        self.domain = str(domain).strip().lower()
        self.added_at = str(added_at) if added_at else datetime.now().isoformat()
        self.penalty = int(penalty) if penalty is not None else self.DEFAULT_PENALTY
        self.is_high_risk_tld = any(self.domain.endswith(ext) for ext in self.HIGH_RISK_EXTENSIONS)

    def to_dict(self):
        return {
            "domain": self.domain,
            "added_at": self.added_at,
            "penalty": self.penalty,
            "is_high_risk_tld": self.is_high_risk_tld,
        }

    def __str__(self):
        return f"[BlacklistDomain: {self.domain} | Penalty: +{self.penalty}]"


class BlacklistService:
    DEFAULT_DOMAINS = [
        "secure-paypal-verify.com",
        "appleid-alert-support.com",
        "account-update-bank.xyz",

        "login-security-check.net",
        "free-gift-crypto.com",
        "irs-tax-refund-gov.cc",
        "verify-netflix-billing.org",
    ]

    # Tuple
    FORBIDDEN_PROTOCOLS = ("http://", "https://", "ftp://", "mailto:")
    RISK_LEVEL_TUPLE = ("Standard", "Elevated", "Critical")

    def __init__(self, json_path=None):
        if json_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.json_path = os.path.join(base_dir, "data", "blacklist.json")
        else:
            self.json_path = str(json_path)

        # Set
        self._domains = set()
        # Dictionary: Maps domain
        self._domain_objects = {}
        self._load()

    # Domain Normalization using while and if/elif/else
    @classmethod
    def clean_domain(cls, domain_input):
        if not domain_input or not isinstance(domain_input, str):
            return ""

        clean = domain_input.strip().lower()

        # Loop
        has_protocol = True
        while has_protocol:
            has_protocol = False
            for proto in cls.FORBIDDEN_PROTOCOLS:
                if clean.startswith(proto):
                    clean = clean[len(proto):]
                    has_protocol = True

        # Extract domain from email if '@' present
        if "@" in clean:
            clean = clean.split("@")[-1]

        # Strip paths and ports
        clean = clean.split("/")[0].split(":")[0]
        clean = clean.strip(". ")
        return clean

    # Validation Function
    @staticmethod
    def is_valid_domain(domain):
        if not domain or not isinstance(domain, str):
            return False
        if len(domain) < 3 or len(domain) > 255:
            return False
        if "." not in domain:
            return False
        pattern = r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63})+$"
        return bool(re.match(pattern, domain))

    # File Handling
    def _load(self):
        # Exception Handling
        if os.path.exists(self.json_path):
            try:
                with open(self.json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        loaded_set = set()
                        for item in data:
                            clean = self.clean_domain(item)
                            if clean:
                                loaded_set.add(clean)
                                self._domain_objects[clean] = BlacklistDomain(clean)
                        self._domains = loaded_set
            except (FileNotFoundError, IOError, json.JSONDecodeError) as e:
                print(f"[BlacklistService] Error loading {self.json_path}: {e}")
                self._domains = set()

        if not self._domains:
            for d in self.DEFAULT_DOMAINS:
                clean = self.clean_domain(d)
                self._domains.add(clean)
                self._domain_objects[clean] = BlacklistDomain(clean)
            self._save()

    # File Handling: Saving JSON
    def _save(self):
        os.makedirs(os.path.dirname(self.json_path), exist_ok=True)
        try:
            with open(self.json_path, "w", encoding="utf-8") as f:
                # List: sorted list written to json
                json.dump(sorted(list(self._domains)), f, indent=2)
        except (IOError, OSError) as e:
            print(f"[BlacklistService] Error saving {self.json_path}: {e}")

    # Query Methods
    def get_all(self):
        return sorted(list(self._domains))

    def count(self):
        return len(self._domains)

    def contains(self, domain):
        cleaned = self.clean_domain(domain)
        if not cleaned:
            return False

        if cleaned in self._domains:
            return True

        parts = cleaned.split(".")
        if len(parts) > 2:
            parent = ".".join(parts[1:])
            if parent in self._domains:
                return True

        return False

    def add(self, domain_input):
        cleaned = self.clean_domain(domain_input)

        if not cleaned:
            return False, "Validation error: Domain name cannot be empty."

        if not self.is_valid_domain(cleaned):
            return False, f"Out-of-range value: '{cleaned}' is not a valid domain format."

        if cleaned in self._domains:
            return False, f"Duplicate identifier: Domain '{cleaned}' is already in the blacklist."

        self._domains.add(cleaned)
        self._domain_objects[cleaned] = BlacklistDomain(cleaned)
        self._save()

        history_service.log_action(
            action="BLACKLIST_ADD",
            entity_type="BLACKLIST",
            entity_id=cleaned,
            summary=f"Added domain '{cleaned}' to blacklist (+40 pts penalty)",
            details={"domain": cleaned, "penalty": 40},
            actor="Administrator"
        )

        return True, f"Domain '{cleaned}' successfully added to blacklist."

    def remove(self, domain_input):
        cleaned = self.clean_domain(domain_input)
        if not cleaned:
            return False, "Validation error: Domain name cannot be empty."

        if cleaned not in self._domains:
            return False, f"Record not found: Domain '{cleaned}' was not found in the blacklist."

        self._domains.remove(cleaned)
        if cleaned in self._domain_objects:
            del self._domain_objects[cleaned]
        self._save()

        history_service.log_action(
            action="BLACKLIST_REMOVE",
            entity_type="BLACKLIST",
            entity_id=cleaned,
            summary=f"Removed domain '{cleaned}' from blacklist",
            details={"domain": cleaned},
            actor="Administrator"
        )

        return True, f"Domain '{cleaned}' successfully removed from blacklist."


blacklist_service = BlacklistService()
