# Phantombuster Web Scraper

Инструмент для автоматизированного сбора данных из таблиц на сайте Phantombuster. Скрипт автоматически авторизуется на сайте, извлекает данные из всех доступных таблиц и сохраняет их в CSV-файлы.

## Технические требования

- Python 3.11.9 (рекомендуется)
- Google Chrome
- Доступ к аккаунту Phantombuster

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/phantombuster-scraper.git
cd phantombuster-scraper
```

2. Создайте и активируйте виртуальное окружение:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/MacOS
python -m venv venv
source venv/bin/activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Настройка

### Настройка авторизации

1. **Подготовка файла cookies**:
   
   Для доступа к закрытым разделам Phantombuster необходимо предоставить cookies авторизованной сессии:

   a. Войдите в свой аккаунт Phantombuster через браузер
   
   b. Используйте расширение для экспорта cookies (например, "EditThisCookie" для Chrome)
   
   c. Экспортируйте cookies в JSON формате
   
   d. Сохраните файл как `Cookies.json` в корневой директории проекта

2. **Проверка URL**:
   
   Убедитесь, что URL в скрипте соответствует нужному разделу Phantombuster:
   ```python
   url = "https://phantombuster.com/7912167802097990/phantoms/5388867849466815/console"
   ```

### Настройка параметров скрапинга

При необходимости можно настроить следующие параметры в файле `main.py`:

- `next_button_xpath` - XPath кнопки перехода на следующую страницу
- Количество отображаемых строк в функции `select_page_size()`
- Время ожидания после загрузки страницы

## Использование

1. Запустите скрипт:
```bash
python main.py
```

2. Скрипт автоматически выполнит следующие действия:
   - Откроет браузер Chrome
   - Перейдет на указанный URL
   - Загрузит cookies для авторизации
   - Выберет отображение 30 строк на странице
   - Последовательно обработает все страницы с таблицами
   - Сохранит каждую таблицу в отдельный CSV файл в папке `Results/`
   - Объединит все таблицы в один файл `Results.csv`

## Структура проекта

```
phantombuster-scraper/
├── main.py                # Основной скрипт для парсинга
├── Cookies.json           # Файл с cookies для авторизации
├── requirements.txt       # Зависимости проекта
├── README.md              # Руководство по проекту
├── Updates.md             # Журнал обновлений
└── Results/               # Папка для сохранения результатов
    ├── 1.csv              # Таблица с первой страницы
    ├── 2.csv              # Таблица со второй страницы
    └── ...
```

## Решение проблем

### 1. Ошибка "WebDriver not found"
- Убедитесь, что Chrome установлен в системе
- Попробуйте обновить webdriver-manager: `pip install --upgrade webdriver-manager`

### 2. Проблемы с авторизацией
- Проверьте актуальность файла Cookies.json (cookies имеют срок действия)
- Экспортируйте cookies заново

### 3. Таблица не парсится корректно
- Проверьте XPath селекторы в функции `parse_table()`
- Добавьте время ожидания для полной загрузки таблицы

### 4. Кнопка "далее" не найдена
- Проверьте XPath кнопки `next_button_xpath`
- Увеличьте время ожидания в WebDriverWait

## Расширение функциональности

### Добавление прокси

Для использования прокси измените настройку драйвера в функции `setup_driver()`:

```python
def setup_driver():
    chrome_options = Options()
    # Добавляем прокси
    chrome_options.add_argument('--proxy-server=http://your-proxy-address:port')
    # ... остальной код
```

### Запуск в режиме headless

Для запуска без визуального интерфейса:

```python
chrome_options.add_argument("--headless")
```

### Сохранение в другие форматы

Для сохранения в Excel формат:

```python
# Импортируйте дополнительные библиотеки
from openpyxl import Workbook

# Изменение в main()
combined_df.to_excel("Results.xlsx", index=False)
```

## Лицензия

MIT