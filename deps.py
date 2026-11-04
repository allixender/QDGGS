"""optional py deps (h3) installed into the QGIS profile, per python version"""
import os
import shutil
import subprocess
import sys

from qgis.core import QgsApplication

PYVER = f"{sys.version_info[0]}.{sys.version_info[1]}"


def depsDir():
    return os.path.join(QgsApplication.qgisSettingsDirPath(), "python", "dggrid_deps", "py" + PYVER.replace(".", ""))


def addDepsPath():
    d = depsDir()
    if os.path.isdir(d) and d not in sys.path:
        sys.path.append(d)


def _run(cmd, env=None):
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    return subprocess.run(cmd, env=env, capture_output=True, text=True, creationflags=flags)


def _env():
    # bundled pythons (mac) don't find their stdlib on their own
    return dict(os.environ, PYTHONPATH=os.pathsep.join(p for p in sys.path if p))


def pythonExe():
    # sys.executable is the QGIS binary on win/mac
    if os.name == "nt":
        names = ["python.exe", "python3.exe"]
    else:
        names = ["python" + PYVER, "python3", "python"]
    dirs = [os.path.dirname(sys.executable), sys.exec_prefix, os.path.join(sys.exec_prefix, "bin")]
    cands = [os.path.join(d, n) for d in dirs for n in names]
    cands += [shutil.which(n) for n in names]
    for p in cands:
        if not p or not os.path.isfile(p):
            continue
        try:
            r = _run([p, "-c", "import sys; print('%d.%d' % sys.version_info[:2])"], _env())
        except OSError:
            continue
        if r.returncode == 0 and r.stdout.strip() == PYVER:
            return p
    return None


def pipCmd(pkgs):
    py = pythonExe() or "python3"
    return [py, "-m", "pip", "install", "--target", depsDir(), "--only-binary", ":all:"] + list(pkgs)


def pipInstall(pkgs):
    """returns (ok, log)"""
    if pythonExe() is None:
        return False, f"no python {PYVER} interpreter found"
    os.makedirs(depsDir(), exist_ok=True)
    r = _run(pipCmd(pkgs), _env())
    addDepsPath()
    return r.returncode == 0, r.stdout + r.stderr
