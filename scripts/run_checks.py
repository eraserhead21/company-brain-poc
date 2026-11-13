"""Run every check with one command. Exit code 1 if any check fails.

  1. unit tests            python -m unittest discover -s tests
  2. redaction patterns    scripts/redaction_check.py
  3. provenance            scripts/provenance_check.py
  4. relations             scripts/relations_check.py
  5. answer keys           tests/score.py --auto, once for each key

Steps 2 to 4 are the gate that capture runs. Steps 1 and 5 read tests/, so a
person or CI runs them, never capture.

Step 5 fails on a leaked planted value or name. It prints the script-marked
judgement tests and does not fail on them: each key was written for the
sources of its own round, and a later document can change the right answer.

Usage: python scripts/run_checks.py [--keys seeds.json holdout.json ...]
"""
import argparse
import subprocess
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent


def run(title, *cmd):
    print(f"\n=== {title}", flush=True)
    done = subprocess.run([sys.executable, *cmd], cwd=ROOT)
    print(f"--- {title}: {'ok' if done.returncode == 0 else 'FAILED'}", flush=True)
    return done.returncode == 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--keys", nargs="*")
    args = ap.parse_args(argv)
    keys = args.keys or sorted(p.name for p in (ROOT / "tests" / "answers").glob("*.json")
                               if '"redaction_seeds"' in p.read_text(encoding="utf-8"))
    results = {
        "unit tests": run("unit tests", "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"),
        "redaction": run("redaction", "scripts/redaction_check.py", "learnings/approved", "brief.md", "relations.json"),
        "provenance": run("provenance", "scripts/provenance_check.py", "--no-review"),
        "relations": run("relations", "scripts/relations_check.py"),
    }
    for key in keys:
        results[f"answer key {key}"] = run(f"answer key {key}", "tests/score.py", "--key", key, "--auto")
    print("\n=== summary")
    for name, ok in results.items():
        print(f"  {'ok    ' if ok else 'FAILED'} {name}")
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
