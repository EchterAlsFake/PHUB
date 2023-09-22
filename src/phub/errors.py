'''
PHUB 4 errors types.
'''

class ClientAlreadyLogged(Exception):
    '''
    The Client already has initiated
    a login call which was successfull.
    '''

class LoginFailed(Exception):
    '''
    The Client failed to connect.
    Given credentials might be wrong.
    '''

class RegexError(Exception):
    '''
    A regex failed to execute.
    '''

class URLError(Exception):
    '''
    Provided URL is invalid.
    '''

class ParsingError(Exception):
    '''
    The parser failed to properly
    fetch data.
    '''

class MaxRetriesExceeded(Exception):
    '''
    A module failed its job after too
    many retries. You might want to
    try again after a few time.
    
    You can also use :attr:`Client.delay`
    to slow down requests.
    '''

class UserNotFound(Exception):
    '''
    User wasn't found. This either happens
    because the user does not exists, or
    it's name or URL is wrong.
    '''

class NoResult(Exception):
    '''
    A query failed to retrieve an item
    at a specific index. Most of the time,
    this is raised when you go too far in
    a fetching loop:
    
    .. code-block:: python
        query = ...
        for i in range(1000):
            print(query[i])
    
    Instead, use:
    
    .. code-block:: python
        query = ...
        for item in query[:1000]:
            print(item)
    
    '''

class InvalidCategory(Exception):
    '''
    The category is invalid. This happens
    while trying to make Temporary
    categories behave like normal categories.
    This can usually be fixed by updating
    PHUB constants:
    
    .. code-block:: bash
        python -m phub update_locals
    
    '''

# EOF