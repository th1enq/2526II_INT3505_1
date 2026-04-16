from __future__ import annotations

import argparse
import json
import os
import statistics
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
import psycopg

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/pagination_demo",
)


@dataclass
class TimingResult:
    strategy: str
    scenario: str
    depth: int
    page_size: int
    runs: int
    latencies_ms: list[float]

    @property
    def avg_ms(self) -> float:
        return statistics.fmean(self.latencies_ms)

    @property
    def p95_ms(self) -> float:
        if len(self.latencies_ms) < 2:
            return self.latencies_ms[0]
        return statistics.quantiles(self.latencies_ms, n=20)[-1]


def connect() -> psycopg.Connection:
    return psycopg.connect(DATABASE_URL)


def ensure_schema(conn: psycopg.Connection) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS items (
                id BIGSERIAL PRIMARY KEY,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                payload TEXT NOT NULL
            );
            """
        )
    #     cur.execute(
    #         """
    #         CREATE INDEX IF NOT EXISTS idx_items_created_at_id_desc
    #         ON items (created_at DESC, id DESC);
    #         """
    #     )
    conn.commit()


def seed_if_needed(conn: psycopg.Connection, target_rows: int) -> int:
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM items")
        current_rows = cur.fetchone()[0]

    if current_rows >= target_rows:
        return current_rows

    to_insert = target_rows - current_rows
    print(f"Seeding {to_insert:,} rows...")

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO items (created_at, payload)
            SELECT NOW() - (gs || ' seconds')::interval,
                   md5(random()::text)
            FROM generate_series(1, %s) AS gs
            """,
            (to_insert,),
        )
    conn.commit()

    with conn.cursor() as cur:
        cur.execute("ANALYZE items")
    conn.commit()

    return target_rows


def _time_query(conn: psycopg.Connection, query: str, params: tuple[Any, ...]) -> float:
    started = time.perf_counter()
    with conn.cursor() as cur:
        cur.execute(query, params)
        cur.fetchall()
    ended = time.perf_counter()
    return (ended - started) * 1000


def _bench_offset_limit(
    conn: psycopg.Connection,
    *,
    strategy: str,
    depth: int,
    page_size: int,
    runs: int,
) -> TimingResult:
    offset = depth * page_size
    query = """
        SELECT id, created_at, payload
        FROM items
        ORDER BY created_at DESC, id DESC
        OFFSET %s
        LIMIT %s
    """
    latencies = [_time_query(conn, query, (offset, page_size)) for _ in range(runs)]
    return TimingResult(strategy, "deep_jump", depth, page_size, runs, latencies)


def bench_offset(conn: psycopg.Connection, depth: int, page_size: int, runs: int) -> TimingResult:
    return _bench_offset_limit(
        conn,
        strategy="offset",
        depth=depth,
        page_size=page_size,
        runs=runs,
    )


def bench_page_size(conn: psycopg.Connection, depth: int, page_size: int, runs: int) -> TimingResult:
    return _bench_offset_limit(
        conn,
        strategy="page-size",
        depth=depth,
        page_size=page_size,
        runs=runs,
    )


def bench_cursor_scan(conn: psycopg.Connection, depth: int, page_size: int, runs: int) -> TimingResult:
    query_first = """
        SELECT id, created_at
        FROM items
        ORDER BY created_at DESC, id DESC
        LIMIT %s
    """
    query_next = """
        SELECT id, created_at
        FROM items
        WHERE (created_at, id) < (%s, %s)
        ORDER BY created_at DESC, id DESC
        LIMIT %s
    """

    latencies = []
    for _ in range(runs):
        last_created_at = None
        last_id = None
        run_started = time.perf_counter()

        for step in range(depth + 1):
            with conn.cursor() as cur:
                if step == 0:
                    cur.execute(query_first, (page_size,))
                else:
                    cur.execute(query_next, (last_created_at, last_id, page_size))
                rows = cur.fetchall()

            if not rows:
                break

            last_id = rows[-1][0]
            last_created_at = rows[-1][1]

        run_ended = time.perf_counter()
        latencies.append((run_ended - run_started) * 1000)

    return TimingResult("cursor", "sequential_scan_to_depth", depth, page_size, runs, latencies)


def generate_report(results: list[TimingResult], output_path: Path) -> None:
    report = {
        "generated_at": datetime.now(UTC).isoformat(),
        "results": [
            {
                "strategy": item.strategy,
                "scenario": item.scenario,
                "depth": item.depth,
                "page_size": item.page_size,
                "runs": item.runs,
                "avg_ms": round(item.avg_ms, 3),
                "p95_ms": round(item.p95_ms, 3),
                "raw_ms": [round(x, 3) for x in item.latencies_ms],
            }
            for item in results
        ],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")


def print_table(results: list[TimingResult]) -> None:
    header = (
        f"{'strategy':<12} {'scenario':<28} {'depth':>7} {'size':>6} "
        f"{'avg(ms)':>10} {'p95(ms)':>10}"
    )
    print(header)
    print("-" * len(header))
    for item in results:
        print(
            f"{item.strategy:<12} {item.scenario:<28} {item.depth:>7} "
            f"{item.page_size:>6} {item.avg_ms:>10.3f} {item.p95_ms:>10.3f}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark pagination strategies")
    parser.add_argument("--rows", type=int, default=1_000_000, help="Target row count")
    parser.add_argument("--page-size", type=int, default=50, help="Page size")
    parser.add_argument(
        "--depths",
        type=int,
        nargs="+",
        default=[10, 100, 1000, 5000],
        help="Depths (0-based page index) to benchmark",
    )
    parser.add_argument("--runs", type=int, default=5, help="Runs per scenario")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("docs/benchmark_results.json"),
        help="Output JSON path",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.page_size <= 0 or args.rows <= 0 or args.runs <= 0:
        raise ValueError("rows, page-size, and runs must be positive")

    with connect() as conn:
        ensure_schema(conn)
        total_rows = seed_if_needed(conn, args.rows)
        print(f"Rows in table: {total_rows:,}")

        all_results: list[TimingResult] = []
        for depth in args.depths:
            if depth < 0:
                raise ValueError("Depth must be >= 0")

            all_results.append(bench_offset(conn, depth, args.page_size, args.runs))
            all_results.append(bench_page_size(conn, depth, args.page_size, args.runs))
            all_results.append(bench_cursor_scan(conn, depth, args.page_size, args.runs))

        print_table(all_results)
        generate_report(all_results, args.out)
        print(f"\nSaved report to {args.out}")


if __name__ == "__main__":
    main()
