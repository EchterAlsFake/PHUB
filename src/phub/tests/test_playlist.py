try:
    from phub import Client, Like, User
    from base_api.modules.config import config
    from base_api.base import BaseCore
except (ModuleNotFoundError, ImportError):
    from ...phub import Client, Like, User
    from base_api.modules.config import config
    from base_api.base import BaseCore

url = "https://de.pornhub.com/playlist/113348141"
client = Client(language="en")
playlist = client.get_playlist(url)


def test_videos():
    
    for idx, video in enumerate(playlist):
        assert isinstance(video.title, str) and len(video.title) > 3

        if idx == 37:  # Testing 37 videos, because one page contains 36, and I want to make sure page iteration works
            break


def test_playlist_objects():

    assert isinstance(playlist.like, Like)
    assert isinstance(playlist.views, int)
    assert isinstance(len(playlist), int)
    assert isinstance(playlist.hidden_videos_amount, int)
    assert isinstance(playlist.author, User)
    assert isinstance(playlist.title, str) and len(playlist.title) >= 1
    assert isinstance(playlist.tags, list)

# EOF