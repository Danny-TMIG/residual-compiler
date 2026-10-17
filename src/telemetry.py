class _Prom:
    def __init__(self):
        self.v = 0.0

    def gauge(self, name, val, labels=None):
        self.v = float(val)

    def export_text_format(self):
        return f"sovereign_manifold_tick_current {int(self.v)}\nsovereign_manifold_health_status 1.0\n"


class UnifiedTelemetryFacade:
    def __init__(self):
        self.prometheus = _Prom()

    def record_cycle(self, tick, status):
        self.prometheus.gauge("tick", tick)
