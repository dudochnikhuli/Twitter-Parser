import os
import json
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
from webdriver_manager.chrome import ChromeDriverManager


def load_cookies(driver, cookies_file):
    """Загружает cookies из JSON файла"""
    try:
        with open(cookies_file, 'r') as file:
            cookies = json.load(file)
            for cookie in cookies:
                # Selenium не может обрабатывать некоторые атрибуты cookie
                if 'sameSite' in cookie:
                    if cookie['sameSite'] == 'None':
                        cookie['sameSite'] = 'Strict'
                if 'expiry' in cookie:
                    del cookie['expiry']
                driver.add_cookie(cookie)
        print("Cookies успешно загружены")
    except Exception as e:
        print(f"Ошибка при загрузке cookies: {e}")


def setup_driver():
    """Настраивает и возвращает драйвер Chrome"""
    chrome_options = Options()
    # Добавляем опции для повышения надежности
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    # Раскомментируйте строку ниже, если вам не нужно видеть браузер
    # chrome_options.add_argument("--headless")
    
    try:
        # Способ 1: Использование менеджера с явным указанием пути для кэширования
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        
        # Создаем временную директорию для драйвера, если её нет
        driver_path = os.path.join(os.getcwd(), "webdriver")
        if not os.path.exists(driver_path):
            os.makedirs(driver_path)
            
        service = Service(ChromeDriverManager(path=driver_path).install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.maximize_window()
        return driver
        
    except Exception as e:
        print(f"Ошибка при установке драйвера через менеджер: {e}")
        
        try:
            # Способ 2: Использование ChromeDriver напрямую (требуется ручная загрузка)
            # Загрузите ChromeDriver с https://chromedriver.chromium.org/downloads
            # и поместите chromedriver.exe в корневую папку проекта
            chromedriver_path = os.path.join(os.getcwd(), "chromedriver.exe")
            
            if os.path.exists(chromedriver_path):
                print(f"Используем локальный ChromeDriver: {chromedriver_path}")
                service = Service(executable_path=chromedriver_path)
                driver = webdriver.Chrome(service=service, options=chrome_options)
                driver.maximize_window()
                return driver
            else:
                print(f"ChromeDriver не найден по пути: {chromedriver_path}")
                print("Пожалуйста, скачайте подходящую версию ChromeDriver и поместите в корневую папку проекта")
                raise FileNotFoundError(f"ChromeDriver не найден: {chromedriver_path}")
                
        except Exception as e2:
            print(f"Все способы установки драйвера не удались: {e2}")
            raise


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


def main():
    # Путь к файлу с cookies
    cookies_file = "Cookies.json"
    
    # URL сайта
    url = "https://phantombuster.com/7912167802097990/phantoms/5388867849466815/console"
    
    # XPath кнопки "далее"
    next_button_xpath = "/html/body/div[1]/div/div[2]/main/div/section[2]/div/div[2]/div[5]/div[2]/div[2]/button[2]"
    
    # Создаем папку для результатов, если её нет
    if not os.path.exists("Results"):
        os.makedirs("Results")
    
    driver = setup_driver()
    
    try:
        # Открываем сайт
        driver.get(url)
        print(f"Открыта страница: {url}")
        
        # Ждем 3 секунды после перехода
        time.sleep(3)
        
        # Загружаем cookies для авторизации
        load_cookies(driver, cookies_file)
        
        # Обновляем страницу после загрузки cookies
        driver.refresh()
        time.sleep(3)
        
        # Выбираем 30 строк на странице
        select_page_size(driver, 30)
        
        page_num = 1
        has_next_page = True
        
        while has_next_page:
            print(f"Обработка страницы {page_num}")
            
            # Парсим текущую таблицу
            df = parse_table(driver)
            
            if df is not None and not df.empty:
                # Сохраняем в CSV
                csv_path = os.path.join("Results", f"{page_num}.csv")
                df.to_csv(csv_path, index=False, encoding='utf-8')
                print(f"Сохранена таблица в {csv_path}")
            else:
                print(f"Не удалось получить данные с страницы {page_num}")
            
            # Проверяем, есть ли кнопка "далее" и активна ли она
            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, next_button_xpath))
                )
                
                # Проверяем, не отключена ли кнопка
                if "disabled" in next_button.get_attribute("class") or not next_button.is_enabled():
                    print("Достигнута последняя страница")
                    has_next_page = False
                else:
                    # Кликаем по кнопке "далее"
                    next_button.click()
                    print("Переход на следующую страницу")
                    
                    # Ждем загрузки новой таблицы
                    time.sleep(2)
                    page_num += 1
            except (TimeoutException, NoSuchElementException) as e:
                print(f"Кнопка 'далее' не найдена или не доступна: {e}")
                has_next_page = False
        
        print("Парсинг завершен. Объединение CSV файлов...")
        
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
                print("Все таблицы объединены в Results.csv")
            else:
                print("Не найдены данные для объединения")
        else:
            print("Не найдены CSV файлы для объединения")
    
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    
    finally:
        # Закрываем браузер
        driver.quit()
        print("Браузер закрыт. Программа завершена.")


if __name__ == "__main__":
    main()