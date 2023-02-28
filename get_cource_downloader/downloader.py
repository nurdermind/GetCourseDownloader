from itertools import groupby
from time import sleep

import requests
import os
from tqdm import tqdm
import click
import asyncio
import aiohttp


async def download_file(session, url, output_dir, semaphore, filename=None):
    async with semaphore:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    filename = filename or url.split('/')[-1]
                    with open(os.path.join(output_dir, filename.split('.')[0] + '.mp4'), 'wb') as f:
                        total_size = response.content.total_bytes
                        with tqdm(total=total_size, unit='B', unit_scale=True, desc=filename, leave=False) as pbar:
                            async for chunk in response.content.iter_chunked(1024 * 1024):
                                f.write(chunk)
                                pbar.update(len(chunk))
        except Exception as e:
            print(e)


async def download_all_videos(videos: list[dict], output_dir, semaphore=10):
    for section, group_videos in groupby(videos, lambda x: x['section']):
        section = section.replace('\\', '').replace('/', '')
        section_output_dir = os.path.join(output_dir, section)
        os.makedirs(section_output_dir, exist_ok=True)
        async with aiohttp.ClientSession() as session:
            tasks = [asyncio.ensure_future(download_file(session,
                                                         video['url'],
                                                         section_output_dir,
                                                         semaphore,
                                                         filename=video['title'])) for video in group_videos]
            for f in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc=f'Скачивание файлов {section}',
                          colour='green',
                          leave=True):
                await f
