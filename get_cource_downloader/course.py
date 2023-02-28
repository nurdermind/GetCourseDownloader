import os

from tqdm import tqdm

from get_cource_downloader.web import WebSession
from .section import Section


class Course(WebSession):

    def download(self, output_dir, show_progress=True):
        output_dir = self._get_output_dir_path(output_dir, self.title)
        for section in tqdm(self.get_sections(), position=0, desc="Скачивание разделов", leave=True, colour='green', unit='раздел'):
            section.download(output_dir)

    def get_sections(self):
        sections = [Section(url=self.url, cookie_path=self.cookie_path)]
        sections_html = self.html.find_all('a', href=lambda href: href and '/teach/control/stream' in href)
        for section_html in sections_html:
            section_url = self._get_absolute_url(section_html.get('href'))
            sections.append(Section(url=section_url, cookie_path=self.cookie_path))

        return sections
