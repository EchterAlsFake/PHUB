import phub
from phub.modules import downloader

client = phub.Client()

video = client.get('')

video.download('.', 'best', backend = downloader.FFMPEG)