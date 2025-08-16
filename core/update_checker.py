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

            if latest_sha and latest_sha != prev_sha:
                return UpdateInfo(True, latest_sha)

            return UpdateInfo(False, latest_sha or prev_sha)

        except Exception as e:
            return UpdateInfo(False, self.settings.get_last_update_sha(), message=str(e)[:200])

    def accept_update(self, latest_sha: str):
        try:
            self.settings.set_last_update_sha(latest_sha)
        except Exception:
            pass


