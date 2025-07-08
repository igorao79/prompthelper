# -*- coding: utf-8 -*-

"""
Продвинутый процессор фавиконок
Качественное удаление фона и преобразование в PNG
"""

import os
from PIL import Image, ImageFilter, ImageEnhance
from pathlib import Path

# Опциональные зависимости для продвинутых функций
try:
    import numpy as np
    import cv2
    ADVANCED_FEATURES = True
except ImportError:
    ADVANCED_FEATURES = False
    np = None
    cv2 = None

class AdvancedFaviconProcessor:
    """Продвинутый процессор фавиконок с качественным удалением фона"""
    
    def __init__(self, silent_mode=False):
        """
        Инициализация процессора
        
        Args:
            silent_mode (bool): Режим без вывода сообщений
        """
        self.silent_mode = silent_mode
        
        if not self.silent_mode:
            print("🎨 Продвинутый процессор фавиконок")
            print("=" * 50)
    
    def process_favicon(self, input_path, output_path=None, size=512):
        """
        Обрабатывает фавиконку: удаляет фон, преобразует в PNG
        
        Args:
            input_path (str): Путь к исходному изображению
            output_path (str): Путь для сохранения (опционально)
            size (int): Размер фавиконки
            
        Returns:
            PIL.Image: Обработанное изображение или None
        """
        try:
            if not self.silent_mode:
                print(f"🔧 Обработка фавиконки: {input_path}")
            
            # Загружаем изображение
            image = Image.open(input_path)
            
            # Преобразуем в RGBA
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            # Изменяем размер
            if image.size != (size, size):
                image = image.resize((size, size), Image.Resampling.LANCZOS)
            
            # Применяем улучшенное удаление фона
            processed_image = self._advanced_background_removal(image)
            
            # Дополнительная обработка для улучшения качества
            processed_image = self._enhance_favicon(processed_image)
            
            # Сохраняем если указан путь
            if output_path:
                processed_image.save(output_path, format='PNG')
                if not self.silent_mode:
                    print(f"✅ Фавиконка обработана: {output_path}")
                    file_size = os.path.getsize(output_path)
                    print(f"📁 Размер файла: {file_size} байт")
            
            return processed_image
            
        except Exception as e:
            if not self.silent_mode:
                print(f"❌ Ошибка обработки фавиконки: {e}")
            return None
    
    def _advanced_background_removal(self, image):
        """Продвинутое удаление фона с использованием нескольких методов"""
        try:
            # Метод 1: Анализ краев (улучшенный)
            edge_result = self._edge_based_removal(image)
            
            # Метод 2: Цветовой анализ
            color_result = self._color_based_removal(image)
            
            # Метод 3: Контрастное выделение
            contrast_result = self._contrast_based_removal(image)
            
            # Комбинируем результаты
            final_result = self._combine_removal_methods(edge_result, color_result, contrast_result)
            
            return final_result
            
        except Exception as e:
            if not self.silent_mode:
                print(f"⚠️ Ошибка удаления фона: {e}")
            return image
    
    def _edge_based_removal(self, image):
        """Удаление фона на основе анализа краев"""
        try:
            # Получаем данные пикселей
            data = image.getdata()
            width, height = image.size
            
            # Анализируем границы изображения (больше точек)
            border_pixels = []
            
            # Верхняя и нижняя границы
            for x in range(width):
                border_pixels.append(image.getpixel((x, 0)))
                border_pixels.append(image.getpixel((x, height-1)))
            
            # Левая и правая границы
            for y in range(height):
                border_pixels.append(image.getpixel((0, y)))
                border_pixels.append(image.getpixel((width-1, y)))
            
            # Определяем цвет фона
            bg_color = self._find_dominant_background_color(border_pixels)
            
            if not bg_color:
                return image
            
            # Создаем новое изображение с прозрачностью
            new_data = []
            for pixel in data:
                if self._is_background_pixel(pixel, bg_color, tolerance=25):
                    new_data.append((255, 255, 255, 0))  # Прозрачный
                else:
                    new_data.append(pixel)
            
            result = Image.new('RGBA', image.size)
            result.putdata(new_data)
            return result
            
        except Exception as e:
            return image
    
    def _color_based_removal(self, image):
        """Удаление фона на основе цветового анализа"""
        try:
            # Конвертируем в HSV для лучшего анализа цветов
            hsv_image = image.convert('HSV')
            
            # Анализируем цвета в углах
            corners = [
                image.getpixel((0, 0)),
                image.getpixel((image.width-1, 0)),
                image.getpixel((0, image.height-1)),
                image.getpixel((image.width-1, image.height-1))
            ]
            
            # Ищем наиболее вероятный цвет фона
            bg_color = self._find_dominant_background_color(corners)
            
            if not bg_color:
                return image
            
            # Создаем маску для удаления фона
            mask = self._create_color_mask(image, bg_color)
            
            # Применяем маску
            result = image.copy()
            result.putalpha(mask)
            
            return result
            
        except Exception as e:
            return image
    
    def _contrast_based_removal(self, image):
        """Удаление фона на основе контрастного анализа"""
        try:
            if not ADVANCED_FEATURES:
                # Fallback без numpy/cv2
                return self._simple_contrast_removal(image)
            
            # Конвертируем в numpy array для анализа
            img_array = np.array(image)
            
            # Анализируем контраст
            gray = np.dot(img_array[...,:3], [0.2989, 0.5870, 0.1140])
            
            # Находим области с низким контрастом (вероятно фон)
            edges = cv2.Canny(gray.astype(np.uint8), 50, 150)
            
            # Создаем маску на основе краев
            mask = np.where(edges > 0, 255, 0).astype(np.uint8)
            
            # Расширяем маску для лучшего выделения объектов
            kernel = np.ones((3,3), np.uint8)
            mask = cv2.dilate(mask, kernel, iterations=2)
            
            # Инвертируем маску для фона
            bg_mask = 255 - mask
            
            # Применяем к изображению
            result = image.copy()
            alpha = Image.fromarray(bg_mask, mode='L')
            result.putalpha(alpha)
            
            return result
            
        except Exception as e:
            return image
    
    def _simple_contrast_removal(self, image):
        """Простое удаление фона без numpy/cv2"""
        try:
            # Простой алгоритм без внешних зависимостей
            result = image.copy()
            
            # Применяем фильтр для выделения краев
            edges = result.filter(ImageFilter.FIND_EDGES)
            
            # Конвертируем в маску
            mask = edges.convert('L')
            
            # Инвертируем маску
            mask = mask.point(lambda x: 255 if x > 30 else 0)
            
            result.putalpha(mask)
            return result
            
        except Exception as e:
            return image
    
    def _find_dominant_background_color(self, pixels):
        """Находит доминирующий цвет фона"""
        try:
            # Фильтруем только светлые пиксели (возможные фоновые)
            light_pixels = []
            for pixel in pixels:
                if len(pixel) >= 3:
                    r, g, b = pixel[0], pixel[1], pixel[2]
                    # Только очень светлые пиксели
                    if r > 230 and g > 230 and b > 230:
                        light_pixels.append((r, g, b))
            
            if not light_pixels:
                return None
            
            # Находим самый частый цвет
            color_counts = {}
            for color in light_pixels:
                # Округляем цвета для группировки
                rounded_color = (
                    round(color[0] / 10) * 10,
                    round(color[1] / 10) * 10,
                    round(color[2] / 10) * 10
                )
                color_counts[rounded_color] = color_counts.get(rounded_color, 0) + 1
            
            if not color_counts:
                return None
            
            # Возвращаем самый частый цвет
            dominant_color = max(color_counts.keys(), key=lambda k: color_counts[k])
            return dominant_color
            
        except Exception as e:
            return None
    
    def _is_background_pixel(self, pixel, bg_color, tolerance=25):
        """Проверяет, является ли пиксель фоновым"""
        try:
            if len(pixel) < 3 or not bg_color:
                return False
            
            r, g, b = pixel[0], pixel[1], pixel[2]
            bg_r, bg_g, bg_b = bg_color[0], bg_color[1], bg_color[2]
            
            # Проверяем расстояние между цветами
            distance = ((r - bg_r) ** 2 + (g - bg_g) ** 2 + (b - bg_b) ** 2) ** 0.5
            
            return distance <= tolerance
            
        except Exception as e:
            return False
    
    def _create_color_mask(self, image, bg_color):
        """Создает маску для удаления цвета"""
        try:
            mask = Image.new('L', image.size, 255)
            
            for y in range(image.height):
                for x in range(image.width):
                    pixel = image.getpixel((x, y))
                    if self._is_background_pixel(pixel, bg_color, tolerance=30):
                        mask.putpixel((x, y), 0)
            
            return mask
            
        except Exception as e:
            return Image.new('L', image.size, 255)
    
    def _combine_removal_methods(self, edge_result, color_result, contrast_result):
        """Комбинирует результаты разных методов удаления фона"""
        try:
            # Создаем итоговую маску на основе всех методов
            width, height = edge_result.size
            final_mask = Image.new('L', (width, height), 255)
            
            for y in range(height):
                for x in range(width):
                    # Получаем альфа-канал от каждого метода
                    edge_alpha = edge_result.getpixel((x, y))[3] if len(edge_result.getpixel((x, y))) > 3 else 255
                    color_alpha = color_result.getpixel((x, y))[3] if len(color_result.getpixel((x, y))) > 3 else 255
                    contrast_alpha = contrast_result.getpixel((x, y))[3] if len(contrast_result.getpixel((x, y))) > 3 else 255
                    
                    # Берем минимальное значение (самое прозрачное)
                    final_alpha = min(edge_alpha, color_alpha, contrast_alpha)
                    
                    # Если большинство методов считают пиксель фоновым, делаем его прозрачным
                    transparent_votes = sum([
                        edge_alpha < 128,
                        color_alpha < 128,
                        contrast_alpha < 128
                    ])
                    
                    if transparent_votes >= 2:
                        final_alpha = 0
                    
                    final_mask.putpixel((x, y), final_alpha)
            
            # Применяем итоговую маску к лучшему результату
            result = edge_result.copy()
            result.putalpha(final_mask)
            
            return result
            
        except Exception as e:
            return edge_result
    
    def _enhance_favicon(self, image):
        """Улучшает качество фавиконки"""
        try:
            # Повышаем резкость
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.2)
            
            # Слегка повышаем контрастность
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.1)
            
            # Применяем легкую фильтрацию для сглаживания
            image = image.filter(ImageFilter.SMOOTH_MORE)
            
            return image
            
        except Exception as e:
            return image
    
    def batch_process_favicons(self, input_dir, output_dir=None, size=512):
        """
        Обрабатывает несколько фавиконок в папке
        
        Args:
            input_dir (str): Папка с исходными изображениями
            output_dir (str): Папка для сохранения (опционально)
            size (int): Размер фавиконок
            
        Returns:
            list: Список обработанных файлов
        """
        try:
            input_path = Path(input_dir)
            output_path = Path(output_dir) if output_dir else input_path
            
            if not input_path.exists():
                if not self.silent_mode:
                    print(f"❌ Папка не найдена: {input_path}")
                return []
            
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Поддерживаемые форматы
            supported_formats = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
            
            processed_files = []
            
            for file_path in input_path.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in supported_formats:
                    output_file = output_path / f"{file_path.stem}_processed.png"
                    
                    result = self.process_favicon(str(file_path), str(output_file), size)
                    if result:
                        processed_files.append(str(output_file))
            
            if not self.silent_mode:
                print(f"✅ Обработано {len(processed_files)} файлов")
            
            return processed_files
            
        except Exception as e:
            if not self.silent_mode:
                print(f"❌ Ошибка пакетной обработки: {e}")
            return []

def main():
    """Тестирование процессора фавиконок"""
    print("🧪 Тест продвинутого процессора фавиконок")
    print("=" * 60)
    
    processor = AdvancedFaviconProcessor()
    
    # Тестируем на тестовом изображении
    test_image_path = "test_favicon.png"
    
    # Создаем тестовое изображение если его нет
    if not os.path.exists(test_image_path):
        # Создаем простое тестовое изображение
        test_image = Image.new('RGB', (512, 512), color='white')
        from PIL import ImageDraw
        draw = ImageDraw.Draw(test_image)
        draw.ellipse([100, 100, 412, 412], fill='blue', outline='navy', width=5)
        draw.text((200, 220), "TEST", fill='white')
        test_image.save(test_image_path)
        print(f"📝 Создано тестовое изображение: {test_image_path}")
    
    # Обрабатываем тестовое изображение
    processed_path = "test_favicon_processed.png"
    result = processor.process_favicon(test_image_path, processed_path)
    
    if result:
        print(f"✅ Тестовое изображение обработано: {processed_path}")
    else:
        print("❌ Не удалось обработать тестовое изображение")

if __name__ == "__main__":
    main() 