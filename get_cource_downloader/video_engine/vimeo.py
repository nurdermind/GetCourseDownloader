from vimeo_downloader import Vimeo

from .base import BaseVideo


class VimeoVideo(BaseVideo):

    @staticmethod
    def is_this_that_engine(iframe_url):
        return 'player.vimeo' in iframe_url

    @property
    def video_url(self):
        return Vimeo(self.iframe_url, self.lesson_url).streams[-1].direct_url
