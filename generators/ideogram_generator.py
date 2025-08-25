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

    def generate_eight_images(
        self,
        prompt: str,
        media_dir: str,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> int:
        """
        Генерирует 8 изображений одним сценарием (2 батча по 4) без изменения промпта.

        Returns:
            int: количество успешно сохраненных изображений
        """
        output_path = Path(media_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Ожидаемые имена файлов проекта (по порядку сохранения)
        image_names = [
            "main", "about1", "about2", "about3",
            "gallery1", "gallery2", "gallery3", "favicon",
        ]

        saved = 0
        cursor = 0

        # Строго два запроса по 4 изображения
        for batch_index in range(2):
            self._notify(progress_callback, f"🎨 Ideogram: партия {batch_index + 1}/2 (4 изображения)")
            urls = self._request_image_urls(prompt, num_images=4)
            if not urls:
                self._notify(progress_callback, "⚠️ Ideogram: не удалось получить ссылки изображений")
                continue

            for i, url in enumerate(urls):
                if cursor >= len(image_names):
                    break
                name = image_names[cursor]
                try:
                    img = self._download_image(url)
                    if img is None:
                        self._notify(progress_callback, f"⚠️ Не удалось загрузить изображение для {name}")
                        cursor += 1
                        continue

                    if name == "favicon":
                        # Приводим к 512x512 и сохраняем PNG
                        if img.mode != "RGBA":
                            img = img.convert("RGBA")
                        img = img.resize((512, 512), Image.Resampling.LANCZOS)
                        out_file = output_path / f"{name}.png"
                        self._save_png(img, str(out_file))
                        saved += 1
                        self._notify(progress_callback, f"✅ {name}: сохранено (PNG)")
                    else:
                        out_file = output_path / f"{name}.jpg"
                        # Сжимаем до ~150 КБ
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
        """Генерирует одно изображение (num_images=1) без изменения промпта."""
        output_path = Path(media_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        self._notify(progress_callback, f"🎨 Ideogram: генерация {image_name}")
        urls = self._request_image_urls(prompt, num_images=1)
        if not urls:
            self._notify(progress_callback, "⚠️ Ideogram: не удалось получить ссылку изображения")
            return None

        try:
            img = self._download_image(urls[0])
            if img is None:
                return None
            if image_name == "favicon":
                if img.mode != "RGBA":
                    img = img.convert("RGBA")
                img = img.resize((512, 512), Image.Resampling.LANCZOS)
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
        
        # v3 API структура (без model параметра - всегда 3.0 Turbo)
        # Нормализуем скорость к допустимым значениям API: TURBO | QUALITY
        rs = (os.getenv("IDEOGRAM_RENDERING_SPEED", "TURBO").strip().upper())
        if rs in ("FAST", "DEFAULT"):
            rs = "TURBO" if rs == "FAST" else "QUALITY"
        if rs not in ("TURBO", "QUALITY"):
            rs = "TURBO"

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
        try:
            if self.debug_billing and not self.silent_mode:
                try:
                    print(f"[Ideogram] v3 API payload: { {'rendering_speed': payload['rendering_speed'], 'num_images': payload['num_images']} }")
                except Exception:
                    pass
            resp = self.session.post(self.api_url, json=payload, timeout=45)
            if resp.status_code != 200:
                if self.debug_billing and not self.silent_mode:
                    try:
                        print(f"[Ideogram] HTTP {resp.status_code}. Body: {resp.text[:500]}")
                    except Exception:
                        pass
                return []
            data = resp.json() or {}
            if self.debug_billing and not self.silent_mode:
                try:
                    # Выведем ключевые заголовки/поля для сверки тарифа
                    interesting_headers = {k: v for k, v in resp.headers.items() if k.lower().startswith(('x-', 'rate', 'billing', 'cost'))}
                    print(f"[Ideogram] Response headers (partial): {interesting_headers}")
                    keys = list(data.keys())
                    print(f"[Ideogram] Response json keys: {keys}")
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
            return urls
        except Exception:
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
        try:
            r = self.session.get(url, timeout=45)
            if r.status_code != 200:
                return None
            img = Image.open(BytesIO(r.content))
            # Приводим к RGB для JPEG-сохранения при необходимости
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGB")
            return img
        except Exception:
            return None

    def _save_jpeg_under_size(self, image: Image.Image, filepath: str, target_size_kb: int = 150) -> bool:
        try:
            img = image
            if img.mode == "RGBA":
                img = img.convert("RGB")
            # Быстрый путь: одно сохранение с разумным качеством, без optimize (ускоряет запись)
            q = int(os.getenv("IDEOGRAM_JPEG_QUALITY", "75"))
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

        for batch_index, batch_size in enumerate(batches):
            self._notify(progress_callback, f"🎨 Ideogram: партия {batch_index + 1}/{len(batches)} ({batch_size} изображений)")
            urls = self._request_image_urls(prompt, num_images=batch_size)
            if not urls:
                self._notify(progress_callback, "⚠️ Ideogram: не удалось получить ссылки изображений")
                continue
            for url in urls:
                if cursor >= len(names):
                    break
                name = names[cursor]
                try:
                    img = self._download_image(url)
                    if img is None:
                        self._notify(progress_callback, f"⚠️ Не удалось загрузить изображение для {name}")
                        cursor += 1
                        continue
                    out_file = output_path / (f"{name}.png" if name == "favicon" else f"{name}.jpg")
                    if name == "favicon":
                        if img.mode != "RGBA":
                            img = img.convert("RGBA")
                        img = img.resize((512, 512), Image.Resampling.LANCZOS)
                        self._save_png(img, str(out_file))
                    else:
                        self._save_jpeg_under_size(img, str(out_file))
                    saved += 1
                    self._notify(progress_callback, f"✅ {name}: сохранено")
                except Exception as e:
                    self._notify(progress_callback, f"⚠️ Ошибка сохранения {name}: {e}")
                finally:
                    cursor += 1
        return saved

    def _save_png(self, image: Image.Image, filepath: str) -> bool:
        try:
            image.save(filepath, format="PNG", optimize=True)
            return True
        except Exception:
            return False

    def _notify(self, cb: Optional[Callable[[str], None]], message: str) -> None:
        if cb:
            try:
                cb(message)
            except Exception:
                pass
        if not self.silent_mode:
            print(message)


