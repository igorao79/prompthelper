import traceback
from gui import LandingPageGeneratorGUI

if __name__ == '__main__':
    try:
        print("Запуск приложения...")
        app = LandingPageGeneratorGUI()
        print("GUI создан, запускаем mainloop...")
        app.run()
        print("Приложение завершено.")
    except Exception as e:
        print(f"Ошибка при запуске: {e}")
        print("Полная трассировка ошибки:")
        traceback.print_exc()
        input("Нажмите Enter для выхода...") 