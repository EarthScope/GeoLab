"""Helpers for smoke-testing installed packages and CLI tools."""

import importlib
import shutil
import subprocess

RESULTS = []


def reset():
    """Clear RESULTS — call before a fresh run in a long-lived kernel."""
    RESULTS.clear()


def py(modname, alias=None, smoke=None):
    """Import `modname` and optionally run `smoke(mod)` as a sanity check."""
    label = alias or modname
    try:
        mod = importlib.import_module(modname)
        if smoke is not None:
            smoke(mod)
        version = getattr(mod, '__version__', '')
        RESULTS.append((label, 'OK', str(version), ''))
    except Exception as exc:
        RESULTS.append((label, 'FAIL', '', f'{type(exc).__name__}: {exc}'))


def cli(cmd, version_flag='--version'):
    """Verify `cmd` is on $PATH and responds to a version flag."""
    path = shutil.which(cmd)
    if not path:
        RESULTS.append((cmd, 'FAIL', '', 'not on $PATH'))
        return
    try:
        r = subprocess.run([cmd, version_flag],
                           capture_output=True, text=True, timeout=10)
        line = (r.stdout or r.stderr).strip().splitlines()
        version = line[0] if line else 'on PATH'
        RESULTS.append((cmd, 'OK', version[:80], ''))
    except Exception as exc:
        RESULTS.append((cmd, 'OK', 'on PATH', f'{type(exc).__name__}'))
