from src.triad import SovereignTriadNode
from src.telemetry import UnifiedTelemetryFacade


def test_triad(tmp_path):
    n = SovereignTriadNode(db_path=str(tmp_path / "t.db"))
    n.write_state(1, "W", "ACTIVE", {"x": True})
    assert n.run_codeql_invariant_check()


def test_tel():
    t = UnifiedTelemetryFacade()
    t.record_cycle(42, "OK")
    txt = t.prometheus.export_text_format()
    assert "sovereign_manifold_tick_current 42" in txt
    assert "sovereign_manifold_health_status 1.0" in txt
