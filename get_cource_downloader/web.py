import os
import pickle
from urllib.parse import urlparse, urljoin

from bs4 import BeautifulSoup
from fake_headers import Headers
from requests import Session
from requests.cookies import RequestsCookieJar

from .save_mixin import SaveMixin


class WebSession(SaveMixin):

    def __init__(self, url, cookie_path):
        assert url.startswith('https://')
        self.domain = urlparse(url).netloc
        self.url = url

        self._session = Session()
        headers = Headers(
            browser="chrome",  # Generate only Chrome UA
            os="win",  # Generate ony Windows platform
            headers=True  # generate misc headers
        ).generate()
        self._session.headers.update(headers)
        self.cookie_path = cookie_path
        cookies = self._get_cookie_from_file(self.cookie_path)
        cookie_jar = RequestsCookieJar()
        for cookie in cookies:
            cookie_jar.set(
                name=cookie['name'],
                value=cookie['value'],
                domain=cookie['domain'],
                expires=cookie['expiry'],
                path=cookie['path'],
                secure=not cookie['httpOnly']
            )
        self._session.cookies = cookie_jar

        self.html = self._get_html()
        self.title = self._get_title()

    def _get_cookie_from_file(self, path):
        with open(path, 'rb') as f:
            return pickle.load(f)

    def _get_title(self):
        return self.html.find('title').text.replace(os.path.sep, '|')

    def _get_html(self):
        r = self._session.get(self.url)
        r.raise_for_status()
        return BeautifulSoup(r.text, 'html.parser')

    def _get_absolute_url(self, relative_url):
        url = urljoin('https://' + self.domain, relative_url)
        return url
