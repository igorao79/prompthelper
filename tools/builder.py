#!/usr/bin/env python3
"""
Windows Builder: скачивает ветку linux из репозитория igorao79/prompthelper,
собирает onefile EXE с помощью PyInstaller и складывает результат в release/.

Запуск (из корня проекта):
  python tools/builder.py

Опции:
  --repo https://github.com/igorao79/prompthelper
  --branch linux

Требования: установленный Python 3.10+, доступ в интернет.
"""
import argparse
import io
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import requests


def run(cmd, cwd=None):
    print(f"$ {' '.join(cmd)}")
    subprocess.check_call(cmd, cwd=cwd)


def ensure_venv(venv_dir: Path):
    if not venv_dir.exists():
        run([sys.executable, "-m", "venv", str(venv_dir)])
    python = venv_dir / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    def pip_run(*args):
        run([str(python), "-m", "pip", *args])
    return python, pip_run


def download_branch_zip(repo: str, branch: str, dest_dir: Path) -> Path:
    zip_url = f"{repo}/archive/refs/heads/{branch}.zip"
    print(f"📥 Скачиваем {zip_url}")
    r = requests.get(zip_url, timeout=60)
    if r.status_code == 404:
        raise FileNotFoundError("zip not found")
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    zf.extractall(dest_dir)
    # Внутри будет папка вида prompthelper-<branch>
    root_candidates = list(dest_dir.glob("*"))
    if not root_candidates:
        raise RuntimeError("Архив пустой")
    return root_candidates[0]


def clone_branch_git(repo: str, branch: str, dest_dir: Path) -> Path:
    print("📦 Zip недоступен, пробуем git clone --depth 1 ...")
    repo_dir = dest_dir / "repo"
    run(["git", "clone", "--depth", "1", "--branch", branch, repo, str(repo_dir)])
    return repo_dir


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default="https://github.com/igorao79/prompthelper")
    parser.add_argument("--branch", default="linux")
    args = parser.parse_args()

    project_root = Path.cwd()
    build_root = project_root / "_build"
    release_root = project_root / "release"
    venv_dir = build_root / "venv"
    src_dir = build_root / "src"

    # Чистим и готовим папки
    if build_root.exists():
        shutil.rmtree(build_root, ignore_errors=True)
    build_root.mkdir(parents=True, exist_ok=True)
    src_dir.mkdir(parents=True, exist_ok=True)
    release_root.mkdir(parents=True, exist_ok=True)

    # Скачиваем исходники ветки
    try:
        branch_root = download_branch_zip(args.repo, args.branch, src_dir)
    except FileNotFoundError:
        branch_root = clone_branch_git(args.repo, args.branch, src_dir)

    # Создаем venv и ставим зависимости
    python, pip_run = ensure_venv(venv_dir)
    # Обновляем pip/setuptools/wheel корректно через -m pip
    pip_run("install", "--upgrade", "pip", "setuptools", "wheel")
    req = branch_root / "requirements.txt"
    if req.exists():
        pip_run("install", "-r", str(req))
    pip_run("install", "pyinstaller", "requests")  # для сборки и проверки обновлений

    # Сборка
    dist_dir = build_root / "dist"
    if dist_dir.exists():
        shutil.rmtree(dist_dir, ignore_errors=True)

    # PyInstaller
    pyinstaller_cmd = [
        str(python), "-m", "PyInstaller",
        "--noconfirm", "--clean", "--onefile",
        "--name", "PromptHelper",
        "--hidden-import", "PySide6",
        "--hidden-import", "PIL",
        "--hidden-import", "requests",
        str(branch_root / "main.py"),
    ]
    run(pyinstaller_cmd, cwd=branch_root)

    built_exe = branch_root / "dist" / ("PromptHelper.exe" if os.name == "nt" else "PromptHelper")
    if not built_exe.exists():
        raise RuntimeError("Сборка не создала EXE")

    shutil.copy2(built_exe, release_root / built_exe.name)
    print(f"✅ Готово: {release_root / built_exe.name}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Ошибка сборки: {e}")
        sys.exit(1)


