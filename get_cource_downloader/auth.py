import pickle

from selenium.common import TimeoutException
from selenium.webdriver.chrome.service import Service
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from tqdm import tqdm
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from abc import ABCMeta, abstractmethod, abstractproperty, ABC
from urllib.parse import urljoin
from urllib.parse import urlparse

from loguru import logger


class Authentication:

    def __init__(self, site_url: str, headless=True):
        assert site_url.startswith('https://')
        self.domain = urlparse(site_url).netloc
        self.headless = headless

        self.cookie = None

        self._init_options(headless=headless)

        service = Service(executable_path=ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=self._options)

    def _init_options(self, headless: bool) -> None:
        self._options = Options()
        if headless:
            self._options.add_argument('--headless')

    def login(self, login: str = None, password: str = None, cookie_path='cookie.pkl'):

        login_url = self.get_absolute_url('cms/system/login')
        self.driver.get(login_url)

        form = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "form")))

        username_field = form.find_element(By.NAME, "email")
        password_field = form.find_element(By.NAME, "password")
        username_field.send_keys(login)
        password_field.send_keys(password)

        login_button = form.find_element(By.XPATH, "//button[contains(text(), 'Войти')]")
        login_button.click()
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Перейти в аккаунт')]")))

        self.cookie = self.driver.get_cookies()
        if cookie_path:
            with open(cookie_path, 'wb') as file:
                pickle.dump(self.cookie, file)
            logger.info("Куки сохранены в файл: {}".format(cookie_path))

        return self.cookie

    def get_absolute_url(self, relative_url):
        url = urljoin('https://' + self.domain, relative_url)
        return url

    def __del__(self):
        self.driver.close()
        self.driver.quit()
