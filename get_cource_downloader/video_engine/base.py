import os
import requests
from tqdm import tqdm
from loguru import logger
from abc import ABC, abstractmethod


class BaseVideo(ABC):

    def __init__(self, title, iframe_url, lesson_url):
        self.title = title
        self.iframe_url = iframe_url
        self.lesson_url = lesson_url

    def download(self, output_file=None):
        if output_file is None:
            output_file = self.title + '.mp4'

        with requests.get(self.video_url, stream=True) as response:
            if response.status_code == 200:
                with open(output_file, 'wb') as f:
                    total_size = int(response.headers.get('Content-Length'))
                    with tqdm(total=total_size, unit='B', unit_scale=True, desc=os.path.basename(output_file),
                              leave=False) as pbar:
                        for chunk in response.iter_content(1024 * 1024):
                            f.write(chunk)
                            pbar.update(len(chunk))
            else:
                logger.error(f'{response.status_code} - {self.video_url}')

        return output_file

    @staticmethod
    @abstractmethod
    def is_this_that_engine(iframe_url):
        pass

    @property
    @abstractmethod
    def video_url(self):
        pass