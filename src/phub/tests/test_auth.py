import os

try:
    from phub import Client

except (ModuleNotFoundError, ImportError):
    from ...phub import Client

def test_auth():
    
    client = Client(
        email = os.getenv('EMAIL'),
        password = os.getenv('PASSWORD'),
        login = False
    )
    
    client.login()
    
    assert client.logged

# EOF
