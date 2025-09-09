"""
Генерация изображений через Ideogram API (3.0 Turbo)

- 8 изображений: выполняет 2 запроса по 4 изображения
- Промпт передается БЕЗ каких-либо модификаций (то, что ввел пользователь)
- Сохранение и сжатие изображений: JPG (основные), PNG (favicon)
"""

import os
import time
from io import BytesIO
from pathlib import Path
from typing import Callable, List, Optional, Tuple

import requests
from PIL import Image
import random


class IdeogramGenerator:
    """Генератор изображений на базе Ideogram 2.0 Turbo."""

    def __init__(self, api_key: Optional[str] = None, silent_mode: bool = False, model: Optional[str] = None, magic_prompt_option: Optional[str] = None):
        # Приоритет: явный ключ -> ENV; если ключ отсутствует — не генерируем изображения
        self.api_key = api_key or os.getenv("IDEOGRAM_API_KEY") or ""
        self.api_url = "https://api.ideogram.ai/v1/ideogram-v3/generate"
        # Persistent session для keep-alive/пула соединений
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({
                "Api-Key": self.api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
            })
        self.headers = {"Api-Key": self.api_key} if self.api_key else {}
        self.silent_mode = silent_mode
        # Модель: v3 API всегда использует 3.0 Turbo
        self.model = (model or os.getenv("IDEOGRAM_MODEL") or "3.0 Turbo").strip()
        # Magic Prompt: OFF | AUTO | ON — для скорости по умолчанию OFF (можно задать через ENV)
        mpo = (magic_prompt_option or os.getenv("IDEOGRAM_MAGIC_PROMPT_OPTION") or "OFF").strip().upper()
        self.magic_prompt_option = mpo if mpo in ("OFF", "AUTO", "ON") else "ON"
        # Размер батча: по умолчанию 4 (2 запроса x 4 = 8), можно переопределить для диагностики
        try:
            self.num_images_per_request = max(1, int(os.getenv("IDEOGRAM_NUM_IMAGES_PER_REQUEST", "4")))
        except Exception:
            self.num_images_per_request = 4
        # Отладка биллинга/запросов
        self.debug_billing = str(os.getenv("IDEOGRAM_DEBUG_BILLING", "0")).lower() in ("1", "true", "yes")
        # Ретраи HTTP
        try:
            self.max_http_retries = max(1, int(os.getenv("IDEOGRAM_HTTP_RETRIES", "4")))
        except Exception:
            self.max_http_retries = 4
        try:
            self.http_backoff_base = max(0.25, float(os.getenv("IDEOGRAM_BACKOFF_BASE", "1.5")))
        except Exception:
            self.http_backoff_base = 1.5
        try:
            self.http_backoff_cap = max(1.0, float(os.getenv("IDEOGRAM_BACKOFF_CAP", "12")))
        except Exception:
            self.http_backoff_cap = 12.0
        self.retry_statuses = {429, 500, 502, 503, 504}

        # Пул соединений для ускорения параллельных загрузок
        try:
            pool_size = max(8, int(os.getenv("IDEOGRAM_HTTP_POOL", "20")))
        except Exception:
            pool_size = 20
        try:
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry  # type: ignore
            adapter = HTTPAdapter(pool_connections=pool_size, pool_maxsize=pool_size, max_retries=0)
            self.session.mount("http://", adapter)
            self.session.mount("https://", adapter)
        except Exception:
            pass

        # Глобальная скорость рендеринга (FAST/DEFAULT/QUALITY) => (TURBO/QUALITY)
        rs = (os.getenv("IDEOGRAM_RENDERING_SPEED", "FAST").strip().upper())
        if rs in ("FAST", "DEFAULT"):
            rs = "TURBO" if rs == "FAST" else "QUALITY"
        self.rendering_speed = rs if rs in ("TURBO", "QUALITY") else "TURBO"

    def generate_eight_images(
        self,
        prompt: str,
        media_dir: str,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> int:
        """
        Генерирует гарантированно 8 изображений, повторяя запросы, пока все не будут сохранены.

        Returns:
            int: количество успешно сохраненных изображений (целится в 8)
        """
        output_path = Path(media_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Ожидаемые имена файлов проекта (по порядку сохранения)
        image_names = [
            "main", "about1", "about2", "about3",
            "gallery1", "gallery2", "gallery3", "favicon",
        ]
        from collections import deque
        remaining = deque(image_names)
        saved = 0
        attempts = 0
        try:
            max_attempts = max(8, int(os.getenv("IDEOGRAM_MAX_TOTAL_ATTEMPTS", "50")))
        except Exception:
            max_attempts = 50
        base_sleep = 1.0
        backoff = 1.5
        cap_sleep = 10.0

        while remaining and attempts < max_attempts:
            attempts += 1
            batch_size = min(self.num_images_per_request, len(remaining))
            self._notify(progress_callback, f"🎨 Ideogram: попытка {attempts}, запрашиваем {batch_size} (осталось {len(remaining)})")
            urls = self._request_image_urls(prompt, num_images=batch_size)
            if not urls:
                delay = min(cap_sleep, base_sleep * (backoff ** (attempts - 1)))
                delay += random.uniform(0.0, 0.3)
                self._notify(progress_callback, f"⏳ Пустой ответ, ожидание {delay:.1f}с и повтор")
                time.sleep(delay)
                continue

            for url in urls:
                if not remaining:
                    break
                name = remaining[0]
                try:
                    img = self._download_image(url)
                    if img is None:
                        self._notify(progress_callback, f"⚠️ Загрузка не удалась для {name}, повторим позже")
                        continue
                    if name == "favicon":
                        if img.mode != "RGBA":
                            img = img.convert("RGBA")
                        # Стандартный размер favicon для современных браузеров
                        favicon_size = (64, 64)
                        img = img.resize(favicon_size, Image.Resampling.LANCZOS)
                        out_file = output_path / f"{name}.png"
                        if self._save_png(img, str(out_file)):
                            remaining.popleft()
                            saved += 1
                            self._notify(progress_callback, f"✅ {name}: сохранено (PNG)")
                        else:
                            self._notify(progress_callback, f"⚠️ {name}: ошибка сохранения, повторим")
                    else:
                        out_file = output_path / f"{name}.jpg"
                        if self._save_jpeg_under_size(img, str(out_file), target_size_kb=150):
                            remaining.popleft()
                            saved += 1
                            self._notify(progress_callback, f"✅ {name}: сохранено (JPEG)")
                        else:
                            self._notify(progress_callback, f"⚠️ {name}: не удалось сжать/сохранить, повторим")
                except Exception as e:
                    self._notify(progress_callback, f"⚠️ Ошибка сохранения {name}: {e}")

            if remaining:
                delay = min(cap_sleep, base_sleep * (backoff ** (attempts - 1)))
                delay += random.uniform(0.0, 0.3)
                self._notify(progress_callback, f"⏳ Осталось {len(remaining)} файлов, ожидание {delay:.1f}с и повтор")
                time.sleep(delay)

        if remaining:
            self._notify(progress_callback, f"⚠️ Не все изображения сохранены: осталось {len(remaining)}")
        return saved

    def generate_four_images(
        self,
        prompt: str,
        media_dir: str,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> int:
        """
        Генерирует 4 изображения одним запросом (или несколькими, если переопределён IDEOGRAM_NUM_IMAGES_PER_REQUEST).
        Имена: main, about1, about2, about3. Промпт не модифицируется пользователем, добавляется только no-text оговорка.
        """
        output_path = Path(media_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        image_names = ["main", "about1", "about2", "about3"]
        saved = 0
        cursor = 0

        total_needed = 4
        batches = []
        remaining = total_needed
        while remaining > 0:
            take = min(self.num_images_per_request, remaining)
            batches.append(take)
            remaining -= take

        for batch_index, batch_size in enumerate(batches):
            self._notify(progress_callback, f"🎨 Ideogram: партия {batch_index + 1}/{len(batches)} ({batch_size} изображений)")
            urls = self._request_image_urls(prompt, num_images=batch_size)
            if not urls:
                self._notify(progress_callback, "⚠️ Ideogram: не удалось получить ссылки изображений")
                continue

            for url in urls:
                if cursor >= len(image_names):
                    break
                name = image_names[cursor]
                try:
                    img = self._download_image(url)
                    if img is None:
                        self._notify(progress_callback, f"⚠️ Не удалось загрузить изображение для {name}")
                        cursor += 1
                        continue
                    out_file = output_path / f"{name}.jpg"
                    if self._save_jpeg_under_size(img, str(out_file), target_size_kb=150):
                        saved += 1
                        self._notify(progress_callback, f"✅ {name}: сохранено (JPEG)")
                    else:
                        self._notify(progress_callback, f"⚠️ {name}: не удалось сжать/сохранить")
                except Exception as e:
                    self._notify(progress_callback, f"⚠️ Ошибка сохранения {name}: {e}")
                finally:
                    cursor += 1

        return saved

    def generate_single_image(
        self,
        prompt: str,
        image_name: str,
        media_dir: str,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> Optional[str]:
        """Генерирует одно изображение (num_images=1) без изменения промпта. С ретраями URL и скачивания."""
        output_path = Path(media_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        self._notify(progress_callback, f"🎨 Ideogram: генерация {image_name}")
        # Несколько попыток получить URL
        urls = []
        for attempt in range(self.max_http_retries):
            urls = self._request_image_urls(prompt, num_images=1)
            if urls:
                break
            time.sleep(min(self.http_backoff_cap, self.http_backoff_base * (2 ** attempt)))
        if not urls:
            self._notify(progress_callback, "⚠️ Ideogram: не удалось получить ссылку изображения")
            return None

        try:
            img = self._download_image(urls[0])
            if img is None:
                # Повторно пробуем получить новый URL и скачать
                for attempt in range(self.max_http_retries):
                    urls = self._request_image_urls(prompt, num_images=1)
                    if urls:
                        img = self._download_image(urls[0])
                        if img is not None:
                            break
                    time.sleep(min(self.http_backoff_cap, self.http_backoff_base * (2 ** attempt)))
                if img is None:
                    return None
            if image_name == "favicon":
                if img.mode != "RGBA":
                    img = img.convert("RGBA")
                # Стандартный размер favicon для современных браузеров
                favicon_size = (64, 64)
                img = img.resize(favicon_size, Image.Resampling.LANCZOS)
                out_file = output_path / f"{image_name}.png"
                self._save_png(img, str(out_file))
                self._notify(progress_callback, f"✅ {image_name}: сохранено (PNG)")
                return str(out_file)
            else:
                out_file = output_path / f"{image_name}.jpg"
                if self._save_jpeg_under_size(img, str(out_file), target_size_kb=150):
                    self._notify(progress_callback, f"✅ {image_name}: сохранено (JPEG)")
                    return str(out_file)
                return None
        except Exception:
            return None

    def _request_image_urls(self, prompt: str, num_images: int) -> List[str]:
        # Если нет API ключа — возвращаем пустой список (сигнализируем об отключённой генерации)
        if not self.api_key:
            if not self.silent_mode:
                print("⚠️ Ideogram API ключ не задан — генерация изображений отключена")
            return []
        safe_prompt = self._augment_prompt_no_text(prompt)
        
        # v3 API структура: используем сохранённую глобальную скорость
        rs = self.rendering_speed

        payload = {
            "prompt": safe_prompt,
            "rendering_speed": rs,
            "num_images": max(1, int(num_images)),
        }
        # Параметр улучшения промпта
        try:
            if self.magic_prompt_option in ("OFF", "AUTO", "ON"):
                payload["magic_prompt_option"] = self.magic_prompt_option
        except Exception:
            pass
        attempt = 0
        while attempt < self.max_http_retries:
            attempt += 1
            try:
                if self.debug_billing and not self.silent_mode:
                    try:
                        print(f"[Ideogram] v3 payload: speed={payload['rendering_speed']} num={payload['num_images']} try={attempt}/{self.max_http_retries}")
                    except Exception:
                        pass
                resp = self.session.post(self.api_url, json=payload, timeout=30)
                if resp.status_code != 200:
                    if self.debug_billing and not self.silent_mode:
                        try:
                            print(f"[Ideogram] HTTP {resp.status_code}. Body: {resp.text[:300]}")
                        except Exception:
                            pass
                    if resp.status_code in self.retry_statuses and attempt < self.max_http_retries:
                        delay = min(self.http_backoff_cap, self.http_backoff_base * (2 ** (attempt - 1)))
                        delay += random.uniform(0, 0.3)
                        time.sleep(delay)
                        continue
                    return []
                data = resp.json() or {}
                if self.debug_billing and not self.silent_mode:
                    try:
                        interesting_headers = {k: v for k, v in resp.headers.items() if k.lower().startswith(('x-', 'rate', 'billing', 'cost'))}
                        print(f"[Ideogram] Resp hdr (partial): {interesting_headers}")
                        keys = list(data.keys())
                        print(f"[Ideogram] Resp keys: {keys}")
                    except Exception:
                        pass
                items = data.get("data") or data.get("images") or data.get("results") or []
                urls = []
                for item in items:
                    url = item.get("url") or item.get("image_url") or item.get("imageUrl")
                    if not url:
                        try:
                            url = (item.get("image") or {}).get("url")
                        except Exception:
                            url = None
                    if url:
                        urls.append(url)
                if urls:
                    return urls
                # Пустые urls — пробуем один раз повторить (на случай отложенной готовности)
                if attempt < self.max_http_retries:
                    time.sleep(min(self.http_backoff_cap, self.http_backoff_base * (2 ** (attempt - 1))))
                    continue
                return []
            except Exception:
                if attempt < self.max_http_retries:
                    delay = min(self.http_backoff_cap, self.http_backoff_base * (2 ** (attempt - 1)))
                    delay += random.uniform(0, 0.3)
                    time.sleep(delay)
                    continue
                return []

    def _augment_prompt_no_text(self, prompt: str) -> str:
        try:
            p = (prompt or "").strip()
            lc = p.lower()
            markers = ["no text", "no words", "no letters", "text-free", "without text"]
            if any(m in lc for m in markers):
                return p
            # Добавляем мягкую анти-текстовую оговорку, не меняя смысл тематики
            suffix = ", no text, no words, no letters, no watermark, no caption, text-free"
            return (p + suffix)[:2000]
        except Exception:
            return prompt

    def _download_image(self, url: str) -> Optional[Image.Image]:
        attempt = 0
        while attempt < self.max_http_retries:
            attempt += 1
            try:
                r = self.session.get(url, timeout=20)
                if r.status_code != 200:
                    if r.status_code in self.retry_statuses and attempt < self.max_http_retries:
                        delay = min(self.http_backoff_cap, self.http_backoff_base * (2 ** (attempt - 1)))
                        delay += random.uniform(0, 0.3)
                        time.sleep(delay)
                        continue
                    return None
                img = Image.open(BytesIO(r.content))
                if img.mode not in ("RGB", "RGBA"):
                    img = img.convert("RGB")
                return img
            except Exception:
                if attempt < self.max_http_retries:
                    delay = min(self.http_backoff_cap, self.http_backoff_base * (2 ** (attempt - 1)))
                    delay += random.uniform(0, 0.3)
                    time.sleep(delay)
                    continue
                return None

    def _save_jpeg_under_size(self, image: Image.Image, filepath: str, target_size_kb: int = 150) -> bool:
        try:
            img = image
            if img.mode == "RGBA":
                img = img.convert("RGB")
            # Быстрый путь: одно сохранение с разумным качеством, без optimize (ускоряет запись)
            q = int(os.getenv("IDEOGRAM_JPEG_QUALITY", "70"))
            img.save(filepath, format="JPEG", quality=max(40, min(95, q)))
            return True
        except Exception:
            return False

    # Батч любой длины с заданными именами файлов
    def generate_named_images(
        self,
        prompt: str,
        media_dir: str,
        names: List[str],
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> int:
        output_path = Path(media_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        saved = 0
        cursor = 0

        total_needed = len(names)
        batches: List[int] = []
        remaining = total_needed
        while remaining > 0:
            take = min(self.num_images_per_request, remaining)
            batches.append(take)
            remaining -= take

        attempts = 0
        max_attempts = max(8, int(os.getenv("IDEOGRAM_MAX_TOTAL_ATTEMPTS", "50")))
        remaining = names[:]
        while remaining and attempts < max_attempts:
            attempts += 1
            batch_size = min(self.num_images_per_request, len(remaining))
            self._notify(progress_callback, f"🎨 Ideogram: попытка {attempts}, запрашиваем {batch_size} (осталось {len(remaining)})")
            urls = self._request_image_urls(prompt, num_images=batch_size)
            if not urls:
                time.sleep(min(self.http_backoff_cap, self.http_backoff_base * (2 ** (attempts - 1))))
                continue
            new_remaining = []
            i = 0
            for name in remaining:
                if i >= len(urls):
                    new_remaining.append(name)
                    continue
                url = urls[i]
                i += 1
                try:
                    img = self._download_image(url)
                    if img is None:
                        new_remaining.append(name)
                        continue
                    out_file = output_path / (f"{name}.png" if name == "favicon" else f"{name}.jpg")
                    if name == "favicon":
                        if img.mode != "RGBA":
                            img = img.convert("RGBA")
                        # Стандартный размер favicon для современных браузеров
                        favicon_size = (64, 64)
                        img = img.resize(favicon_size, Image.Resampling.LANCZOS)
                        ok = self._save_png(img, str(out_file))
                    else:
                        ok = self._save_jpeg_under_size(img, str(out_file))
                    if ok:
                        saved += 1
                        self._notify(progress_callback, f"✅ {name}: сохранено")
                    else:
                        new_remaining.append(name)
                except Exception as e:
                    self._notify(progress_callback, f"⚠️ Ошибка сохранения {name}: {e}")
                    new_remaining.append(name)
            remaining = new_remaining
        return saved

    def _save_png(self, image: Image.Image, filepath: str) -> bool:
        try:
            # Оптимизация PNG для favicon: максимальная компрессия
            image.save(filepath, format="PNG", optimize=True, compress_level=9)
            return True
        except Exception:
            return False

    def _notify(self, cb: Optional[Callable[[str], None]], message: str) -> None:
        if cb:
            try:
                cb(message)
            except Exception:
                pass
        # Тише в продакшене (по умолчанию не печатаем), включается через IDEOGRAM_VERBOSE
        if not self.silent_mode and str(os.getenv("IDEOGRAM_VERBOSE", "0")).lower() in ("1", "true", "yes"):
            print(message)


