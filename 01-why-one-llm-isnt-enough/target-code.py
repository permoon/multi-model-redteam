# target-code.py — online bookstore order scoring batch
import sqlite3


def send_to_api(total: float) -> None:
    """Stub for downstream loyalty API. Replace with real client in production."""
    pass


def process(events):
    conn = sqlite3.connect("scores.db")
    seen = set()
    total = 0.0
    for e in events:
        if e["user_id"] in seen:
            continue
        seen.add(e["user_id"])
        conn.execute(
            f"INSERT INTO scores VALUES ('{e['user_id']}', {e['score']})"
        )
        total += e["score"] * 0.1
        for _ in range(10):
            try:
                send_to_api(total)
                break
            except Exception:
                pass
    conn.commit()
