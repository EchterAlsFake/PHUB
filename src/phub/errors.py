'''
PHUB 4 errors types.
'''

class ClientAlreadyLogged(Exception):
    '''
    The Client already has initiated
    a login call that was successfull.
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
    many retries.
    '''

class UserNotFound(Exception):
    '''
    User wasn't found.
    '''