import os
import time
import glob
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


def wait_for_manual_login():
    """Ожидает, пока пользователь войдет в систему вручную"""
    print("\n===== ИНСТРУКЦИЯ ПО ВХОДУ В СИСТЕМУ =====")
    print("1. Войдите в свой аккаунт Phantombuster в открывшемся окне браузера")
    print("2. После успешного входа нажмите Enter в этом окне консоли")
    print("=============================================")
    input("Нажмите Enter после входа в систему... ")
    print("Спасибо! Продолжаем выполнение программы...")


def setup_driver():
    """Настраивает и возвращает драйвер Chrome"""
    chrome_options = Options()
    # Добавляем опции для повышения надежности
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    # Раскомментируйте строку ниже, если вам не нужно видеть браузер
    # chrome_options.add_argument("--headless")
    
    # Ищем Chrome binary в папке chrome-win64 и других стандартных местах
    chrome_binary_paths = [
        os.path.join(os.getcwd(), "chrome-win64", "chrome.exe"),  # В папке chrome-win64 проекта
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",  # Стандартный путь Windows
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",  # Стандартный путь Windows x86
        "/usr/bin/google-chrome",  # Стандартный путь Linux
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",  # Mac
    ]
    
    chrome_binary = None
    for path in chrome_binary_paths:
        if os.path.exists(path):
            chrome_binary = path
            print(f"Найден Chrome browser: {path}")
            break
    
    if chrome_binary:
        chrome_options.binary_location = chrome_binary
    else:
        print("Внимание: Chrome browser не найден в стандартных местоположениях.")
        print("Будет использован Chrome по умолчанию, если он установлен в системе.")
    
    # Расширенный список возможных путей к chromedriver
    possible_paths = [
        os.path.join(os.getcwd(), "chromedriver.exe"),  # Windows в текущей директории
        os.path.join(os.getcwd(), "webdriver", "chromedriver.exe"),  # Windows в папке webdriver
        os.path.join(os.getcwd(), "drivers", "chromedriver.exe"),  # Еще один вариант
        "./chromedriver.exe",
        "./webdriver/chromedriver.exe",
        "../webdriver/chromedriver.exe",
        # Linux/Mac пути
        os.path.join(os.getcwd(), "chromedriver"),
        os.path.join(os.getcwd(), "webdriver", "chromedriver"),
        "./chromedriver",
        "./webdriver/chromedriver"
    ]
    
    # Перебираем все возможные пути и пытаемся использовать первый найденный chromedriver
    for path in possible_paths:
        if os.path.exists(path):
            print(f"Найден ChromeDriver: {path}")
            try:
                service = Service(executable_path=path)
                driver = webdriver.Chrome(service=service, options=chrome_options)
                driver.maximize_window()
                print("ChromeDriver успешно инициализирован")
                return driver
            except Exception as e:
                print(f"Не удалось запустить ChromeDriver по пути {path}: {e}")
                continue
    
    # Если все методы не сработали, выдаем инструкции по ручной установке
    print("\n===== ОШИБКА ИНИЦИАЛИЗАЦИИ WEBDRIVER =====")
    print("Не удалось найти ChromeDriver.")
    print("\nРекомендации по решению проблемы:")
    print("1. Убедитесь, что Google Chrome установлен в системе.")
    print("2. Скачайте ChromeDriver, соответствующий вашей версии Chrome:")
    print("   https://chromedriver.chromium.org/downloads")
    print("3. Поместите файл chromedriver.exe в одну из следующих папок:")
    print("   - Текущую директорию проекта")
    print("   - В папку 'webdriver' внутри директории проекта")
    print("\nПроверить версию Chrome можно, открыв адрес chrome://version/ в браузере")
    print("==========================================")
    
    raise FileNotFoundError("ChromeDriver не найден")


