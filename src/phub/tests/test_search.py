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
print(f"Using config:; {client.core.config.request_delay}")

def test_basic_search():
    search = client.search("Mia Khalifa")  # for the nostalgia
    for idx, result in enumerate(search):
        assert isinstance(result.title, str) and len(result.title) >= 3

        if idx == 5:
            break


def test_basic_search_filters():
    search = client.search("Mia Khalifa", category="babe", exclude_category="bbw", hd=True, production="professional")
    for idx, result in enumerate(search):
        assert isinstance(result.title, str) and len(result.title) >= 3

        if idx == 5:
            break


def test_user_search():
    search = client.search_user("Mia", is_model=True, is_online=False)
    for idx, result in enumerate(search):
        assert isinstance(result.name, str) and len(result.name) >= 3

        if idx == 5:
            break

# EOF