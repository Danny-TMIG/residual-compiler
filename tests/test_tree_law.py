import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from tree import Verdict, classify


def test_pass_complete_with_natives_raises():
    with pytest.raises(ValueError, match="unrepresentable"):
        Verdict(
            "PASS-COMPLETE",
            "should be impossible",
            native_count=1,
            native_hits=("numpy==1.0",),
        )


def test_pass_complete_with_zero_natives_ok():
    v = Verdict("PASS-COMPLETE", "clean", native_count=0, native_hits=())
    assert v.exit_code == 0


def test_fail_incomplete_with_natives():
    v = Verdict(
        "FAIL-INCOMPLETE",
        "natives present",
        native_count=1,
        native_hits=("numpy==1.0",),
    )
    assert v.exit_code == 1


def test_fail_vuln():
    v = Verdict("FAIL-VULN", "audit failed", native_count=0, native_hits=())
    assert v.exit_code == 1


def test_unknown_status_rejected():
    with pytest.raises(ValueError):
        Verdict("MAYBE", "nope", native_count=0, native_hits=())


def test_classify_pure_python(tmp_path):
    f = tmp_path / "freeze.txt"
    f.write_text("pytest==7.0\nrequests==2.31\n")
    v = classify(f, audit_failed=False)
    assert v.status == "PASS-COMPLETE"


def test_classify_native_dep(tmp_path):
    f = tmp_path / "freeze.txt"
    f.write_text("numpy==1.26.0\npytest==7.0\n")
    v = classify(f, audit_failed=False)
    assert v.status == "FAIL-INCOMPLETE"


def test_classify_audit_failure_wins(tmp_path):
    f = tmp_path / "freeze.txt"
    f.write_text("numpy==1.26.0\n")
    v = classify(f, audit_failed=True)
    assert v.status == "FAIL-VULN"
