'''
PHUB Literals.
'''

from typing import Literal, Iterable, Type, Union

# Language locales
language = Literal['en', 'cn', 'de', 'fr', 'it', 'pt', 'pl', 'rt', 'nl', 'cz', 'jp']

# Production type
production = Literal['homemade', 'professional']

# Sortings for videos
sort = Literal['recent', 'views', 'rated', 'longuest']
ht_sort = Literal['recent', 'views', 'rated', 'featured']

# Sortings for users
sort_user = Literal['popular', 'newest']

# Sorting period
period = Literal['all', 'day', 'week', 'month', 'year']
ht_period = Literal['all', 'week', 'month']

# Feed sections
section = Literal['all', 'post', 'photo', 'video', 'comment', 'favorite', 'playlist']

# Allowed genders
gender = Literal[
    'male', 'female', 'couple', 'female couple', 'trans female',
    'male couple', 'trans male', 'other', 'non binary'
]

# User sexual orientation
orientation = Literal['none', 'male', 'female', 'all']

# What content user offers 
offers = Literal['custom videos', 'fan club']

# User relationship
relation = Literal['single', 'taken', 'open']

# Video segment (orientation)
Segment = Literal['female', 'male', 'straight', 'gay', 'transgender', 'miscellaneous', 'uncategorized']

'''
For clarity, these categories where renamed:
teen18-1      -> teen
twink18       -> twink
college-18    -> college
school-18     -> school
babysitter-18 -> babysitter
60fps-1       -> 60fps
old-young-18  -> old-young
360-1         -> 360
180-1         -> 180
pov-1         -> pov
'''

# Video categories
category = Literal[
    'asian', 'orgy', 'amateur', 'big-ass', 'babe', 'bbw', 'big-dick', 'big-tits', 'blonde', 'bondage',
    'brunette', 'celebrity', 'blowjob', 'bukkake', 'creampie', 'cumshot', 'ebony', 'fetish', 'fisting',
    'handjob', 'hardcore', 'masturbation', 'toys', 'public', 'interracial', 'latina', 'lesbian', 'mature',
    'milf', 'pornstar', 'reality', 'funny', 'striptease', 'anal', 'hentai', 'teen', 'hd-porn',
    'japanese-gay', 'bareback-gay', 'pov', 'red-head', 'vintage', 'black-gay', 'massage-gay', 'euro-gay',
    'daddy-gay', 'asian-gay', 'twink', 'latino-gay', 'muscle-gay', 'fetish-gay', 'party', 'solo-male-gay',
    'euro', 'blowjob-gay', 'compilation', 'big-dick-gay', 'small-tits', 'pornstar-gay', 'webcam', 'group-gay',
    'gay', 'interracial-gay', 'threesome', 'bear-gay', 'rough-sex', 'college', 'squirt', 'hunks-gay',
    'creampie-gay', 'double-penetration', 'popular-with-women', 'bisexual-male', 'vintage-gay', 'massage',
    'gangbang', 'role-play', 'straight-guys-gay', 'transgender', 'public-gay', 'reality-gay',
    'cartoon', 'school', 'babysitter', 'casting', 'smoking', 'solo-male', 'feet', 'french', 'german',
    'british', 'italian', 'arab', 'russian', 'czech', 'indian', 'brazilian', 'korean', 'vr', '60fps',
    'vr-gay', 'hd-porn-gay', 'interactive', 'japanese', 'exclusive', 'music', 'pussy-licking', 'ffm', 'fmm',
    'verified-amateurs', 'verified-models', 'behind-the-scenes', 'old-young', 'parody', 'pissing', 'sfw',
    'described-video', 'cosplay', 'cuckold', 'amateur-gay', 'handjob-gay', 'uncut-gay', 'rough-sex-gay',
    'jock-gay', 'mature-gay', 'webcam-gay', 'cumshot-gay', 'casting-gay', 'pov-gay', 'compilation-gay',
    'chubby-gay', 'military-gay', 'feet-gay', 'cartoon-gay', 'step-fantasy', 'verified-couples', 'solo-female',
    'female-orgasm', 'muscular-men', 'romantic', 'scissoring', 'strap-on', 'tattooed-men-gay', 'tattooed-women',
    'trans-with-girl', 'trans-with-guy', 'fingering', 'trans-male', '360', '180', '2d', '3d', 'voyeur',
    'pov', 'uncensored', 'verified-amateurs-gay', 'closed-captions', 'closed-captions-gay'
]

