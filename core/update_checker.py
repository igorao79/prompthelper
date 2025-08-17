import json
import os
from dataclasses import dataclass
from typing import Optional

import requests

GITHUB_API_BRANCH = "https://api.github.com/repos/igorao79/prompthelper/branches/linux"
GITHUB_ZIP_URL = "https://github.com/igorao79/prompthelper/archive/refs/heads/linux.zip"


@dataclass
class UpdateInfo:
    available: bool
    latest_sha: str
    zip_url: str = GITHUB_ZIP_URL
    binary_url: Optional[str] = None
    message: str = ""


class UpdateChecker:
    def __init__(self, settings_manager):
        self.settings = settings_manager

    def check(self) -> UpdateInfo:
        try:
            if not self.settings.get_auto_check_updates():
                return UpdateInfo(False, self.settings.get_last_update_sha(), message="Auto-check disabled")

            resp = requests.get(GITHUB_API_BRANCH, timeout=10)
            if resp.status_code != 200:
                return UpdateInfo(False, self.settings.get_last_update_sha(), message=f"HTTP {resp.status_code}")

            data = resp.json()
            latest_sha = data.get("commit", {}).get("sha", "")
            prev_sha = self.settings.get_last_update_sha()

            # Ищем бинарный релиз LandGen.exe (опционально)
            binary_url = self._get_latest_release_binary_url()

            if latest_sha and latest_sha != prev_sha:
                return UpdateInfo(True, latest_sha, GITHUB_ZIP_URL, binary_url)

            return UpdateInfo(False, latest_sha or prev_sha, GITHUB_ZIP_URL, binary_url)

        except Exception as e:
            return UpdateInfo(False, self.settings.get_last_update_sha(), message=str(e)[:200])

    def accept_update(self, latest_sha: str):
        try:
            self.settings.set_last_update_sha(latest_sha)
        except Exception:
            pass

    def _get_latest_release_binary_url(self) -> Optional[str]:
        try:
            releases_api = "https://api.github.com/repos/igorao79/prompthelper/releases/latest"
            r = requests.get(releases_api, timeout=10)
            if r.status_code != 200:
                return None
            data = r.json()
            assets = data.get("assets", [])
            for a in assets:
                url = a.get("browser_download_url")
                name = a.get("name", "")
                if url and name and name.lower().endswith(".exe") and "landgen" in name.lower():
                    return url
            return None
        except Exception:
            return None