def parse_table(driver):
    """Извлекает данные из текущей таблицы на странице"""
    try:
        # Ожидаем, пока таблица загрузится
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        
        # Получаем заголовки таблицы
        headers = []
        header_elements = driver.find_elements(By.CSS_SELECTOR, "table th")
        for header in header_elements:
            headers.append(header.text)
        
        # Получаем строки таблицы
        rows = []
        row_elements = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
        for row_elem in row_elements:
            row_data = []
            cell_elements = row_elem.find_elements(By.TAG_NAME, "td")
            for cell in cell_elements:
                row_data.append(cell.text)
            if row_data:  # Проверка, что строка не пустая
                rows.append(row_data)
        
        # Создаем DataFrame
        if rows and headers and len(rows[0]) == len(headers):
            df = pd.DataFrame(rows, columns=headers)
            return df
        else:
            print("Предупреждение: несоответствие в размерах данных!")
            print(f"Заголовки ({len(headers)}): {headers}")
            print(f"Первая строка ({len(rows[0]) if rows else 0}): {rows[0] if rows else []}")
            # Создаем DataFrame даже при несоответствии
            if rows:
                return pd.DataFrame(rows)
            return None
    except Exception as e:
        print(f"Ошибка при парсинге таблицы: {e}")
        return None


def select_page_size(driver, size=30):
    """Выбирает количество строк на странице"""
    try:
        # Находим селект для выбора количества строк
        select_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "csvInteractiveTablePageSizeSelect"))
        )
        select_element.click()
        
        # Выбираем опцию с нужным значением
        option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, f"option[value='{size}']"))
        )
        option.click()
        print(f"Выбрано {size} строк на странице")
        
        # Ждем обновления таблицы
        time.sleep(2)
    except Exception as e:
        print(f"Ошибка при выборе количества строк: {e}")
        print("Продолжение с текущими настройками...")


def get_total_pages(driver):
    """Определяет общее количество страниц путем парсинга элементов пагинации"""
    try:
        # Ждем загрузки элементов пагинации
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".tw-font-qanelas.tw-flex.tw-min-w-2.tw-justify-center.tw-font-medium.tw-text-body-s"))
        )
        
        # Получаем все элементы с номерами страниц
        page_elements = driver.find_elements(By.CSS_SELECTOR, ".tw-font-qanelas.tw-flex.tw-min-w-2.tw-justify-center.tw-font-medium.tw-text-body-s")
        
        # Извлекаем номера страниц и находим максимальный
        max_page = 1
        for elem in page_elements:
            try:
                page_num = int(elem.text.strip())
                max_page = max(max_page, page_num)
            except (ValueError, TypeError):
                continue
        
        print(f"Обнаружено всего страниц: {max_page}")
        return max_page
    except Exception as e:
        print(f"Ошибка при определении количества страниц: {e}")
        return 1  # По умолчанию считаем, что есть только 1 страница, если определение не удалось


def click_next_button(driver):
    """Пытается нажать на кнопку 'Далее' используя различные методы"""
    # Метод 1: Поиск по аналитическому атрибуту
    try:
        next_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[analyticsval1='goToNextPageLink']"))
        )
        if "disabled" not in next_button.get_attribute("class"):
            next_button.click()
            print("Переход на следующую страницу (метод 1)")
            return True
    except Exception as e:
        print(f"Метод 1 не сработал: {e}")
    
    # Метод 2: Поиск по SVG иконке
    try:
        next_button = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "svg.fa-chevron-right"))
        )
        # Кликаем по родительскому элементу button
        parent_button = next_button.find_element(By.XPATH, "./ancestor::button")
        if "disabled" not in parent_button.get_attribute("class"):
            parent_button.click()
            print("Переход на следующую страницу (метод 2)")
            return True
    except Exception as e:
        print(f"Метод 2 не сработал: {e}")
    
    # Метод 3: Использование XPath
    try:
        # Пробуем оба варианта XPath
        xpaths = [
            "/html/body/div[2]/div/div[2]/main/div/section[2]/div/div[2]/div[5]/div[2]/div[2]/button[2]",
            "/html/body/div[1]/div/div[2]/main/div/section[2]/div/div[2]/div[5]/div[2]/div[2]/button[2]"
        ]
        for xpath in xpaths:
            try:
                next_button = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                if "disabled" not in next_button.get_attribute("class"):
                    next_button.click()
                    print(f"Переход на следующую страницу (метод 3, XPath: {xpath})")
                    return True
            except:
                continue
    except Exception as e:
        print(f"Метод 3 не сработал: {e}")
    
    # Метод 4: JavaScript
    try:
        js_script = """
        let nextButton = Array.from(document.querySelectorAll('button')).find(
            button => button.querySelector('svg.fa-chevron-right') && !button.disabled
        );
        if (nextButton) {
            nextButton.click();
            return true;
        }
        return false;
        """
        result = driver.execute_script(js_script)
        if result:
            print("Переход на следующую страницу (метод 4, JavaScript)")
            return True
    except Exception as e:
        print(f"Метод 4 не сработал: {e}")
    
    print("Не удалось найти или нажать кнопку 'Далее'. Возможно, достигнута последняя страница.")
    return False


