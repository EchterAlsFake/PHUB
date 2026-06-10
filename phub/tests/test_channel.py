import pytest
from phub import Client

@pytest.fixture
def client() -> Client:
    return Client()


@pytest.mark.asyncio
async def test_channel(client):
    channel = await client.get_channel("https://www.pornhub.com/channels/brazzers/")
    assert isinstance(channel.name, str) and len(channel.name) > 0
    assert isinstance(channel.description, str) and len(channel.description) > 0
    assert isinstance(channel.rank, int)
    assert isinstance(channel.join_date, str) and len(channel.join_date) > 0
    assert isinstance(channel.website, str) and len(channel.website) > 0
    assert isinstance(channel.is_award_winner, bool)
    assert isinstance(channel.subscribers, str) and len(channel.subscribers) > 0
    assert isinstance(channel.total_videos, str) and len(channel.total_videos) > 0
    assert isinstance(channel.video_views, str) and len(channel.video_views) > 0

    user = await channel.get_user()
    assert isinstance(user.about, str) and len(user.about) > 0