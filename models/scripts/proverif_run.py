import argparse
import csv
from datetime import datetime
from pathlib import Path
import re
import subprocess
import time

BASE_DIR = Path(__file__).resolve().parents[1]
PROVERIF_DIR = BASE_DIR / "proverif"
RESULTS_DIR = BASE_DIR / "results"

QUERY_NAME_RE = re.compile(r"^\(\*\s*([A-Za-z0-9_]+)\s*\*\)\s*$")
RESULT_RE = re.compile(r"^RESULT\s+(.+?)\s+is\s+(true|false|cannot be proved)\.\s*$")


def default_output_csv():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return RESULTS_DIR / f"proverif_results_{timestamp}.csv"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run ProVerif on .pv files and log one CSV row per query."
    )
    parser.add_argument(
        "--root",
        default=str(PROVERIF_DIR),
        help="Root directory containing .pv files.",
    )
    parser.add_argument(
        "--output",
        default=str(default_output_csv()),
        help="CSV file to write results into.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=0,
        help="Kill a single ProVerif run after this many seconds. Use 0 to disable.",
    )
    parser.add_argument(
        "--pattern",
        default="*.pv",
        help="Glob pattern under --root for selecting files.",
    )
    return parser.parse_args()


def discover_files(root: Path, pattern: str):
    return sorted(path for path in root.rglob(pattern) if path.is_file())


def extract_query_names(file_path: Path):
    query_names = []
    pending_name = None

    for raw_line in file_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()

        comment_match = QUERY_NAME_RE.match(line)
        if comment_match:
            pending_name = comment_match.group(1)
            continue

        if not line:
            continue

        if line.startswith("query "):
            query_names.append(pending_name or f"query_{len(query_names) + 1}")
            pending_name = None
            continue

        if not line.startswith("(*"):
            pending_name = None

    return query_names


def infer_flags(file_path: Path):
    stem_lower = file_path.stem.lower()
    flags = []

    if "leakshare" in stem_lower:
        flags.append("LeakShare")
    if "leaksessionkey" in stem_lower:
        flags.append("LeakSessionKey")
    if "leakskey" in stem_lower:
        flags.append("LeakSKey")
    if "quantum" in stem_lower or "quantum" in {part.lower() for part in file_path.parts}:
        flags.append("PQDL")

    return " ".join(flags) if flags else "None"


def parse_results(output_text: str):
    results = []
    for line in output_text.splitlines():
        match = RESULT_RE.match(line.strip())
        if match:
            raw_query, status = match.groups()
            results.append((raw_query, status))
    return results


def run_proverif(file_path: Path, timeout_seconds: int):
    cmd = ["proverif", str(file_path)]
    started_at = time.time()

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_seconds if timeout_seconds > 0 else None,
        )
        wall_time = time.time() - started_at
        output = proc.stdout + proc.stderr
        return {
            "status": "completed",
            "returncode": proc.returncode,
            "wall_time": wall_time,
            "output": output,
        }
    except subprocess.TimeoutExpired as exc:
        wall_time = time.time() - started_at
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode(errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode(errors="replace")
        return {
            "status": "timeout",
            "returncode": None,
            "wall_time": wall_time,
            "output": stdout + stderr,
        }


def main():
    args = parse_args()
    root = Path(args.root).resolve()
    output_csv = Path(args.output).resolve()
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    files = discover_files(root, args.pattern)

    with output_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["File", "QueryName", "Result", "Time(s)", "Flags"])

        for file_path in files:
            rel_path = file_path.relative_to(BASE_DIR)
            query_names = extract_query_names(file_path)
            flags = infer_flags(file_path)

            print(f"Running {rel_path} with flags: {flags}", flush=True)
            run = run_proverif(file_path, args.timeout)
            parsed_results = parse_results(run["output"])

            if run["status"] == "timeout":
                for query_name in query_names or ["unknown"]:
                    writer.writerow([str(rel_path), query_name, "timeout", f"{run['wall_time']:.2f}", flags])
                f.flush()
                print(f"Timed out after {run['wall_time']:.2f}s", flush=True)
                continue

            if not parsed_results:
                for query_name in query_names or ["unknown"]:
                    writer.writerow([str(rel_path), query_name, f"error({run['returncode']})", f"{run['wall_time']:.2f}", flags])
                f.flush()
                print(f"No parseable results for {rel_path} (rc={run['returncode']})", flush=True)
                continue

            for index, (raw_query, status) in enumerate(parsed_results):
                query_name = query_names[index] if index < len(query_names) else raw_query
                writer.writerow([str(rel_path), query_name, status, f"{run['wall_time']:.2f}", flags])

            f.flush()
            print(
                f"Completed {rel_path} -> {len(parsed_results)} queries, {run['wall_time']:.2f}s",
                flush=True,
            )

    print(f"\nResults written to {output_csv}", flush=True)


if __name__ == "__main__":
    main()
