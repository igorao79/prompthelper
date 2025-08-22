import json
import os
from dataclasses import dataclass
from typing import Optional, Tuple
from core.version import VERSION as LOCAL_VERSION

import requests

GITHUB_API_BRANCH = "https://api.github.com/repos/igorao79/prompthelper/branches/linux"
GITHUB_ZIP_URL = "https://github.com/igorao79/prompthelper/archive/refs/heads/linux.zip"


@dataclass
class UpdateInfo:
    available: bool
    latest_sha: str
    zip_url: str = GITHUB_ZIP_URL
    binary_url: Optional[str] = None
    version: str = ""
    message: str = ""


class UpdateChecker:
    def __init__(self, settings_manager):
        self.settings = settings_manager

    def check(self) -> UpdateInfo:
        try:
            if not self.settings.get_auto_check_updates():
                return UpdateInfo(False, self.settings.get_last_update_sha(), message="Auto-check disabled")

            # Предпочитаем релизную модель обновлений: сравнение тегов версий
            binary_url, version = self._get_latest_release_binary_url()
            cur_ver = (LOCAL_VERSION or "").lower().lstrip('v')
            rel_ver = (version or "").lower().lstrip('v')
            if rel_ver and (cur_ver != rel_ver) and ('dev' in cur_ver or cur_ver != rel_ver):
                # Сохраняем маркер последнего известного релиза
                return UpdateInfo(True, rel_ver, GITHUB_ZIP_URL, binary_url, rel_ver)

            # Фоллбек на проверку ветки (для дев/ручных тестов)
            resp = requests.get(GITHUB_API_BRANCH, timeout=10)
            if resp.status_code != 200:
                return UpdateInfo(False, self.settings.get_last_update_sha(), message=f"HTTP {resp.status_code}")
            data = resp.json()
            latest_sha = data.get("commit", {}).get("sha", "")
            prev_sha = self.settings.get_last_update_sha()
            if latest_sha and latest_sha != prev_sha:
                return UpdateInfo(True, latest_sha, GITHUB_ZIP_URL, binary_url, rel_ver or (latest_sha[:7] if latest_sha else ""))

            return UpdateInfo(False, latest_sha or prev_sha, GITHUB_ZIP_URL, binary_url, rel_ver or (latest_sha[:7] if latest_sha else ""))

        except Exception as e:
            return UpdateInfo(False, self.settings.get_last_update_sha(), message=str(e)[:200])

    def check_force(self) -> UpdateInfo:
        """То же что check(), но игнорирует настройку auto_check_updates."""
        try:
            resp = requests.get(GITHUB_API_BRANCH, timeout=10)
            if resp.status_code != 200:
                return UpdateInfo(False, self.settings.get_last_update_sha(), message=f"HTTP {resp.status_code}")

            data = resp.json()
            latest_sha = data.get("commit", {}).get("sha", "")
            prev_sha = self.settings.get_last_update_sha()

            binary_url, version = self._get_latest_release_binary_url()

            if latest_sha and latest_sha != prev_sha:
                return UpdateInfo(True, latest_sha, GITHUB_ZIP_URL, binary_url, version or (latest_sha[:7] if latest_sha else ""))

            return UpdateInfo(False, latest_sha or prev_sha, GITHUB_ZIP_URL, binary_url, version or (latest_sha[:7] if latest_sha else ""))
        except Exception as e:
            return UpdateInfo(False, self.settings.get_last_update_sha(), message=str(e)[:200])

    def accept_update(self, latest_sha: str):
        try:
            self.settings.set_last_update_sha(latest_sha)
        except Exception:
            pass

    def _get_latest_release_binary_url(self) -> Tuple[Optional[str], Optional[str]]:
        try:
            releases_api = "https://api.github.com/repos/igorao79/prompthelper/releases/latest"
            r = requests.get(releases_api, timeout=10)
            if r.status_code != 200:
                return None, None
            data = r.json()
            version = data.get("tag_name") or data.get("name") or None
            assets = data.get("assets", [])
            # Ищем zip-архив с exe (предпочтительно) или сам .exe
            zip_url = None
            exe_url = None
            for a in assets:
                url = a.get("browser_download_url")
                name = a.get("name", "")
                lname = name.lower()
                if url and lname.endswith(".zip") and "landgen" in lname:
                    zip_url = url
                if url and lname.endswith(".exe") and "landgen" in lname:
                    exe_url = url
            return (zip_url or exe_url), version
        except Exception:
            return None, None


