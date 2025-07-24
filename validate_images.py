#!/usr/bin/env python3
"""
Скрипт для проверки качества сгенерированных изображений
Использование: python validate_images.py [путь_к_media] [тематика]
"""

import sys
import os
from pathlib import Path

# Добавляем текущую директорию в путь для импорта
sys.path.append(str(Path(__file__).parent))

from validators.image_validator import validate_images

def main():
    """Главная функция скрипта"""
    
    # Получаем аргументы командной строки
    if len(sys.argv) > 1:
        media_dir = sys.argv[1]
    else:
        media_dir = "media"  # По умолчанию
    
    if len(sys.argv) > 2:
        theme = sys.argv[2]
    else:
        theme = None
    
    print("🔍 ВАЛИДАТОР КАЧЕСТВА ИЗОБРАЖЕНИЙ")
    print("="*50)
    print(f"📁 Папка: {media_dir}")
    print(f"🎯 Тематика: {theme or 'Не указана'}")
    print("="*50)
    
    # Проверяем существование папки
    if not os.path.exists(media_dir):
        print(f"❌ Ошибка: Папка {media_dir} не найдена!")
        print("💡 Создайте папку media с изображениями или укажите правильный путь")
        return 1
    
    # Проверяем наличие изображений
    media_path = Path(media_dir)
    image_files = list(media_path.glob("*.jpg")) + list(media_path.glob("*.png"))
    
    if not image_files:
        print(f"❌ В папке {media_dir} нет изображений (jpg/png)")
        return 1
    
    print(f"📊 Найдено изображений: {len(image_files)}")
    print()
    
    try:
        # Запускаем валидацию
        report = validate_images(media_dir, theme, save_report=True, silent_mode=False)
        
        if report.get("error"):
            print(f"❌ Ошибка валидации: {report['error']}")
            return 1
        
        # Выводим краткую статистику
        print("\n🎯 КРАТКИЕ РЕЗУЛЬТАТЫ:")
        print(f"⭐ Общая оценка: {report['overall_score']}/10")
        
        if report['overall_score'] >= 8:
            print("✅ Изображения высокого качества! Можно использовать.")
            return_code = 0
        elif report['overall_score'] >= 6:
            print("✅ Изображения приемлемого качества.")
            return_code = 0
        elif report['overall_score'] >= 4:
            print("⚠️ Есть проблемы с качеством. Рекомендуется улучшение.")
            return_code = 1
        else:
            print("❌ Низкое качество! Требуется перегенерация.")
            return_code = 2
        
        # Показываем проблемные файлы
        problem_files = []
        for filename, analysis in report["quality_scores"].items():
            if analysis.get("overall_score", 0) < 6:
                problem_files.append(filename)
        
        if problem_files:
            print(f"\n⚠️ Проблемные файлы: {', '.join(problem_files)}")
        
        # Показываем рекомендации
        if report["recommendations"]:
            print(f"\n💡 ГЛАВНЫЕ РЕКОМЕНДАЦИИ:")
            for i, rec in enumerate(report["recommendations"][:3], 1):
                print(f"  {i}. {rec}")
        
        print(f"\n💾 Подробный отчет сохранен в: validation_report.json")
        
        return return_code
        
    except KeyboardInterrupt:
        print("\n⏹️ Валидация прервана пользователем")
        return 1
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        return 1

def show_help():
    """Показывает справку по использованию"""
    print("""
🔍 ВАЛИДАТОР КАЧЕСТВА ИЗОБРАЖЕНИЙ

Проверяет сгенерированные изображения на качество и достоверность.

ИСПОЛЬЗОВАНИЕ:
    python validate_images.py                    # Проверить папку media
    python validate_images.py media_folder       # Проверить указанную папку  
    python validate_images.py media_folder тема  # Проверить с указанием темы

ПРИМЕРЫ:
    python validate_images.py
    python validate_images.py media "автосервис"
    python validate_images.py ../images "салон красоты"

ЧТО ПРОВЕРЯЕТСЯ:
    ✓ Четкость и резкость
    ✓ Контрастность
    ✓ Уровень шума
    ✓ Цветовой баланс  
    ✓ Размер файлов
    ✓ Наличие лиц (для review изображений)
    ✓ Анатомическая правдоподобность
    ✓ Логичность объектов (автомобили и т.д.)
    ✓ Артефакты AI-генерации
    ✓ Геометрическая согласованность

КОДЫ ВОЗВРАТА:
    0 - Качество хорошее или отличное
    1 - Есть проблемы, но приемлемо
    2 - Низкое качество, требует переделки

ОТЧЕТ:
    Подробный отчет сохраняется в validation_report.json
    """)

if __name__ == "__main__":
    # Проверяем аргументы
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help", "help"]:
        show_help()
        sys.exit(0)
    
    # Запускаем валидацию
    exit_code = main()
    sys.exit(exit_code) 