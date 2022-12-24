import gspread
import re
from datetime import datetime
from gspread.exceptions import WorksheetNotFound

# исходные данные json ключа, файла с логами и google таблицы
KEY = "key.json"
FILE = "logs_example.txt"
ACCESS_LINK = "https://docs.google.com/spreadsheets/d/1MxOJjUa5BXydrZree0YLoAEdlK4dswuPrwkA7y_fT8E/edit?usp=sharing"


# создание файла с логами
def create_logs_example():
    file = FILE
    log_n = 1
    with open(file, 'a') as the_file:
        for i in range(50):
            date_and_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            log_string = f"{date_and_time} log number #{log_n}\n"
            the_file.write(log_string)
            log_n += 1
    print("Test logs are created")


# имитация получения логов
def get_log():
    with open(FILE, 'r') as f_read:
        data = f_read.read().splitlines(True)
        log = data[:1]
    with open(FILE, 'w') as f_write:
        f_write.writelines(data[1:])
    return log


def main():

    # создается файл с примерами логов
    create_logs_example()

    # подключение к таблице
    gc = gspread.service_account(filename=KEY)
    wks = gc.open_by_url(ACCESS_LINK)

    # получение сегодняшней даты и создание листа в таблице
    # каждому дню соответствует свой лист
    current_date = datetime.today().strftime('%Y-%m-%d')
    try:
        sh = wks.worksheet(current_date)
    except WorksheetNotFound:
        sh = wks.add_worksheet(title=current_date, rows=1000, cols=20)

    row = 1
    log_flow = True

    # цикл с получением логов
    while log_flow:
        # проверка даты
        # если наступил следующий день - логи будут помещаться в новый лист
        date_today = datetime.today().strftime('%Y-%m-%d')
        if current_date != date_today:
            current_date = date_today
            sh = wks.add_worksheet(title=current_date, rows=1000, cols=20)
            row = 1

        # получение лога, даты, времени, текста лога
        try:
            log = get_log()[0]
            date = re.search(r'\d{4}-\d{2}-\d{2}', log).group()
            log = log.replace(date, '')
            time = re.search(r'\d{2}:\d{2}:\d{2}', log).group()
            log = log.replace(time, '')

            # помещение в таблицу
            cell = f"A{row}"
            sh.update(cell, [[time, log, date]])

            print(f"{log} added")
            row += 1
        except Exception:
            print("No more logs")
            log_flow = False

    print("All logs has been added")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e.args)
