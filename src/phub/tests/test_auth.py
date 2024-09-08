import os

try:
    from phub import Client

except (ModuleNotFoundError, ImportError):
    from ...phub import Client

def test_auth():
    
    email = os.getenv('EMAIL')
    password = os.getenv('PASSWORD')
    
    assert email and password
    
    client = Client(email, password, login = False)
    client.login()
    
    assert client.logged

# EOF