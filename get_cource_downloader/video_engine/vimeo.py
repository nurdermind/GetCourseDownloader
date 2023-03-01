import json
import os
import re
import subprocess
from urllib.parse import urljoin

import base64
import requests
import shutil

from loguru import logger
from subprocess import run
from vimeo_downloader import Vimeo

from .base import BaseVideo


class VimeoVideo(BaseVideo):

    @staticmethod
    def is_this_that_engine(iframe_url):
        return 'player.vimeo' in iframe_url

    @property
    def video_url(self):
        vimeo_video = Vimeo(self.iframe_url, self.lesson_url)
        if vimeo_video.streams:
            progressive_max_quality = int(re.match(r'(\d+)p', vimeo_video.best_stream.quality).group(1))
            segments_max_quality = max(self._get_5vod_data()['video'], key=lambda x: x['height'])['height']
            if progressive_max_quality >= segments_max_quality:
                return vimeo_video.best_stream.direct_url
        return None

    def download(self, output_file=None):
        if output_file is None:
            output_file = self.title + '.mp4'
        video_url = self.video_url
        if video_url:
            self._download(video_url, output_file)
        else:
            self._download_if_not_progressive_urls(output_file)

        return output_file

    def _download_if_not_progressive_urls(self, output_file):
        vod_data = self._get_5vod_data()
        avc_url = self._get_avc_url()

        video = max(vod_data['video'], key=lambda x: x['height'])
        audio = max(vod_data['audio'], key=lambda x: x['bitrate'])
        base_url = urljoin(avc_url, vod_data['base_url'])

        if 'index_segment' in video:
            video['index_segment'] = video['index_segment'].split('&')[0]
            video_url = urljoin(base_url, video['base_url'] + video['index_segment'])
            video_path = self._download(video_url, output_file + '_silent.mp4')
        else:
            init_segment_bytes = base64.b64decode(video['init_segment'])
            segments = [urljoin(base_url, video['base_url'] + s['url']) for s in video['segments']]
            video_path = self._download_segments_to_one_file(init_segment_bytes, segments,
                                                             output_file=output_file + '_silent.mp4')

        if 'index_segment' in audio:
            audio['index_segment'] = audio['index_segment'].split('&')[0]
            audio_url = urljoin(base_url, audio['base_url'] + audio['index_segment'])
            audio_path = self._download(audio_url, output_file + '_silent.mp3')
        else:
            init_segment_bytes = base64.b64decode(audio['init_segment'])
            segments = [urljoin(base_url, audio['base_url'] + s['url']) for s in audio['segments']]
            audio_path = self._download_segments_to_one_file(init_segment_bytes, segments,
                                                             output_file=output_file + '_silent.mp3')
        self._concatenate_video_and_audio(video_path=video_path, audio_path=audio_path, output_file=output_file)
        os.remove(video_path)
        os.remove(audio_path)
        return output_file

    @staticmethod
    def _download_segments_to_one_file(init_segment: bytes, urls, output_file):
        with open(output_file, 'wb') as out_file:
            out_file.write(init_segment)
            for url in urls:
                response = requests.get(url, stream=True)
                response.raise_for_status()
                shutil.copyfileobj(response.raw, out_file)
                del response
        return output_file

    def _concatenate_video_and_audio(self, video_path, audio_path, output_file):
        process = run(['ffmpeg', '-y',
                       '-i', video_path,
                       '-i', audio_path,
                       '-c:v', 'copy',
                       '-c:a', 'aac',
                       output_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        process.check_returncode()
        return output_file

    def _get_config_from_iframe(self, html):
        if s := re.search(r'window.playerConfig = ({".+"}})', str(html)):
            return json.loads(s.group(1))

    def _get_avc_url(self):
        vimeo_video = Vimeo(self.iframe_url, self.lesson_url)
        config = vimeo_video._extractor()
        return config['request']['files']['dash']['cdns']['akfire_interconnect_quic']['avc_url']

    def _get_5vod_data(self):
        avc_url = self._get_avc_url()
        r_5vod = requests.get(avc_url)
        r_5vod.raise_for_status()
        return r_5vod.json()
