"""Canonical rule set. Regenerate data/policy.json with:
python -m src.policy_builder_cli build
"""

RULES = [
    # -------------------- allow (low risk) --------------------
    {"id": "allow-search", "when": {"operation": "search"}, "then": "ALLOW"},
    {"id": "allow-learn", "when": {"operation": "learn"}, "then": "ALLOW"},
    # -------------------- escalate (medium risk: needs change approval) ----
    {
        "id": "execute-dev-needs-approval",
        "when": {"operation": "execute", "target_env": "dev"},
        "then": "ESCALATE",
        "requires": ["change_approved"],
    },
    {
        "id": "execute-staging-needs-approval",
        "when": {"operation": "execute", "target_env": "staging"},
        "then": "ESCALATE",
        "requires": ["change_approved"],
    },
    {
        "id": "execute-prod-needs-approval-and-incident-free",
        "when": {"operation": "execute", "target_env": "prod"},
        "then": "ESCALATE",
        "requires": ["change_approved", "incident_free"],
    },
    {
        "id": "deploy-dev-needs-approval",
        "when": {"operation": "deploy", "target_env": "dev"},
        "then": "ESCALATE",
        "requires": ["change_approved"],
    },
    {
        "id": "deploy-staging-needs-approval",
        "when": {"operation": "deploy", "target_env": "staging"},
        "then": "ESCALATE",
        "requires": ["change_approved"],
    },
    # -------------------- deny (high risk: unconditional in this build) ----
    {
        "id": "no-unapproved-prod-deploy",
        "when": {"operation": "deploy", "target_env": "prod"},
        "then": "DENY",
        "reason": "prod deploy requires signed release + incident-free attestation; "
        "neither is implemented in this build, so the gate refuses unconditionally",
    },
]
DEFAULT = "DENY"
