"""
Универсальная система оптимизации промптов для предотвращения зависаний API
"""

import re

class PromptOptimizer:
    """Оптимизирует промпты для стабильной работы с любыми API"""
    
    # Максимальные длины для разных типов промптов
    MAX_LENGTHS = {
        'main': 100,
        'about1': 90,
        'about2': 90, 
        'about3': 90,
        'review1': 110,
        'review2': 110,
        'review3': 110,
        'favicon': 70
    }
    
    # Стоп-слова, которые можно удалить для сокращения
    STOP_WORDS = [
        'with', 'and', 'for', 'the', 'of', 'in', 'to', 'a', 'an',
        'comprehensive', 'professional', 'advanced', 'modern', 'expert',
        'sophisticated', 'experienced', 'high-quality', 'state-of-the-art'
    ]
    
    @classmethod
    def optimize_prompt(cls, prompt, prompt_type='main'):
        """
        Оптимизирует промпт для предотвращения зависаний API
        
        Args:
            prompt (str): Исходный промпт
            prompt_type (str): Тип промпта (main, about1, etc.)
            
        Returns:
            str: Оптимизированный промпт
        """
        if not prompt:
            return prompt
            
        max_length = cls.MAX_LENGTHS.get(prompt_type, 90)
        
        # Если промпт уже короткий, возвращаем как есть
        if len(prompt) <= max_length:
            return prompt
        
        # Этап 1: Удаляем лишние пробелы и знаки препинания
        optimized = re.sub(r'\s+', ' ', prompt.strip())
        optimized = re.sub(r'[,;:]+', ',', optimized)
        
        if len(optimized) <= max_length:
            return optimized
        
        # Этап 2: Умное сокращение по словам
        words = optimized.split()
        
        # Сначала удаляем стоп-слова (кроме первых слов)
        if len(words) > 3:
            filtered_words = []
            for i, word in enumerate(words):
                if i < 2 or word.lower() not in cls.STOP_WORDS:
                    filtered_words.append(word)
            
            if len(filtered_words) >= 3:
                words = filtered_words
        
        # Если все еще длинно, обрезаем по словам
        if len(' '.join(words)) > max_length:
            truncated = []
            current_length = 0
            
            for word in words:
                if current_length + len(word) + 1 <= max_length:
                    truncated.append(word)
                    current_length += len(word) + 1
                else:
                    break
            
            words = truncated
        
        result = ' '.join(words)
        
        # Убираем висящие предлоги в конце
        while result.endswith((' with', ' and', ' for', ' of', ' in', ' to')):
            words = result.split()
            result = ' '.join(words[:-1])
        
        return result
    
    @classmethod
    def optimize_prompts_dict(cls, prompts_dict):
        """
        Оптимизирует весь словарь промптов
        
        Args:
            prompts_dict (dict): Словарь промптов
            
        Returns:
            dict: Оптимизированный словарь промптов
        """
        optimized = {}
        
        for key, prompt in prompts_dict.items():
            optimized[key] = cls.optimize_prompt(prompt, key)
        
        return optimized
    
    @classmethod
    def validate_prompt_safety(cls, prompt):
        """
        Проверяет безопасность промпта для API
        
        Args:
            prompt (str): Промпт для проверки
            
        Returns:
            tuple: (is_safe: bool, issues: list)
        """
        issues = []
        
        # Проверка длины
        if len(prompt) > 150:
            issues.append(f"Слишком длинный ({len(prompt)} символов)")
        
        # Проверка на повторяющиеся слова
        words = prompt.lower().split()
        word_count = {}
        for word in words:
            word_count[word] = word_count.get(word, 0) + 1
        
        repeated = [word for word, count in word_count.items() if count > 2]
        if repeated:
            issues.append(f"Повторяющиеся слова: {', '.join(repeated[:3])}")
        
        # Проверка на проблемные символы
        problematic_chars = ['№', '§', '©', '®', '™', '€', '£', '¥']
        if any(char in prompt for char in problematic_chars):
            issues.append("Содержит проблемные символы")
        
        is_safe = len(issues) == 0
        return is_safe, issues


def optimize_prompts_for_api(prompts_dict):
    """
    Универсальная функция оптимизации промптов для API
    Предотвращает зависания и ошибки генерации
    """
    return PromptOptimizer.optimize_prompts_dict(prompts_dict) 