"""
PHUB built-in CLI.
"""

import os
import argparse
import re

from phub import Client, Video
from phub.modules.download import threaded, FFMPEG, default


def text_progress_bar(downloaded, total, title=False):
    """Thanks, ChatGPT, I still suck at math <3"""
    bar_length = 50
    filled_length = int(round(bar_length * downloaded / float(total)))
    percents = round(100.0 * downloaded / float(total), 1)
    bar = '#' * filled_length + '-' * (bar_length - filled_length)
    if title is False:
        print(f"\r[{bar}] {percents}%", end='')

    else:
        print(f"\r | {title} | -->: [{bar}] {percents}%", end='')


def download_video(client: Client, url: [str, Video], channel:str, output: str, quality: str, downloader: str):
    if not isinstance(url, Video):
        video = client.get(url)


    elif isinstance(url, Video):
        video = url

    else:
        raise "Some error happened here, please report on GitHub, thank you :) "

    origtitle = video.title
    title =  re.sub(r'[<>:"/\\|?*]', '', video.title)
    if channel: channel+=" - "
    final_output_path = os.path.join(output, channel + title + " - pornhub.mp4")

    print(f"Downloading: {title} to: {final_output_path}")
    video.download(path=final_output_path, quality=quality, downloader=downloader, display=text_progress_bar)
    print(f"Successfully downloaded: {title}")

def resolve_threading_mode(mode, workers=10, timeout=10):
    """Resolve the appropriate threading mode based on input."""
    return {
        "threaded": threaded(max_workers=workers, timeout=timeout),
        "ffmpeg": FFMPEG,
        "default": default
    }.get(mode, default)


def main():
    parser = argparse.ArgumentParser(description="PHUB built-in CLI")
    group = parser.add_mutually_exclusive_group(required=True) # Makes sure only URL, or model, or a file can be given as an input
    group.add_argument("-url", type=str, help="a PornHub Video URL", default="")
    group.add_argument("-model", type=str, help="a Pornhub Model URL", default="")
    parser.add_argument("-video_limit", type=int, help="the maximum number of videos to download from a model (Default: all)", default=100000)
    group.add_argument("-file", type=str, help="List to a file with Video URLs (separated by new lines)", default="")
    parser.add_argument("-downloader", type=str, help="The threading (download backend) to use", choices=[
        "threaded", "default", "ffmpeg"], default="threaded")

    parser.add_argument("-quality", type=str, help="The video quality", choices=["best", "half", "worst"],
                      default="best")

    parser.add_argument("-output", type=str, help="The output path", default="./")
    parser.add_argument("-channel", type=str, help="Name of Pornhub channel", default="")

    args = parser.parse_args()
    quality = args.quality
    output = args.output
    channel = args.channel
    downloader = resolve_threading_mode(mode=args.downloader)
    url = args.url
    model = args.model
    video_limit = args.video_limit
    file = args.file

    client = Client()

    if len(url) >= 3:  # Comparison with not == "" doesn't work, don't ask me why I have no fucking idea...
        download_video(client=client, url=url, channel=channel, output=output, quality=quality, downloader=downloader)

    elif len(model) >= 3:
        model_videos = client.get_user(model).videos
        idx = 0

        for video in model_videos:
            if idx >= video_limit:
                break

            download_video(client=client, url=video, output=output, quality=quality, downloader=downloader)
            idx += 1

    elif len(file) >= 1:
        try:
            with open(file, "r") as f:
                urls = f.read().splitlines()

        except PermissionError:
            raise "You do not have the necessary permissions to read the file!"

        except FileNotFoundError:
            raise f"The file does not exist at your given location: {file}"


        for idx, url in enumerate(urls, start=1):
            print(f"[{idx}|{len(urls)}] Downloading: {url}")
            download_video(client=client, url=url, output=output, quality=quality, downloader=downloader)


if __name__ == '__main__':
    main()

# EOF
