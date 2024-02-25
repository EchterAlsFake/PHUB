try:
    from phub import Client
    from phub import literals

except (ModuleNotFoundError, ImportError):
    from ...phub import Client
    from ...phub import literals

client = Client(delay=2, language="en")


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
