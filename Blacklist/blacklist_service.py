"""
Phishing_Email_Detector_Server/Blacklist/blacklist_service.py
Service for managing blacklisted sender domains.
Uses a Python set for O(1) membership testing and ensures JSON persistence.
"""

import os
import json
import re
from typing import List, Set
from History.history_service import history_service


class BlacklistService:
    """Manages the set of blacklisted sender domains."""

    DEFAULT_DOMAINS = [
        "secure-paypal-verify.com",
        "appleid-alert-support.com",
        "account-update-bank.xyz",
        "login-security-check.net",
        "free-gift-crypto.com",
        "irs-tax-refund-gov.cc",
        "verify-netflix-billing.org",
    ]

    def __init__(self, json_path: str = None):
        if json_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.json_path = os.path.join(base_dir, "data", "blacklist.json")
        else:
            self.json_path = json_path

        # In-memory Python set for fast O(1) membership testing
        self._domains: Set[str] = set()
        self._load()

    @staticmethod
    def clean_domain(domain_input: str) -> str:
        """
        Normalize domain input:
        Removes protocol prefix (http://, https://), port numbers, URL paths,
        and leading '@' symbols if an email was passed.
        """
        if not domain_input or not isinstance(domain_input, str):
            return ""

        clean = domain_input.strip().lower()
        # Remove mailto: or protocols
        clean = re.sub(r"^(https?://|mailto:)", "", clean)
        # If user passed young@iworld.de, extract iworld.de
        if "@" in clean:
            clean = clean.split("@")[-1]
        # Remove paths and trailing slashes
        clean = clean.split("/")[0].split(":")[0]
        # Remove leading dots or whitespaces
        clean = clean.strip(". ")
        return clean

    @staticmethod
    def is_valid_domain(domain: str) -> bool:
        """Validate whether the domain string is structurally valid."""
        if not domain or len(domain) < 3 or "." not in domain:
            return False
        # Regex for valid hostname/domain
        pattern = r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63})+$"
        return bool(re.match(pattern, domain))

    def _load(self):
        """Load domains from JSON file into Python set."""
        if os.path.exists(self.json_path):
            try:
                with open(self.json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self._domains = {self.clean_domain(d) for d in data if self.clean_domain(d)}
            except Exception as e:
                print(f"[BlacklistService] Error loading {self.json_path}: {e}")
                self._domains = set()

        # Seed with initial common phishing domains if empty
        if not self._domains:
            self._domains = set(self.DEFAULT_DOMAINS)
            self._save()

    def _save(self):
        """Save the in-memory set to JSON as a sorted list."""
        os.makedirs(os.path.dirname(self.json_path), exist_ok=True)
        try:
            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump(sorted(list(self._domains)), f, indent=2)
        except Exception as e:
            print(f"[BlacklistService] Error saving {self.json_path}: {e}")

    def get_all(self) -> List[str]:
        """Return all blacklisted domains as a sorted list."""
        return sorted(list(self._domains))

    def contains(self, domain: str) -> bool:
        """Check if a domain or sub-domain matches a blacklisted entry."""
        cleaned = self.clean_domain(domain)
        if not cleaned:
            return False

        if cleaned in self._domains:
            return True

        # Also check parent domains (e.g. evil.phish.com -> check phish.com)
        parts = cleaned.split(".")
        if len(parts) > 2:
            parent = ".".join(parts[1:])
            if parent in self._domains:
                return True

        return False

    def add(self, domain_input: str) -> tuple[bool, str]:
        """
        Add a domain to the blacklist.
        Returns (success: bool, message: str)
        """
        cleaned = self.clean_domain(domain_input)
        if not cleaned:
            return False, "Domain cannot be empty."

        if not self.is_valid_domain(cleaned):
            return False, f"'{cleaned}' is not a valid domain name."

        if cleaned in self._domains:
            return False, f"Domain '{cleaned}' is already in the blacklist."

        self._domains.add(cleaned)
        self._save()

        # Audit history log
        history_service.log_action(
            action="BLACKLIST_ADD",
            entity_type="BLACKLIST",
            entity_id=cleaned,
            summary=f"Added domain '{cleaned}' to blacklisted domains",
            details={"domain": cleaned},
            actor="Administrator"
        )

        return True, f"Domain '{cleaned}' successfully blacklisted."

    def remove(self, domain_input: str) -> tuple[bool, str]:
        """
        Remove a domain from the blacklist.
        Returns (success: bool, message: str)
        """
        cleaned = self.clean_domain(domain_input)
        if not cleaned:
            return False, "Domain cannot be empty."

        if cleaned not in self._domains:
            return False, f"Domain '{cleaned}' was not found in the blacklist."

        self._domains.discard(cleaned)
        self._save()

        # Audit history log
        history_service.log_action(
            action="BLACKLIST_REMOVE",
            entity_type="BLACKLIST",
            entity_id=cleaned,
            summary=f"Removed domain '{cleaned}' from blacklisted domains",
            details={"domain": cleaned},
            actor="Administrator"
        )

        return True, f"Domain '{cleaned}' removed from blacklist."

    def count(self) -> int:
        """Return number of blacklisted domains."""
        return len(self._domains)

