import socket
import urllib.error
import urllib.request
from pathlib import Path


class NetworkError(Exception):
    pass


def check_url(url, timeout=5):
    """Check whether a remote resource can be reached."""
    if not url:
        raise NetworkError("URL cannot be empty.")

    request = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return {
                "ok": True,
                "status": response.status,
                "content_type": response.headers.get("Content-Type", ""),
                "length": response.headers.get("Content-Length", ""),
            }
    except urllib.error.HTTPError as exc:
        if exc.code == 405:
            return _fallback_get(url, timeout)
        raise NetworkError(f"HTTP error: {exc.code}") from exc
    except (urllib.error.URLError, socket.timeout) as exc:
        raise NetworkError(f"Network request failed: {exc}") from exc


def _fallback_get(url, timeout):
    request = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return {
                "ok": True,
                "status": response.status,
                "content_type": response.headers.get("Content-Type", ""),
                "length": response.headers.get("Content-Length", ""),
            }
    except (urllib.error.URLError, socket.timeout) as exc:
        raise NetworkError(f"Network request failed: {exc}") from exc


def download_file(url, target_path, timeout=30):
    """Download a resource such as a model weight file with exception handling."""
    target = Path(target_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            with target.open("wb") as file:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    file.write(chunk)
    except (urllib.error.URLError, socket.timeout, OSError) as exc:
        raise NetworkError(f"Download failed: {exc}") from exc
    return target
