#!/usr/bin/env python3
"""
Скрипт для исправления отступов на строке 988 и соседних
"""

def fix_line_988():
    with open('generators/prompt_generator.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixed_count = 0
    
    # Исправляем строки с 987 по 1010 где есть неправильные отступы
    for i in range(986, min(1010, len(lines))):  # строки 987-1010 (индекс начинается с 0)
        line = lines[i]
        line_num = i + 1
        
        # Если строка начинается с 8 пробелов, заменяем на 4
        if line.startswith('        ') and not line.startswith('            '):
            new_line = '    ' + line[8:]
            if line != new_line:
                lines[i] = new_line
                print(f"Исправлена строка {line_num}: {line.strip()[:50]}...")
                fixed_count += 1
    
    # Записываем обратно
    with open('generators/prompt_generator.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"✅ Исправлено {fixed_count} строк!")

if __name__ == "__main__":
    fix_line_988() 