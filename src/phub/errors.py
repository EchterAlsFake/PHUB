'''
Errors for the PHUB package.
'''


class CounterNotFound(Exception):
    '''
    The video counter wasn't found in the query,
    or is badly parsed.
    '''

class ParsingError(Exception):
    '''
    The parser failed to properly resolve the script
    for this element.
    '''

class UserNotFoundError(Exception):
    '''
    Failed to find a PH user account.
    '''

class NotLoggedIn(Exception):
    '''
    The client is not logged to a PH account,
    but tried to access account data.
    '''

class AlreadyLoggedIn(Exception):
    '''
    The client already established a connection with PH.
    '''

class LogginFailed(Exception):
    '''
    Login phase failed. Credentials may be wrong.
    '''

class TooManyRequests(Exception):
    '''
    The client sent too many requests.
    To bypass, consider using proxies or
    set a small delay to the client request:
    
    .. code-block:: python
    
        client = phub.Client(delay = True)
    '''

class Noresult(Exception):
    '''
    The search query did not found videos with
    its given filters.
    '''

# EOF