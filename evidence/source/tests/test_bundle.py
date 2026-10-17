from src import bundle


def test_det():
    assert (
        bundle.bundle([{"id": "x"}])["sha256"] == bundle.bundle([{"id": "x"}])["sha256"]
    )


def test_dist():
    assert (
        bundle.bundle([{"id": "x"}])["sha256"] != bundle.bundle([{"id": "y"}])["sha256"]
    )
