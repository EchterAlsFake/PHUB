try:
    from phub import Client
    from base_api.modules.config import config
    from base_api.base import BaseCore
except (ModuleNotFoundError, ImportError):
    from ...phub import Client

config.request_delay = 0
core = BaseCore(config=config)
client = Client(language="en", core=core)
url = "https://de.pornhub.com/view_video.php?viewkey=ph60f99fa4b5cd7"
video = client.get(url)


def test_video_information():
    title = video.title
    likes = video.likes.up
    dislikes = video.likes.down
    views = video.views
    categories = video.categories
    tags = video.tags
    duration = video.duration
    embed = video.embed
    image = video.image.url
    id = video.id
    assert isinstance(title, str) and len(title) > 3
    assert isinstance(likes, int) and len(str(likes)) >= 1
    assert isinstance(dislikes, int) and len(str(dislikes)) >= 1
    assert isinstance(views, int) and len(str(views)) >= 1
    assert isinstance(categories, list) and len(categories) >= 1
    assert isinstance(tags, list) and len(tags) >= 1
    assert isinstance(duration.seconds, int) and len(str(duration)) >= 3
    assert isinstance(embed, str) and len(embed) >= 3
    assert isinstance(image, str) and len(image) >= 3
    assert isinstance(id, (str, int))

def test_download():
    stuff = video.download(quality="best", return_report=True)
    assert stuff["status"] == "completed"


