#!/usr/bin/env python3
"""
SD-Toolx dev runner — starts Django + optional Celery worker/beat.
Usage: python durga.py
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV_PYTHON = ROOT / ".venv" / "bin" / "python"
PYTHON = str(VENV_PYTHON if VENV_PYTHON.exists() else sys.executable)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.dev")
os.chdir(ROOT)


def clear_pycache():
    for path in ROOT.rglob("__pycache__"):
        shutil.rmtree(path, ignore_errors=True)


def run(cmd, **kwargs):
    return subprocess.Popen(cmd, cwd=ROOT, **kwargs)


def main():
    clear_pycache()
    print("\n🚀 SD-Toolx dev server\n")

    # Migrations + seed
    subprocess.run([PYTHON, "manage.py", "migrate", "--noinput"], check=False)
    subprocess.run([PYTHON, "manage.py", "seed_plans"], check=False)
    subprocess.run([PYTHON, "manage.py", "create_test_user"], check=False)
    subprocess.run([PYTHON, "manage.py", "seed_blog"], check=False)

    # Celery if Redis available
    celery_procs = []
    try:
        import redis

        r = redis.from_url(os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/0"))
        r.ping()
        celery_procs.append(
            run([PYTHON, "-m", "celery", "-A", "core", "worker", "-l", "info", "-Q", "default,priority"])
        )
        celery_procs.append(run([PYTHON, "-m", "celery", "-A", "core", "beat", "-l", "info"]))
        print("✓ Celery worker + beat started (Redis OK)")
    except Exception:
        print("⚠ Redis not running — Celery skipped (runserver still works)")

    server = run([PYTHON, "manage.py", "runserver", "0.0.0.0:8000"])

    print("\n──────────────────────────────────────")
    print("  App:    http://127.0.0.1:8000/")
    print("  Admin:  http://127.0.0.1:8000/sd/")
    print("  Test:   test@sdtoolx.com / Test@1234")
    print("──────────────────────────────────────\n")

    try:
        server.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        for p in celery_procs:
            p.terminate()


if __name__ == "__main__":
    main()
