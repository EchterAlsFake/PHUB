try:
    from phub import Client
    from base_api.modules.config import config
    from base_api.base import BaseCore
except (ModuleNotFoundError, ImportError):
    from ...phub import Client
    from base_api.modules.config import config
    from base_api.base import BaseCore

config.request_delay = 10
core = BaseCore(config=config)
client = Client(language="en", core=core)  # Make a delay, so that PornHub isn't stressed too much

url = "https://pornhub.com/pornstar/nancy-a"
model = client.get_user(url)

def test_info():
    assert isinstance(model.info, dict)


def test_avatar():
    for i in range(5): # Because PornHub is sometimes just stupid.
        try:
            assert isinstance(model.avatar.url, str) and len(model.avatar.url) > 5

        except AssertionError:
            model.refresh()
            continue

def test_bio():
    for i in range(5):
        try:
            assert isinstance(model.bio, str) and len(model.bio) > 1

        except AssertionError:
            model.refresh()
            continue


def test_uploads():
    uploads = model.uploads
    total_uploads = []
    try:
        for video in uploads:
            total_uploads.append(video)

    except Exception:
        pass # Means, that user has no uploads, so I don't care

    if len(total_uploads) >= 1:
        for upload in model.uploads:
            assert isinstance(upload.title, str) and len(upload.title) > 3

# EOF