def main():
    # URL сайта
    url = "https://phantombuster.com/7912167802097990/phantoms/5388867849466815/console"
    
    # Создаем папку для результатов, если её нет
    if not os.path.exists("Results"):
        os.makedirs("Results")
    
    driver = setup_driver()
    
    try:
        # Открываем сайт
        driver.get(url)
        print(f"Открыта страница: {url}")
        
        # Ждем, пока пользователь войдет в систему вручную
        wait_for_manual_login()
        
        # Выбираем 30 строк на странице
        select_page_size(driver, 30)
        
        # Определяем общее количество страниц
        total_pages = get_total_pages(driver)
        
        page_num = 1
        has_next_page = True
        total_records = 0
        
        while has_next_page and page_num <= total_pages:
            print(f"\n=== Обработка страницы {page_num} из {total_pages} ===")
            
            # Даем время для полной загрузки таблицы
            time.sleep(2)
            
            # Парсим текущую таблицу
            df = parse_table(driver)
            
            if df is not None and not df.empty:
                # Сохраняем в CSV
                csv_path = os.path.join("Results", f"{page_num}.csv")
                df.to_csv(csv_path, index=False, encoding='utf-8')
                total_records += len(df)
                print(f"Сохранена таблица в {csv_path} ({len(df)} записей)")
            else:
                print(f"Не удалось получить данные с страницы {page_num}")
            
            # Проверяем, дошли ли мы до последней страницы
            if page_num >= total_pages:
                print("Достигнута последняя страница (по счетчику)")
                has_next_page = False
            else:
                # Пытаемся перейти на следующую страницу
                if click_next_button(driver):
                    page_num += 1
                    # Ждем загрузки новой таблицы
                    time.sleep(3)
                else:
                    has_next_page = False
        
        print("\n=== Парсинг завершен. Объединение CSV файлов... ===")
        
        # Объединяем все CSV файлы
        csv_files = sorted(glob.glob(os.path.join("Results", "*.csv")), 
                           key=lambda x: int(os.path.basename(x).split('.')[0]))
        
        if csv_files:
            dfs = []
            for file in csv_files:
                df = pd.read_csv(file, encoding='utf-8')
                dfs.append(df)
            
            if dfs:
                # Объединяем все DataFrame
                combined_df = pd.concat(dfs, ignore_index=True)
                
                # Сохраняем объединенный файл
                combined_df.to_csv("Results.csv", index=False, encoding='utf-8')
                print(f"Все таблицы объединены в Results.csv")
                print(f"Итого собрано: {len(combined_df)} записей из {page_num} страниц")
            else:
                print("Не найдены данные для объединения")
        else:
            print("Не найдены CSV файлы для объединения")
    
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Закрываем браузер
        driver.quit()
        print("\nБраузер закрыт. Программа завершена.")


if __name__ == "__main__":
    main()