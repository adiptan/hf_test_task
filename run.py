import argparse
import logging
from api import hf_api
from misc import (common_func, settings)

# Log config
logging.basicConfig(filename='importer.log', format='%(asctime)s - %(message)s', level=logging.DEBUG)
logging.debug('Start script.')

# Script arguments config
arg_parser = argparse.ArgumentParser(description='Batch of args.')
arg_parser.add_argument("--base_location", dest="base_location", help="Directory where base located.", required=True)
arg_parser.add_argument("--token", dest="token", help="Api token.", required=True)

args = arg_parser.parse_args()

if __name__ == '__main__':
    # Читаем прогресс-файл
    number_or_read_rows = common_func.read_progress_file(settings.PROGRESS_FILE)

    try:
        # Загруженную базу кладу в переменную, чтобы каждый раз не ходить в файл.
        loaded_data = common_func.load_data_from_xlsx_to_list(args.base_location, number_or_read_rows)
    except FileNotFoundError:
        logging.debug(f'FileNotFoundError error occurred \nNo such file - {args.base_location}.')
        print(f'FileNotFoundError error occurred \nNo such file - {args.base_location}.')
        exit(0)
    try:
        # Данные ниже меняться не будут, по-этому кладу их в переменные, чтобы каждый раз не ходить за ними в API.
        get_account_data = hf_api.HFApi(args.token, 'accounts')
        account_id = common_func.get_account_id(get_account_data.api_get_method()['items'], settings.ACCOUNT_NAME)
        get_vacancy_statuses = hf_api.HFApi(args.token, f'accounts/{account_id}/vacancies/statuses')
        get_vacancies = hf_api.HFApi(args.token, f'accounts/{account_id}/vacancies')

        for applicant_data in loaded_data:
            # 1. Получаем данные из xlsx. Добавляем каждому кандидату в словарь путь до файла с резюме.
            applicant_data['file_path'] = common_func.get_file_path(applicant_data['Должность'], applicant_data['ФИО'])
            # 2. Загружаем кандидатов в ХФ. По каждому кандидату, нужно забрать applicant_id который вернул ХФ.
            post_method = hf_api.PostMethod(args.token, f'accounts/{account_id}/applicants',
                                            common_func.get_applicant_data(applicant_data))
            applicant_id = post_method.add_new_applicant()['id']
            # 2.1 Загрузить файл резюме по кандидату в БД.
            upload_file = hf_api.PostFile(args.token, f'accounts/{account_id}/upload', applicant_data["file_path"])
            file_id = upload_file.upload_file_by_api()['id']
            # 3. Получить id статус вакансии для кандидата.
            vacancy_status_id = common_func.get_applicant_vacancy_status_id(
                get_vacancy_statuses.api_get_method()['items'],
                applicant_data['Статус'])
            # 4. Получить id вакансии на которую нужно перевести кандидата.
            vacancy_id = common_func.get_applicant_vacancy_id(get_vacancies.api_get_method()['items'],
                                                              applicant_data['Должность'])
            # 5. Загрузить кандидата на вакансию, добавить кандидату файл резюме и добавить комментарий из файла.
            add_applicant_to_vacancy = hf_api.PostMethod(args.token,
                                                         f'accounts/{account_id}/applicants/{applicant_id}/vacancy',
                                                         common_func.get_vacancy_data(vacancy_id, vacancy_status_id,
                                                                                      applicant_data["Комментарий"],
                                                                                      file_id))
            print(add_applicant_to_vacancy.add_new_applicant())
            logging.debug(f'Applicant {applicant_data["ФИО"]} is fully processed.')

            number_or_read_rows += 1
            common_func.write_progress_file(settings.PROGRESS_FILE, number_or_read_rows)

        logging.debug('End script.')
        # Если скрипт отработал штатно, нужно записать 0 в settings.PROGRESS_FILE
        common_func.write_progress_file(settings.PROGRESS_FILE, 0)

    except KeyError:
        logging.debug(f'KeyError error occurred \n {get_account_data.api_get_method()}')
        print(get_account_data.api_get_method())
        exit(0)
