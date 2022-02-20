import pandas as pd
import os
import unicodedata


def get_account_id(account_data, account_name):
    """
    Получить id вакансии по каждому кандидату.
    :param vacancies_data: Датасет содержащий данные о вакансиях по организации, полученный из API ХФ.
    :param applicant_vacancy_name: Название вакансии по кандидату.
    :return: id вакансии для конкретного кандидата.
    """
    for account in account_data:
        if account['name'] == account_name:
            return account['id']


def normalize_price(appl_money):
    """
    Если тип данных не float - нужно получить все цифры из строки и собрать из них число.
    :param appl_money:
    :return:
    """
    if type(appl_money) == float:
        return int(appl_money)
    else:
        return "".join([i for i in appl_money.strip() if i.isdigit()])


def get_applicant_data(appl_data):
    """
    Функция собирает обязательные поля которые передаются в body при post-запросе
    :param appl_data:
    :return:
    """
    full_name = appl_data['ФИО'].strip().split(' ')
    body_data = {"first_name": full_name[1],
                 "last_name": full_name[0],
                 "money": normalize_price(appl_data['Ожидания по ЗП'])
                 }
    if len(full_name) == 3:
        body_data['middle_name'] = full_name[2]
    return body_data


def get_applicant_vacancy_status_id(vacancy_status_data, applicant_status_name):
    """
    Получить id статуса вакансии по каждому кандидату.
    :param vacancy_status_data: Датасет содержащий статусы вакансий по организации, полученный из API ХФ.
    :param applicant_status_name: Название статуса вакансии по кандидату.
    :return: id статуса вакансии для конкретного кандидата.
    """
    for vacancy_status in vacancy_status_data:
        if vacancy_status['name'] == applicant_status_name:
            return vacancy_status['id']


def get_applicant_vacancy_id(vacancies_data, applicant_vacancy_name):
    """
    Получить id вакансии по каждому кандидату.
    :param vacancies_data: Датасет содержащий данные о вакансиях по организации, полученный из API ХФ.
    :param applicant_vacancy_name: Название вакансии по кандидату.
    :return: id вакансии для конкретного кандидата.
    """
    for vacancy in vacancies_data:
        if vacancy['position'] == applicant_vacancy_name:
            return vacancy['id']


def get_vacancy_data(vacancy_id, vacancy_status_id, comment, file_id):
    """
    В функцию приходят данные для загрузки кандидата на вакансию.
    :param vacancy_id:
    :param vacancy_status_id:
    :param comment:
    :param file_id:
    :return: dict
    """
    vacancy_data = {
        "vacancy": vacancy_id,
        "status": vacancy_status_id,
        "comment": comment,
        "files": [file_id]
    }
    return vacancy_data


def normalize_str(some_str):
    """
    Unicode-коды некоторых символов в имени файла и соответствующем ему имени кандидата из экселя - различаются.
    Соответственно их не получается сравнить. Для того чтобы привести имя файла и имя кандидата к одному виду
    используется метод normalize.
    :param some_str:
    :return:
    """
    return unicodedata.normalize('NFKC', some_str)


def get_file_path(position, applicant_full_name):
    """
    Функция возвращает относительный путь к файлу с резюме кандидата.
    :param position: Должность. Она же папка, в которой хранятся резюме кандидатов по определенной должности
    :param applicant_full_name: Полное имя кандидата. Так называется файл с резюме кандидата (не включая расширение).
    :return: Относительный путь к файлу резюме
    """
    for folder, subfolders, files in os.walk(f'data/{position}/'):
        for file in files:
            if normalize_str(file.split('.')[0].strip().lower()) == normalize_str(applicant_full_name.strip().lower()):
                return f'{folder}{file}'


def load_data_from_xlsx_to_list(xlsx_file_name, rows=None):
    """
    Функция загружает данные из xlsx файла в список, который хранит словари. Каждый словарь - это данные из строки
    таблицы.
    :param xlsx_file_name: название файла
    :param rows: Номер строки с которой будет продолжено чтение xlsx-файла.
    :return: list
    """
    if rows is None:
        load_data = pd.read_excel(xlsx_file_name,
                                  usecols=['Должность', 'ФИО', 'Ожидания по ЗП',
                                           'Комментарий', 'Статус'])
    else:
        load_data = pd.read_excel(xlsx_file_name, skiprows=[i + 1 for i in range(rows)],
                                  usecols=['Должность', 'ФИО', 'Ожидания по ЗП',
                                           'Комментарий', 'Статус'])

    return load_data.to_dict(orient='records')


def write_progress_file(file_to_write, count_rows):
    """
    Функция записывает значение count_rows в файл settings.PROGRESS_FILE
    :param file_to_write: Файл куда будем писать
    :param count_rows: Значение которое будем писать
    :return:
    """
    with open(file_to_write, 'wt') as f:
        f.write(str(count_rows))


def read_progress_file(file_to_read):
    """
    Функция читает из файла settings.PROGRESS_FILE текущее значение
    :param file_to_read: Файл который будем читать
    :return: int текущее кол-во загруженных в ХФ кандидатов.
    """
    if os.path.exists(file_to_read):
        with open(file_to_read) as f:
            try:
                count_rows = int(f.read())
            except ValueError:
                print(f'Error while processing data in file {file_to_read}. ValueError.')
    else:
        count_rows = 0

    return count_rows
