import pytest

from phub import Client

@pytest.fixture
def client():
    return Client()

@pytest.mark.asyncio
async def test_video(client):
    client = Client()
    # By default this uses HubTraffic API
    video = await client.get_video("https://www.pornhub.com/view_video.php?viewkey=ph61d5d646249b2")

    # These should be available via API data without HTML
    assert isinstance(video.title, str) and len(video.title) > 3
    assert isinstance(video.views, str) and len(video.views) > 1
    assert isinstance(video.publish_date, str) and len(video.publish_date) > 1
    assert isinstance(video.duration, int)
    assert isinstance(video.likes, str)
    assert isinstance(video.thumbnail, str)
    
    # HTML shouldn't be fetched yet
    assert video.html_content is None
    
    # Now fetch HTML for deep scraping
    await video.ensure_html()
    assert video.html_content is not None

    assert isinstance(video.flashvars, dict)
    assert isinstance(video.available_qualities, list) and len(video.available_qualities) > 0
    assert isinstance(video.is_vertical, bool)
    assert isinstance(video.is_video_unavailable, bool)
    assert isinstance(video.is_vr, bool)
    assert isinstance(video.is_hd, bool)
    assert isinstance(video.author_thumbnail, str) and len(video.author_thumbnail) > 0
    # After HTML fetch, these might be dicts if from scrape or list if from API
    assert isinstance(video.categories, (dict, list))
    assert isinstance(video.tags, (dict, list))
    assert isinstance(video.get_m3u8_urls, dict)
    assert isinstance(video.m3u8_base_url, str)
    assert isinstance(video.is_video_unavailable_in_your_country, bool)

    stuff = await video.download(quality="best", return_report=True)
    assert stuff["status"] == "completed"