"""
Валидатор качества сгенерированных изображений
Проверяет на типичные проблемы AI-генерации
"""

import os
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from pathlib import Path
import json
from datetime import datetime
import requests
from io import BytesIO
import base64

class ImageQualityValidator:
    """Класс для проверки качества и достоверности сгенерированных изображений"""
    
    def __init__(self, silent_mode=False):
        self.silent_mode = silent_mode
        self.issues_found = []
        
        # Пороговые значения для анализа
        self.blur_threshold = 100.0  # Ниже = размытость
        self.low_contrast_threshold = 30  # Ниже = низкий контраст
        self.noise_threshold = 0.15  # Выше = много шума
        
        if not self.silent_mode:
            print("🔍 ImageQualityValidator - Анализ качества изображений")
    
    def validate_media_folder(self, media_dir, theme=None):
        """
        Проверяет все изображения в папке media
        
        Args:
            media_dir (str): Путь к папке с изображениями
            theme (str): Тематика для контекстуальной проверки
            
        Returns:
            dict: Отчет о проверке
        """
        if not self.silent_mode:
            print(f"🔍 Анализ изображений в: {media_dir}")
        
        media_path = Path(media_dir)
        if not media_path.exists():
            return {"error": "Папка media не найдена"}
        
        # Список ожидаемых файлов
        expected_files = [
            'main.jpg', 'about1.jpg', 'about2.jpg', 'about3.jpg',
            'review1.jpg', 'review2.jpg', 'review3.jpg', 'favicon.png'
        ]
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "theme": theme,
            "total_files": 0,
            "analyzed_files": 0,
            "quality_scores": {},
            "issues": [],
            "recommendations": [],
            "overall_score": 0
        }
        
        total_score = 0
        analyzed_count = 0
        
        for filename in expected_files:
            file_path = media_path / filename
            
            if file_path.exists():
                report["total_files"] += 1
                
                if not self.silent_mode:
                    print(f"📊 Анализ {filename}...")
                
                # Анализируем изображение
                analysis = self.analyze_image(str(file_path), filename, theme)
                
                if analysis:
                    report["quality_scores"][filename] = analysis
                    report["analyzed_files"] += 1
                    total_score += analysis.get("overall_score", 0)
                    analyzed_count += 1
                    
                    # Собираем проблемы
                    if analysis.get("issues"):
                        report["issues"].extend([
                            f"{filename}: {issue}" for issue in analysis["issues"]
                        ])
        
        # Вычисляем общую оценку
        if analyzed_count > 0:
            report["overall_score"] = round(total_score / analyzed_count, 2)
        
        # Генерируем рекомендации
        report["recommendations"] = self._generate_recommendations(report)
        
        if not self.silent_mode:
            self._print_report(report)
        
        return report
    
    def analyze_image(self, image_path, filename, theme=None):
        """
        Анализирует одно изображение на качество и достоверность
        
        Args:
            image_path (str): Путь к изображению
            filename (str): Имя файла
            theme (str): Тематика
            
        Returns:
            dict: Результат анализа
        """
        try:
            # Загружаем изображение
            image = Image.open(image_path)
            cv_image = cv2.imread(image_path)
            
            if cv_image is None:
                return {"error": "Не удалось загрузить изображение"}
            
            analysis = {
                "filename": filename,
                "size": image.size,
                "format": image.format,
                "mode": image.mode,
                "file_size_kb": round(Path(image_path).stat().st_size / 1024, 2),
                "issues": [],
                "scores": {},
                "overall_score": 0
            }
            
            # Проверки качества
            analysis["scores"]["sharpness"] = self._check_sharpness(cv_image)
            analysis["scores"]["contrast"] = self._check_contrast(cv_image)
            analysis["scores"]["noise"] = self._check_noise(cv_image)
            analysis["scores"]["color_balance"] = self._check_color_balance(cv_image)
            
            # Специфичные проверки по типу изображения
            if "review" in filename:
                analysis["scores"]["face_detection"] = self._check_faces(cv_image)
                analysis["scores"]["human_anatomy"] = self._check_human_anatomy(cv_image, image)
            
            if theme and "авто" in theme.lower():
                analysis["scores"]["vehicle_logic"] = self._check_vehicle_logic(cv_image, image)
            
            # Проверки артефактов AI
            analysis["scores"]["ai_artifacts"] = self._check_ai_artifacts(cv_image, image)
            analysis["scores"]["geometric_consistency"] = self._check_geometry(cv_image)
            
            # Проверка размера файла
            analysis["scores"]["file_size"] = self._check_file_size(analysis["file_size_kb"], filename)
            
            # Вычисляем общую оценку
            scores = [v for v in analysis["scores"].values() if isinstance(v, (int, float))]
            if scores:
                analysis["overall_score"] = round(sum(scores) / len(scores), 2)
            
            # Генерируем список проблем
            analysis["issues"] = self._generate_issues(analysis)
            
            return analysis
            
        except Exception as e:
            return {"error": f"Ошибка анализа: {str(e)}"}
    
    def _check_sharpness(self, cv_image):
        """Проверка четкости изображения"""
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        if laplacian_var > 500:
            return 10  # Отличная четкость
        elif laplacian_var > 200:
            return 8   # Хорошая четкость
        elif laplacian_var > self.blur_threshold:
            return 6   # Приемлемая четкость
        elif laplacian_var > 50:
            return 4   # Слабая четкость
        else:
            return 2   # Размыто
    
    def _check_contrast(self, cv_image):
        """Проверка контрастности"""
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        contrast = gray.std()
        
        if contrast > 60:
            return 10  # Отличный контраст
        elif contrast > 45:
            return 8   # Хороший контраст
        elif contrast > self.low_contrast_threshold:
            return 6   # Приемлемый контраст
        elif contrast > 20:
            return 4   # Слабый контраст
        else:
            return 2   # Очень низкий контраст
    
    def _check_noise(self, cv_image):
        """Проверка уровня шума"""
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # Применяем фильтр для подавления шума
        denoised = cv2.medianBlur(gray, 5)
        
        # Вычисляем разность
        noise = cv2.absdiff(gray, denoised)
        noise_level = np.mean(noise) / 255.0
        
        if noise_level < 0.05:
            return 10  # Минимальный шум
        elif noise_level < 0.1:
            return 8   # Небольшой шум
        elif noise_level < self.noise_threshold:
            return 6   # Умеренный шум
        elif noise_level < 0.25:
            return 4   # Заметный шум
        else:
            return 2   # Сильный шум
    
    def _check_color_balance(self, cv_image):
        """Проверка цветового баланса"""
        # Конвертируем в LAB для анализа
        lab = cv2.cvtColor(cv_image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Проверяем баланс a и b каналов
        a_mean = np.mean(a)
        b_mean = np.mean(b)
        
        # Идеальный баланс около 128
        a_deviation = abs(a_mean - 128)
        b_deviation = abs(b_mean - 128)
        
        avg_deviation = (a_deviation + b_deviation) / 2
        
        if avg_deviation < 5:
            return 10  # Отличный баланс
        elif avg_deviation < 10:
            return 8   # Хороший баланс
        elif avg_deviation < 20:
            return 6   # Приемлемый баланс
        elif avg_deviation < 30:
            return 4   # Слабый баланс
        else:
            return 2   # Плохой баланс
    
    def _check_faces(self, cv_image):
        """Проверка наличия и качества лиц для review изображений"""
        try:
            # Используем каскад Хаара для детекции лиц
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            faces = face_cascade.detectMultiScale(gray, 1.1, 4, minSize=(50, 50))
            
            if len(faces) == 0:
                return 2  # Лицо не найдено
            elif len(faces) == 1:
                # Проверяем размер лица
                (x, y, w, h) = faces[0]
                face_area = w * h
                image_area = cv_image.shape[0] * cv_image.shape[1]
                face_ratio = face_area / image_area
                
                if face_ratio > 0.1:  # Лицо занимает достаточную площадь
                    return 10
                else:
                    return 6  # Лицо слишком маленькое
            else:
                return 4  # Найдено несколько лиц (может быть проблемой)
                
        except:
            return 5  # Ошибка детекции, нейтральная оценка
    
    def _check_human_anatomy(self, cv_image, pil_image):
        """Проверка анатомической правдоподобности людей"""
        # Простые эвристики для выявления анатомических проблем
        score = 8  # Начинаем с хорошей оценки
        
        # Проверяем пропорции изображения
        height, width = cv_image.shape[:2]
        aspect_ratio = width / height
        
        # Для портретов ожидаем определенные пропорции
        if 0.6 <= aspect_ratio <= 1.5:
            score += 1
        else:
            score -= 1
        
        # Проверяем цветовую целостность кожи
        try:
            # Конвертируем в HSV для анализа цвета кожи
            hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
            
            # Диапазон цветов кожи в HSV
            lower_skin = np.array([0, 20, 70])
            upper_skin = np.array([20, 255, 255])
            
            skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
            skin_pixels = cv2.countNonZero(skin_mask)
            total_pixels = cv_image.shape[0] * cv_image.shape[1]
            
            skin_ratio = skin_pixels / total_pixels
            
            # Для портретов ожидаем разумное количество кожи
            if 0.1 <= skin_ratio <= 0.6:
                score += 1
            elif skin_ratio < 0.05:
                score -= 2  # Слишком мало кожи
                
        except:
            pass
        
        return max(2, min(10, score))
    
    def _check_vehicle_logic(self, cv_image, pil_image):
        """Проверка логичности автомобилей"""
        score = 8  # Начальная оценка
        
        # Проверяем симметрию (автомобили обычно симметричны)
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        height, width = gray.shape
        
        # Сравниваем левую и правую половины
        left_half = gray[:, :width//2]
        right_half = cv2.flip(gray[:, width//2:], 1)
        
        # Подгоняем размеры
        min_width = min(left_half.shape[1], right_half.shape[1])
        left_half = left_half[:, :min_width]
        right_half = right_half[:, :min_width]
        
        # Вычисляем разность
        if left_half.shape == right_half.shape:
            diff = cv2.absdiff(left_half, right_half)
            symmetry_score = 1.0 - (np.mean(diff) / 255.0)
            
            if symmetry_score > 0.7:
                score += 1
            elif symmetry_score < 0.4:
                score -= 2  # Очень несимметрично
        
        # Проверяем наличие колес (круглых объектов в нижней части)
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 50, 
                                 param1=50, param2=30, minRadius=10, maxRadius=100)
        
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            wheel_count = 0
            
            # Считаем круги в нижней половине (где должны быть колеса)
            for (x, y, r) in circles:
                if y > height * 0.6:  # Нижняя половина
                    wheel_count += 1
            
            if wheel_count >= 2:
                score += 1
            elif wheel_count == 0:
                score -= 1
        
        return max(2, min(10, score))
    
    def _check_ai_artifacts(self, cv_image, pil_image):
        """Проверка на типичные артефакты AI-генерации"""
        score = 8
        
        # Проверка на дублирующиеся паттерны
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # Ищем повторяющиеся элементы
        template_size = 32
        height, width = gray.shape
        
        if height > template_size * 2 and width > template_size * 2:
            # Берем небольшой участок и ищем его копии
            template = gray[height//4:height//4+template_size, 
                          width//4:width//4+template_size]
            
            result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= 0.8)  # Высокое совпадение
            
            if len(locations[0]) > 3:  # Найдено много копий
                score -= 2
        
        # Проверка на неестественную гладкость (признак AI)
        blur_kernel = 5
        blurred = cv2.GaussianBlur(gray, (blur_kernel, blur_kernel), 0)
        diff = cv2.absdiff(gray, blurred)
        texture_variance = np.var(diff)
        
        if texture_variance < 10:  # Слишком гладко
            score -= 1
        
        # Проверка на неестественные градиенты
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        
        # Ищем области с очень резкими переходами
        extreme_gradients = np.sum(gradient_magnitude > 200)
        total_pixels = gradient_magnitude.size
        
        if extreme_gradients / total_pixels > 0.05:  # Много резких переходов
            score -= 1
        
        return max(2, min(10, score))
    
    def _check_geometry(self, cv_image):
        """Проверка геометрической согласованности"""
        score = 8
        
        # Детекция линий
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
        
        if lines is not None:
            # Анализируем углы между линиями
            angles = []
            for line in lines[:20]:  # Берем первые 20 линий
                rho, theta = line[0]
                angles.append(theta)
            
            # Проверяем на естественность углов
            angles = np.array(angles)
            angle_variance = np.var(angles)
            
            if angle_variance > 0.5:  # Хорошее разнообразие углов
                score += 1
            elif angle_variance < 0.1:  # Слишком однообразные углы
                score -= 1
        
        return max(2, min(10, score))
    
    def _check_file_size(self, size_kb, filename):
        """Проверка размера файла"""
        if filename.endswith('.png'):
            # Для PNG (фавиконки)
            if size_kb < 100:
                return 10
            elif size_kb < 200:
                return 8
            else:
                return 6
        else:
            # Для JPG
            if 50 <= size_kb <= 200:
                return 10
            elif 30 <= size_kb <= 300:
                return 8
            elif size_kb < 30:
                return 4  # Слишком сжато
            else:
                return 6  # Слишком большой
    
    def _generate_issues(self, analysis):
        """Генерирует список проблем на основе анализа"""
        issues = []
        scores = analysis["scores"]
        
        if scores.get("sharpness", 10) < 5:
            issues.append("Изображение размыто или нечетко")
        
        if scores.get("contrast", 10) < 5:
            issues.append("Низкий контраст, изображение блеклое")
        
        if scores.get("noise", 10) < 5:
            issues.append("Высокий уровень шума/зернистости")
        
        if scores.get("color_balance", 10) < 5:
            issues.append("Плохой цветовой баланс")
        
        if scores.get("face_detection", 10) < 5:
            issues.append("Проблемы с лицами (не найдены или множественные)")
        
        if scores.get("human_anatomy", 10) < 5:
            issues.append("Анатомические нарушения или неестественные пропорции")
        
        if scores.get("vehicle_logic", 10) < 5:
            issues.append("Нелогичная структура автомобиля")
        
        if scores.get("ai_artifacts", 10) < 5:
            issues.append("Обнаружены артефакты AI-генерации")
        
        if scores.get("geometric_consistency", 10) < 5:
            issues.append("Геометрические несоответствия")
        
        if scores.get("file_size", 10) < 5:
            issues.append("Неоптимальный размер файла")
        
        return issues
    
    def _generate_recommendations(self, report):
        """Генерирует рекомендации на основе отчета"""
        recommendations = []
        
        # Анализируем общие проблемы
        low_quality_files = []
        for filename, analysis in report["quality_scores"].items():
            if analysis.get("overall_score", 0) < 6:
                low_quality_files.append(filename)
        
        if low_quality_files:
            recommendations.append(f"Рекомендуется перегенерировать: {', '.join(low_quality_files)}")
        
        # Специфичные рекомендации
        if "размыто" in str(report["issues"]):
            recommendations.append("Добавьте в промпты: 'sharp, high quality, detailed'")
        
        if "контраст" in str(report["issues"]):
            recommendations.append("Добавьте в промпты: 'high contrast, vibrant colors'")
        
        if "лиц" in str(report["issues"]):
            recommendations.append("Для review изображений используйте промпты: 'close-up portrait, human face clearly visible'")
        
        if "автомобиль" in str(report["issues"]):
            recommendations.append("Для авто добавьте: 'realistic car, proper vehicle proportions, logical car design'")
        
        if report["overall_score"] < 6:
            recommendations.append("Общее качество низкое. Попробуйте другую модель AI или улучшите промпты")
        
        return recommendations
    
    def _print_report(self, report):
        """Выводит отчет в консоль"""
        print("\n" + "="*60)
        print("📊 ОТЧЕТ О КАЧЕСТВЕ ИЗОБРАЖЕНИЙ")
        print("="*60)
        
        print(f"🎯 Тематика: {report.get('theme', 'Не указана')}")
        print(f"📁 Проанализировано: {report['analyzed_files']}/{report['total_files']} файлов")
        print(f"⭐ Общая оценка: {report['overall_score']}/10")
        
        if report['overall_score'] >= 8:
            print("✅ Отличное качество!")
        elif report['overall_score'] >= 6:
            print("✅ Хорошее качество")
        elif report['overall_score'] >= 4:
            print("⚠️ Среднее качество, есть проблемы")
        else:
            print("❌ Низкое качество, требует переделки")
        
        print("\n📋 ДЕТАЛЬНЫЕ ОЦЕНКИ:")
        for filename, analysis in report["quality_scores"].items():
            score = analysis.get("overall_score", 0)
            icon = "✅" if score >= 7 else "⚠️" if score >= 5 else "❌"
            print(f"  {icon} {filename}: {score}/10")
            
            if analysis.get("issues"):
                for issue in analysis["issues"]:
                    print(f"     🔸 {issue}")
        
        if report["issues"]:
            print(f"\n⚠️ НАЙДЕННЫЕ ПРОБЛЕМЫ ({len(report['issues'])}):")
            for issue in report["issues"][:10]:  # Показываем первые 10
                print(f"  • {issue}")
        
        if report["recommendations"]:
            print(f"\n💡 РЕКОМЕНДАЦИИ:")
            for rec in report["recommendations"]:
                print(f"  ➤ {rec}")
        
        print("="*60)
    
    def save_report(self, report, output_path="validation_report.json"):
        """Сохраняет отчет в JSON файл"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            if not self.silent_mode:
                print(f"💾 Отчет сохранен: {output_path}")
            
            return True
        except Exception as e:
            if not self.silent_mode:
                print(f"❌ Ошибка сохранения отчета: {e}")
            return False


def validate_images(media_dir, theme=None, save_report=True, silent_mode=False):
    """
    Удобная функция для быстрой проверки изображений
    
    Args:
        media_dir (str): Путь к папке с изображениями
        theme (str): Тематика
        save_report (bool): Сохранять ли отчет в файл
        silent_mode (bool): Тихий режим
        
    Returns:
        dict: Отчет о проверке
    """
    validator = ImageQualityValidator(silent_mode=silent_mode)
    report = validator.validate_media_folder(media_dir, theme)
    
    if save_report and not report.get("error"):
        validator.save_report(report)
    
    return report


if __name__ == "__main__":
    # Пример использования
    media_directory = "media"
    theme = "выездной автосервис"
    
    print("🔍 Запуск валидации изображений...")
    report = validate_images(media_directory, theme, save_report=True)
    
    if report.get("error"):
        print(f"❌ Ошибка: {report['error']}")
    else:
        print(f"\n✅ Анализ завершен. Общая оценка: {report['overall_score']}/10") 