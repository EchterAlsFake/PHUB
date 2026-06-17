import pytest
from phub import Client

@pytest.fixture
def client():
    return Client()


@pytest.mark.asyncio
async def test_gif_from_search(client):

    idx = 0
    async for gif in client.search_gifs("fortnite"):
        idx += 1
        assert await gif._ensure_html()
        assert isinstance(gif.title, str) and len(gif.title) > 0
        assert isinstance(gif.thumbnail, str) and len(gif.thumbnail) > 0
        assert isinstance(gif.publish_date, str) and len(gif.publish_date) > 0
        assert isinstance(gif.content_url, str) and len(gif.content_url) > 0
        assert isinstance(gif.tags, dict) and len(gif.tags) > 0
        assert isinstance(gif.vote_count, int)
        assert isinstance(gif.vote_percentage, str)

        if idx >= 5:
            break

@pytest.mark.asyncio
async def test_search(client):
    idx = 0
    async for video in client.search_videos("fortnite"):
        idx += 1
        assert isinstance(video.title, str) and len(video.title) > 0
        assert isinstance(video.duration, int)
        
        # Verify that HTML was NOT fetched during search
        assert video.html_content is None

        if idx == 5:
            break
