try:
    import os
    from phub import Client
    from base_api.modules.config import config
    from base_api.base import BaseCore

except (ModuleNotFoundError, ImportError):
    import os
    from ...phub import Client
    from base_api.modules.config import config
    from base_api.base import BaseCore

def test_auth():
    
    email = os.getenv('EMAIL')
    password = os.getenv('PASSWORD')
    
    assert email and password

    config.request_delay = 0
    core = BaseCore(config=config)
    client = Client(language="en", core=core, email=email, password=password)

    assert client.logged

# EOF