'''
PHUB errors types.
'''

class ClientAlreadyLogged(Exception):
    '''
    The Client is already logged in.
    '''

class LoginFailed(Exception):
    '''
    The Client failed to connect.
    Input credentials might be wrong.
    '''

class RegexError(Exception):
    '''
    A regex failed to execute.
    '''

class URLError(Exception):
    '''
    The provided URL is invalid.
    '''

class ParsingError(Exception):
    '''
    The parser failed to properly fetch data.
    '''

class MaxRetriesExceeded(Exception):
    '''
    A process failed after too many retries.
    
    Note: You can use: attr:`Client.delay` to slow down requests.
    '''

class UserNotFound(Exception):
    '''
    User could not be found either because
    it does not exists, or its name/URL is wrong.
    '''

class NoResult(Exception):
    '''
    A query failed to retrieve an item
    at a specific index. Most of the time,
    this is the equivalent of a StopIteration signal.
    '''

class InvalidCategory(Exception):
    '''
    The category is invalid.
    '''

class VideoError(Exception):
    '''
    Pornhub refused to serve video data because
    of some internal error (mostly because the video
    is not available).
    '''

class RegionBlocked(Exception):
    """
    Sometimes videos can be blocked in your region.
    In this case PHUB can't fetch data.

    Note: This could also be a private video. You only see this Information if you are logged in.
    This is a problem of PornHub itself and not related to PHUb!
    """

class PremiumVideo(Exception):
    """
    Raises when a video is a PornHub premium video.
    """
# EOF