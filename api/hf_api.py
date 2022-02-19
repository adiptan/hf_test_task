import requests
from misc import settings


class HFApi:
    def __init__(self, token, method_url):
        self._token = token
        self._method_url = method_url

    def api_get_method(self):
        get_data = requests.get(f'{settings.API_END_POINT}{self._method_url}',
                                headers={'Authorization': f'Bearer {self._token}'})
        return get_data.json()


class PostMethod(HFApi):
    def __init__(self, token, method_url, body_data):
        super().__init__(token, method_url)
        self._body_data = body_data

    def add_new_applicant(self):
        applicant_post_data = requests.post(f'{settings.API_END_POINT}{self._method_url}', json=self._body_data,
                                            headers={'Authorization': f'Bearer {self._token}'})
        return applicant_post_data.json()


class PostFile(HFApi):
    def __init__(self, token, method_url, file_name):
        super().__init__(token, method_url)
        self.file_name = file_name

    def upload_file_by_api(self):
        applicant_post_data = requests.post(f'{settings.API_END_POINT}{self._method_url}',
                                            files={'file': (self.file_name, open(self.file_name, 'rb'), 'text/csv')},
                                            headers={'Authorization': f'Bearer {self._token}', 'X-File-Parse': 'true'})
        return applicant_post_data.json()
