"""
End-to-End Pipeline Validation Harness.

Executes the entire data lifecycle sequentially:
1. Python Ingestion Pipeline (extract -> validate -> load -> audit)
2. dbt Models & Automated Tests (staging -> intermediate -> marts -> 104 data tests)
3. 5-Pillar Data Quality Audit
4. Multi-Layer Financial & Record Reconciliation
5. Pytest Unit & Integration Suite
6. Power BI Parquet Marts Export
"""

import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

def run_step(step_name: str, cmd: list, cwd: Path = REPO_ROOT):
    print(f"\n{'='*80}")
    print(f">> RUNNING STEP: {step_name}")
    print(f"   Command: {' '.join(cmd)}")
    print(f"{'='*80}")
    start = time.time()
    res = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
    duration = time.time() - start
    
    if res.returncode == 0:
        print(f"[PASS] {step_name} completed in {duration:.2f}s.")
        if res.stdout:
            # Print last few lines
            lines = res.stdout.strip().splitlines()
            print("   Output summary:")
            for l in lines[-5:]:
                print(f"   | {l}")
        return True
    else:
        print(f"[FAIL] {step_name} failed with return code {res.returncode} in {duration:.2f}s.")
        print("--- STDERR ---")
        print(res.stderr)
        print("--- STDOUT ---")
        print(res.stdout)
        return False

def main():
    print("================================================================================")
    print("STARTING COMPLETE END-TO-END VALIDATION HARNESS")
    print("================================================================================")

    steps = [
        ("1. Python Ingestion Pipeline", [sys.executable, "ingestion/pipeline.py"], REPO_ROOT),
        ("2. dbt Full Build & Tests", ["dbt", "build", "--profiles-dir", "."], REPO_ROOT / "dbt"),
        ("3. Data Quality Framework Audit", [sys.executable, "scripts/run_quality_checks.py"], REPO_ROOT),
        ("4. Pytest Test Suite", [sys.executable, "-m", "pytest", "tests/"], REPO_ROOT),
        ("5. Power BI Marts Export", [sys.executable, "scripts/export_marts_for_powerbi.py"], REPO_ROOT),
    ]

    all_passed = True
    for name, cmd, cwd in steps:
        if not run_step(name, cmd, cwd):
            all_passed = False
            break

    print("\n" + "="*80)
    if all_passed:
        print(">> ALL END-TO-END VALIDATION STAGES COMPLETED WITH 100% SUCCESS <<")
    else:
        print(">> END-TO-END VALIDATION ENCOUNTERED FAILURES <<")
    print("="*80)

    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
