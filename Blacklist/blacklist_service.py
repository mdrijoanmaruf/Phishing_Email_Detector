import os
import json
import re

from History.history_service import history_service


# Blacklist Service
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

    def __init__(self, json_path=None):
        if json_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.json_path = os.path.join(base_dir, "data", "blacklist.json")
        else:
            self.json_path = json_path

        self._domains = set()
        self._load()

    # Domain Normalization & Validation
    @staticmethod
    def clean_domain(domain_input):
        if not domain_input or not isinstance(domain_input, str):
            return ""

        clean = domain_input.strip().lower()
        clean = re.sub(r"^(https?://|mailto:)", "", clean)
        if "@" in clean:
            clean = clean.split("@")[-1]
        clean = clean.split("/")[0].split(":")[0]
        clean = clean.strip(". ")
        return clean

    @staticmethod
    def is_valid_domain(domain):
        if not domain or len(domain) < 3 or "." not in domain:
            return False
        pattern = r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63})+$"
        return bool(re.match(pattern, domain))

    # File Persistence
    def _load(self):
        if os.path.exists(self.json_path):
            try:
                with open(self.json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self._domains = {self.clean_domain(d) for d in data if self.clean_domain(d)}
            except Exception as e:
                print(f"[BlacklistService] Error loading {self.json_path}: {e}")
                self._domains = set()

        if not self._domains:
            self._domains = set(self.DEFAULT_DOMAINS)
            self._save()

    def _save(self):
        os.makedirs(os.path.dirname(self.json_path), exist_ok=True)
        try:
            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump(sorted(list(self._domains)), f, indent=2)
        except Exception as e:
            print(f"[BlacklistService] Error saving {self.json_path}: {e}")

    # Membership & Query Methods
    def get_all(self):
        return sorted(list(self._domains))

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

    # Mutation Methods
    def add(self, domain_input):
        cleaned = self.clean_domain(domain_input)
        if not cleaned:
            return False, "Domain cannot be empty."

        if not self.is_valid_domain(cleaned):
            return False, f"'{cleaned}' is not a valid domain name."

        if cleaned in self._domains:
            return False, f"Domain '{cleaned}' is already in the blacklist."

        self._domains.add(cleaned)
        self._save()

        history_service.log_action(
            action="BLACKLIST_ADD",
            entity_type="BLACKLIST",
            entity_id=cleaned,
            summary=f"Added domain '{cleaned}' to blacklisted domains",
            details={"domain": cleaned},
            actor="Administrator"
        )

        return True, f"Domain '{cleaned}' successfully blacklisted."

    def remove(self, domain_input):
        cleaned = self.clean_domain(domain_input)
        if not cleaned:
            return False, "Domain cannot be empty."

        if cleaned not in self._domains:
            return False, f"Domain '{cleaned}' was not found in the blacklist."

        self._domains.discard(cleaned)
        self._save()

        history_service.log_action(
            action="BLACKLIST_REMOVE",
            entity_type="BLACKLIST",
            entity_id=cleaned,
            summary=f"Removed domain '{cleaned}' from blacklisted domains",
            details={"domain": cleaned},
            actor="Administrator"
        )

        return True, f"Domain '{cleaned}' removed from blacklist."

    def count(self):
        return len(self._domains)
