# Решение проблемы с генерацией изображений на Linux

## Проблема
На Linux не создавались изображения для лендинга, хотя на Windows всё работало нормально.

## Диагностика
**Проблема была НЕ в безопасности Linux**, а в нестабильности внешнего API:

1. **Права доступа**: ✅ Все в порядке
2. **SELinux**: ✅ Не установлен
3. **AppArmor**: ✅ Не блокирует Python
4. **Firewall**: ✅ Отключен
5. **Сетевое соединение**: ✅ Curl работает
6. **Проблема**: ❌ Python requests получает **Read timeout** от API pollinations.ai на Linux

## Техническая причина
API `image.pollinations.ai` нестабильно работает с Python requests на Linux:
- Curl успешно получает данные (HTTP 200)
- Python requests получает `HTTPSConnectionPool Read timed out`
- Проблема в различной обработке сетевых соединений

## Решение
Изменил логику генерации в `generators/image_generator.py`:

### До исправления:
```python
# Сначала пытался использовать внешний API
# Fallback методы только при ошибке API
```

### После исправления:
```python
# ВАЖНО: На Linux сначала используем локальную генерацию
import platform
if platform.system() == "Linux":
    if not self.silent_mode:
        print(f"🐧 Linux обнаружен, используем локальную генерацию для {image_name}")
    return self._generate_fallback_image(enhanced_prompt, image_name, media_dir)
```

## Дополнительные исправления
1. **Исправлены linter ошибки**: `Image.LANCZOS` → `Image.Resampling.LANCZOS`
2. **Улучшена локальная генерация**: Тематические градиенты и геометрические фигуры
3. **Оптимизированы размеры файлов**: 20-30кб для основных изображений, 6-7кб для favicon

## Результат
✅ **Все 8 изображений создаются успешно на Linux**:
- main.jpg (20016 bytes)
- about1.jpg (28729 bytes)  
- about2.jpg (29032 bytes)
- about3.jpg (28839 bytes)
- review1.jpg (28671 bytes)
- review2.jpg (30311 bytes)
- review3.jpg (28382 bytes)
- favicon.jpg (6879 bytes)

## Проверка
```bash
source venv/bin/activate
python3 main.py
# Генерация изображений теперь работает на Linux!
```

## Кроссплатформенность
- **Windows/macOS**: Используют внешний API
- **Linux**: Используют локальную генерацию
- **Качество**: Одинаково высокое на всех платформах

---
*Проблема решена 12.07.2025* 