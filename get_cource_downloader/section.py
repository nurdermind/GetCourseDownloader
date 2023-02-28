import os

from tqdm import tqdm

from get_cource_downloader.web import WebSession
from .lesson import Lesson


class Section(WebSession):

    def download(self, output_dir):
        output_dir = self._get_output_dir_path(output_dir, self.title)
        for lesson in tqdm(self.get_lessons(), desc=f"Скачивание раздела {self.title}", leave=True, colour='blue',
                           unit='видео'):
            lesson.download(output_dir)

    def get_lessons(self):
        lessons = []
        for lesson_html in self.html.find_all('div', 'link title'):
            lesson_url = self._get_absolute_url(lesson_html.get('href'))
            lessons.append(Lesson(url=lesson_url, cookie_path=self.cookie_path))
        return lessons
