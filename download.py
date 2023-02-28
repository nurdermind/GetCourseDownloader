import click

from get_cource_downloader.course import Course
from loguru import logger


@click.command()
@click.option('-u', '--url', help='Course url.', prompt=True, required=True)
@click.option('-c', '--cookie', help='cookie path.', required=True)
@click.option('-o', '--output-dir', help='Path to output dir for download video.')
@logger.catch
def cli(url, output_dir, cookie):
    course = Course(url=url, cookie_path=cookie)
    course.download(output_dir)


if __name__ == '__main__':
    cli()
