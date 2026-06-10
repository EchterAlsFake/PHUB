import pytest
from phub import Client

@pytest.fixture
def client():
    return Client()

@pytest.mark.asyncio
async def test_gif(client):
    gif = await client.get_gif("https://www.pornhub.com/gif/54402301")
    assert isinstance(gif.title, str) and len(gif.title) > 0
    assert isinstance(gif.thumbnail, str) and len(gif.thumbnail) > 0
    assert isinstance(gif.publish_date, str) and len(gif.publish_date) > 0
    assert isinstance(gif.content_url, str) and len(gif.content_url) > 0
    assert isinstance(gif.tags, dict) and len(gif.tags) > 0
    assert isinstance(gif.vote_count, int)
    assert isinstance(gif.vote_percentage, str)
    assert await gif.download() is True
