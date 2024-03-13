try:
    from phub import Client

except (ImportError, ModuleNotFoundError):
    from ...phub import Client

url = "https://de.pornhub.com/playlist/113348141"
client = Client(delay=2, language="en")
playlist = client.get_playlist(url)


def test_videos():
    videos = playlist.videos

    for idx, video in enumerate(videos):
        assert isinstance(video.title, str) and len(video.title) > 3

        if idx == 37:  # Testing 37 videos, because one page contains 36, and I want to make sure page iteration works
            break


def test_playlist_objects():
    likes = playlist.likes
    dislikes = playlist.dislikes
    rating = playlist.like_ratio
    views = playlist.views
    total_videos = playlist.total_video_amount
    unavailable_videos = playlist.hidden_videos_amount
    author = playlist.author
    title = playlist.title
    tags = playlist.tags

    assert isinstance(likes, str) and int(likes) in range(0, 10000)  # More likes would be a bit weird in every scenario
    assert isinstance(dislikes, str) and int(dislikes) in range(0, 10000)
    assert isinstance(rating, str) and int(rating) in range(0, 100)  # Ratings are in percent, so can only be between 0 and 100
    assert isinstance(views, str) and len(views) >= 1
    assert isinstance(total_videos, str) and len(total_videos) >= 1
    assert isinstance(unavailable_videos, str) and len(unavailable_videos) >= 1
    assert isinstance(author, str) and len(author) >= 1
    assert isinstance(title, str) and len(title) >= 1
    assert isinstance(tags, list) # and len(tags) >= 1
