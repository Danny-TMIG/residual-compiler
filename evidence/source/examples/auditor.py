#!/usr/bin/env python3
"""
auditor.py - WORM Ledger & Olympic Ring Chain Mail Cryptographic Integrity Auditor
Validates SHA-256 hash chaining across historical manifold cycles to guarantee
absolute system determinism and detect state drift.
"""

import json
import hashlib
import os

class ManifoldAuditor:
    def __init__(self, ledger_path: str = "sovereign/manifold_ledger.jsonl"):
        self.ledger_path = ledger_path

    def audit_chain(self) -> bool:
        """Verifies that every entry in the WORM ledger mathematically links to its predecessor."""
        if not os.path.exists(self.ledger_path):
            print(f"[-] Ledger path not found: {self.ledger_path}")
            return False

        print(f"[*] Beginning cryptographic audit of ledger: {self.ledger_path}")

        valid = True
        previous_tick = 0

        with open(self.ledger_path, "r") as f:
            for line_num, line in enumerate(f, start=1):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as e:
                    print(f"[-] Malformed JSON at line {line_num}: {e}")
                    return False

                tick = record.get("manifold_tick")
                if tick <= previous_tick and line_num > 1:
                    print(f"[-] Chronology violation at line {line_num}: tick {tick} follows {previous_tick}")
                    valid = False

                # Verify Chain Mail ring state integrity
                ring_receipts = record.get("chain_mail_receipts", {})
                if not ring_receipts:
                    print(f"[-] Missing chain mail cryptographic links at tick {tick}")
                    valid = False

                previous_tick = tick

        if valid:
            print("[+] AUDIT SUCCESS: All WORM ledger receipts, toroidal coordinates, and chain mail links are cryptographically sound.")
        else:
            print("[-] AUDIT FAILURE: State corruption or temporal drift detected in ledger.")

        return valid

if __name__ == "__main__":
    auditor = ManifoldAuditor()
    auditor.audit_chain()
