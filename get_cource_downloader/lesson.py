import os

from get_cource_downloader.web import WebSession
from .video_engine import engines


class Lesson(WebSession):

    def download(self, output_dir=None):
        output_dir = output_dir or self.title
        for i, video in enumerate(self.get_videos()):
            self._create_output_path(output_dir)
            if i > 0:
                output_file = os.path.join(output_dir, self.title + f'_{i}.mp4')
            else:
                output_file = os.path.join(output_dir, self.title + '.mp4')
            video.download(output_file)

    def get_videos(self):
        videos = []

        iframes = self.html.find_all('iframe')
        for iframe in iframes:
            for video_engine in engines:
                iframe_url = self._get_absolute_url(iframe.get('src'))
                if video_engine.is_this_that_engine(iframe_url):
                    videos.append(video_engine(title=self.title, iframe_url=iframe_url, lesson_url=self.url))
        return videos

    def _detect_video_engine(self, iframe_url):
        pass
