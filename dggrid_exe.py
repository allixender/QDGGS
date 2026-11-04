"""portable DGGRID from github.com/allixender/DGGRID_portables (adapted from dggrid4py.tool)"""
import hashlib
import os
import platform
import stat
import subprocess
import tarfile
import tempfile
import zipfile

from qgis.core import QgsApplication, QgsBlockingNetworkRequest, QgsSettings
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtNetwork import QNetworkRequest

RELEASE = "v9.1"
URL = "https://github.com/allixender/DGGRID_portables/releases/download"

_assets = {
    ('linux', 'x86_64'): 'dggrid-linux-x86_64.tar.gz',
    ('linux', 'arm64'): 'dggrid-linux-arm64.tar.gz',
    ('darwin', 'x86_64'): 'dggrid-macos-x86_64.tar.gz',
    ('darwin', 'arm64'): 'dggrid-macos-arm64.tar.gz',
    ('windows', 'x86_64'): 'dggrid-windows-x86_64.zip',
    ('windows', 'arm64'): 'dggrid-windows-arm64.zip',
}
_machine_aliases = {'amd64': 'x86_64', 'x64': 'x86_64', 'aarch64': 'arm64'}


def assetName():
    machine = platform.machine().lower()
    return _assets.get((platform.system().lower(), _machine_aliases.get(machine, machine)))


def portableDir():
    return os.path.join(QgsApplication.qgisSettingsDirPath(), "dggrid_portable", RELEASE)


def _marker():
    return os.path.join(portableDir(), "executable.txt")


def cachedExe():
    try:
        with open(_marker()) as f:
            exe = os.path.join(portableDir(), f.read().strip())
    except OSError:
        return None
    return exe if os.path.isfile(exe) else None


def findExe():
    # own dggrid (eg conda, with GDAL) via advanced settings, else the pinned portable
    own = QgsSettings().value("dggrid/executable", "")
    if own and os.path.isfile(own):
        return own
    return cachedExe()


def _get(url):
    req = QgsBlockingNetworkRequest()
    if req.get(QNetworkRequest(QUrl(url)), True) != QgsBlockingNetworkRequest.ErrorCode.NoError:
        raise IOError(f"download failed: {url}\n{req.errorMessage()}")
    return bytes(req.reply().content())


def _checksum(asset):
    for line in _get(f"{URL}/{RELEASE}/SHA256SUMS").decode().splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1].lstrip('*') == asset:
            return parts[0].lower()
    raise ValueError(f"no checksum for {asset} in {RELEASE}")


def _extract(archive, folder):
    root = os.path.realpath(folder)
    is_zip = archive.endswith('.zip')
    with (zipfile.ZipFile(archive) if is_zip else tarfile.open(archive, 'r:gz')) as a:
        names = a.namelist() if is_zip else a.getnames()
        for n in names:
            if not os.path.realpath(os.path.join(folder, n)).startswith(root + os.sep):
                raise ValueError(f"unsafe path in archive: {n}")
        if not is_zip and hasattr(tarfile, 'data_filter'):
            a.extractall(folder, filter='data')
        else:
            a.extractall(folder)
    for n in names:
        if os.path.basename(n) in ('dggrid', 'dggrid.exe'):
            return n
    raise ValueError("no dggrid executable in archive")


def downloadExe():
    asset = assetName()
    if asset is None:
        raise ValueError(f"no portable DGGRID for {platform.system()} {platform.machine()}")
    folder = portableDir()
    os.makedirs(folder, exist_ok=True)
    checksum = _checksum(asset)
    data = _get(f"{URL}/{RELEASE}/{asset}")
    if hashlib.sha256(data).hexdigest() != checksum:
        raise ValueError(f"checksum mismatch for {asset}")
    with tempfile.TemporaryDirectory(dir=folder) as tmp:
        archive = os.path.join(tmp, asset)
        with open(archive, 'wb') as f:
            f.write(data)
        rel = _extract(archive, folder)
    exe = os.path.join(folder, rel)
    os.chmod(exe, os.stat(exe).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    if platform.system() == 'Darwin':
        # not notarised
        subprocess.run(['xattr', '-d', 'com.apple.quarantine', exe], capture_output=True)
    with open(_marker(), 'w') as f:
        f.write(rel)
    return exe
