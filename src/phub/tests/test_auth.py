import os

try:
    from phub import Client

except (ModuleNotFoundError, ImportError):
    from ...phub import Client

client = Client(
    email = os.getenv('EMAIL'),
    password = os.getenv('PASSWORD'),
    login = False
)

def test_auth():
    
    # client.login()
    
    # assert client.account
    
    pass


# EOF