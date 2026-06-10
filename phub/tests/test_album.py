import pytest
import random

from phub import Client, Pornstar

@pytest.fixture
def client() -> Client:
    return Client()

@pytest.mark.asyncio
async def test_album(client):
    album = await client.get_album("https://www.pornhub.com/album/80426065")
    assert isinstance(await album.author, Pornstar)
    assert isinstance(album.publish_date, str) and len(album.publish_date) > 0
    assert isinstance(album.rating_percentage, str) and len(album.rating_percentage) > 0
    assert isinstance(album.tags, dict)
    assert isinstance(album.views, str) and len(album.views) > 0
    assert isinstance(album.votes, str) and len(album.votes) > 0


    idx = 0
    async for photo in album.get_photos(pages=1):
        idx += 1
        assert isinstance(photo, dict)
        assert isinstance(photo.get("url"), str)
        assert isinstance(photo.get("views"), str)
        assert isinstance(photo.get("rating"), str)

        url = photo.get("download_url")
        assert await album.download_photo(url=url, path=f"./{random.randint(0, 1000)}.jpg") is True

        if idx >= 5:
            break


