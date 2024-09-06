import os

try:
    from phub import Client

except (ModuleNotFoundError, ImportError):
    from ...phub import Client

def test_auth():
    
    client = Client(
        email = os.getenv('EMAIL'),
        password = os.getenv('PASSWORD')
    )
    
    assert client.account

# EOF
