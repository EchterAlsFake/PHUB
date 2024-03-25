try:
    from phub import Client
except (ModuleNotFoundError, ImportError):
    from ...phub import Client
url = 'https://de.pornhub.com/pornstar/nancy-a'
client = Client(delay=2, language='en')
model = client.get_user(url)


def test_info():
    assert isinstance(model.info, dict)


def test_avatar():
    assert isinstance(model.avatar.url, str) and len(model.avatar.url) > 5


def test_bio():
    assert isinstance(model.bio, str) and len(model.bio) > 1


def test_uploads():
    uploads = model.uploads
    total_uploads = []
    try:
        for video in uploads:
            total_uploads.append(video)
    except Exception:
        pass
    if len(total_uploads) >= 1:
        for upload in model.uploads:
            assert isinstance(upload.title, str) and len(upload.title) > 3
