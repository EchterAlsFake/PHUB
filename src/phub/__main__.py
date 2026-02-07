"""
PHUB built-in CLI.
"""
import os
import logging
import argparse

from phub import Client
from typing import Union
from base_api import BaseCore

def quality_type(s: str):
    # Small helper for argparse type hinting
    if s.isdigit():
        return int(s)
    return s  # e.g. "best", "half", "worst

downloaded: int = 0 # Keeps track of total downloaded videos
client: Client = Client() # For type hinting (don't ask)

map_log = {
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
    "CRITICAL": logging.CRITICAL,
}


def configure(args):
    core = BaseCore()
    core.enable_logging(level=map_log[args.log_level])
    core.config.proxy = args.proxy if args.proxy else None
    core.config.max_workers = args.max_workers if args.max_workers else 20
    core.initialize_session() # Start the session with our configuration

    global client
    client = Client(core=core)
    client.enable_logging(level=map_log[args.log_level])

def download_video(video, quality: Union[str, int], output: str, no_title: bool = False,
                   use_video_id: bool = False):

    global downloaded
    title = video.title

    if use_video_id:
        title = video.id

    if not no_title:
        output = os.path.join(output, title + ".mp4")


    print(f"Downloading to -->: {output}")
    report = video.download(quality=quality, path=output, no_title=no_title, return_report=True)
    downloaded += 1
    return report # Doesn't hurt, maybe someone uses this for batch processing idk



def main():
    parser = argparse.ArgumentParser(description="PHUB built-in CLI")
    group = parser.add_mutually_exclusive_group(required=True) # Makes sure only URL, or model, or a file can be given as an input
    group.add_argument("-url", type=str, help="a PornHub Video URL", default="")
    group.add_argument("-model", type=str, help="a Pornhub Model URL", default="")
    parser.add_argument("-video_limit", type=int, help="the maximum number of videos to download from a model (Default: all)", default=100000)
    parser.add_argument("--use-video-id", action="store_true", help="uses video ID as the title instead of the original video title")
    parser.add_argument("-quality", type=quality_type, help="The video quality", choices=[144, 240, 360, 480, 720, 1080, 1440, 2160, "best", "half", "worst"],
                      default="best")
    parser.add_argument("-no-title", help="Whether to automatically include the title in the output path or not", action="store_true", default=True)
    parser.add_argument("-max-workers", type=int, help="The maximum amount of concurrent threads that fetch segments", default=20)
    parser.add_argument("--proxy", type=str, help="A proxy in <protocol><ip><port> format")
    parser.add_argument("--log-level", type=str, help="The logging level (default: ERROR)", default="ERROR",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])

    parser.add_argument("-output", type=str, help="The output path", default="./")

    args = parser.parse_args()
    quality = args.quality
    output = args.output
    url = args.url
    model = args.model
    video_limit = args.video_limit
    use_video_id = args.use_video_id

    configure(args)

    if url:
        video = client.get(url)
        download_video(video, quality, output, no_title=args.no_title, use_video_id=use_video_id)

    elif model:
        model = client.get_user(model)
        print(f"Downloading model -->: {model.name}")

        for video in model.videos:
            if downloaded >= video_limit:
                return

            download_video(video, quality, output, no_title=args.no_title, use_video_id=use_video_id)

    print("Finished :)")


if __name__ == "__main__":
    main()