class map:
    '''
    This object maps PHUB literals to their Pornhub URL value.
    '''

    sort = {
        'recent': 'mr',
        'views': 'mv',
        'rated': 'tr',
        'longuest': 'lg'
    }

    period = {
        'day': 't',
        'week': 'w',
        'month': 'm',
        'year': 'y'
    }

    section = {
        'post': 'posts',
        'photo': 'albums',
        'video': 'videos',
        'comment': 'comments',
        'favorite': 'favourite',
        'playlist': 'playlists'
}

    # NOTE - 'uncensored' can be 712 or 722
    category = {
        'asian':                 1, 'orgy':              2, 'amateur':             3, 'big-ass':            4, 'babe':                    5, 'bbw':                 6,
        'big-dick':              7, 'big-tits':          8, 'blonde':              9, 'bondage':           10, 'brunette':               11, 'celebrity':          12,
        'blowjob':              13, 'bukkake':          14, 'creampie':           15, 'cumshot':           16, 'ebony':                  17, 'fetish':             18,
        'fisting':              19, 'handjob':          20, 'hardcore':           21, 'masturbation':      22, 'toys':                   23, 'public':             24,
        'interracial':          25, 'latina':           26, 'lesbian':            27, 'mature':            28, 'milf':                   29, 'pornstar':           30,
        'reality':              31, 'funny':            32, 'striptease':         33, 'anal':              35, 'hentai':                 36, 'teen':               37,
        'hd-porn':              38, 'japanese-gay':     39, 'bareback-gay':       40, 'pov':               41, 'red-head':               42, 'vintage':            43,
        'black-gay':            44, 'massage-gay':      45, 'euro-gay':           46, 'daddy-gay':         47, 'asian-gay':              48, 'twink':              49,
        'latino-gay':           50, 'muscle-gay':       51, 'fetish-gay':         52, 'party':             53, 'solo-male-gay':          54, 'euro':               55,
        'blowjob-gay':          56, 'compilation':      57, 'big-dick-gay':       58, 'small-tits':        59, 'pornstar-gay':           60, 'webcam':             61,
        'group-gay':            62, 'gay':              63, 'interracial-gay':    64, 'threesome':         65, 'bear-gay':               66, 'rough-sex':          67,
        'college':              68, 'squirt':           69, 'hunks-gay':          70, 'creampie-gay':      71, 'double-penetration':     72, 'popular-with-women': 73,
        'bisexual-male':        76, 'vintage-gay':      77, 'massage':            78, 'college':           79, 'gangbang':               80, 'role-play':          81,
        'straight-guys-gay':    82, 'transgender':      83, 'public-gay':         84, 'reality-gay':       85, 'cartoon':                86, 'school':             88,
        'babysitter':           89, 'casting':          90, 'smoking':            91, 'solo-male':         92, 'feet':                   93, 'french':             94,
        'german':               95, 'british':          96, 'italian':            97, 'arab':              98, 'russian':                99, 'czech':             100,
        'indian':              101, 'brazilian':       102, 'korean':            103, 'vr':               104, '60fps':                 105, 'vr-gay':            106,
        'hd-porn-gay':         107, 'interactive':     108, 'japanese':          111, 'exclusive':        115, 'music':                 121, 'pussy-licking':     131,
        'verified-amateurs':   138, 'verified-models': 139, 'behind-the-scenes': 141, 'old-young-18':     181, 'parody':                201, 'pissing':           211,
        'sfw':                 221, 'described-video': 231, 'cosplay':           241, 'cuckold':          242, 'amateur-gay':           252, 'handjob-gay':       262,
        'uncut-gay':           272, 'rough-sex-gay':   312, 'jock-gay':          322, 'mature-gay':       332, 'webcam-gay':            342, 'cumshot-gay':       352,
        'casting-gay':         362, 'pov-gay':         372, 'compilation-gay':   382, 'chubby-gay':       392, 'military-gay':          402, 'feet-gay':          412,
        'cartoon-gay':         422, 'step-fantasy':    444, 'verified-couples':  482, 'solo-female':      492, 'female-orgasm':         502, 'muscular-men':      512,
        'romantic':            522, 'scissoring':      532, 'strap-on':          542, 'tattooed-men-gay': 552, 'tattooed-women':        562, 'trans-with-girl':   572,
        'trans-with-guy':      582, 'fingering':       592, 'trans-male':        602, '360':              612, '180':                   622, '2d':                632,
        '3d':                  642, 'voyeur':          682, 'pov':               702, 'uncensored':       712, 'verified-amateurs-gay': 731, 'closed-captions':   732,
        'closed-captions-gay': 742, 'ffm':             761, 'fmm':               771
    }

    gender = {
        'male': 1,
        'female': 2,
        'couple': 3,
        'trans female': 5,
        'female couple': 6,
        'male couple': 7,
        'trans male': 9,
        'other': 10,
        'non binary': 11
    }

    orientation = {
        'none': 0,
        'male': 1,
        'female': 2,
        'all': 3
    }
    
    offers = {
        'custom videos': 'customvideo',
        'fan club': 'fanclub'
    }
    
    relation = {
        'single': 1,
        'taken': 2,
        'open': 3
    }
    
    # Hubtraffic maps
    ht_sort = {
        'recent': 'newest',
        'views': 'mostviewed',
        'rated': 'rating',
    }
    
    ht_period = {
        'all': 'alltime',
        'week': 'weekly',
        'month': 'monthly'
    }

def _craft_list(args: Iterable[str]) -> str:
    '''
    Craft an item list list into a url-valid list.
    
    Args:
        args (Iterable[str]): A list of items.
    
    Returns:
        str: A dash separated URL-valid list. 
    '''
    
    if isinstance(args, str):
        return args
    
    if args:
        return '-'.join(list(args))

def _craft_boolean(b: Union[bool, None]) -> Union[int, None]:
    '''
    Craft a boolean into a url-valid int.
    
    Args:
        b (bool): Initial boolean value.
    
    Returns:
        int: URL-valid representation of b.
    '''
    
    if b is not None:
        return int(bool(b))

def ass(name: str, item: Union[str, list[str]], literal: Type) -> None:
    '''
    Assert one or multiple items are part of a literal.
    
    Args:
        name (str): The literal name, used for error bodies.
        item (str | list[str]): The object(s) to assert.
        literal (Type): The literal that should match the item(s).
    
    Raises:
        AssertionError: If the item is invalid.
    '''
    
    if not item: return
    
    if isinstance(item, str):
        item = [item]
    
    items = literal.__args__
    
    if len(items) > 5:
        message = ', '.join(items[:5]) + f' [+{abs(len(items) - 5)}]'
    else:
        message = ', '.join(items)
    
    for item_ in item:
        assert item_ in items, f'Argument `{name}` must be one of: `{message}`'

# EOF