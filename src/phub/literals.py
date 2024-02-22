'''
    Literals.
'''

from enum import Enum
from typing import Literal, Iterable


production = Literal['homemade', 'professional']
sort = Literal['recent', 'views', 'rated', 'longuest']
period = Literal['all', 'day', 'week', 'month', 'year']
section: Literal['all', 'post', 'photo', 'video', 'comment', 'favorite', 'playlist']

category = Literal[
    'asian', 'orgy', 'amateur', 'big-ass', 'babe', 'bbw', 'big-dick', 'big-tits', 'blonde', 'bondage',
    'brunette', 'celebrity', 'blowjob', 'bukkake', 'creampie', 'cumshot', 'ebony', 'fetish', 'fisting',
    'handjob', 'hardcore', 'masturbation', 'toys', 'public', 'interracial', 'latina', 'lesbian', 'mature',
    'milf', 'pornstar', 'reality', 'funny', 'striptease', 'anal', 'hentai', 'teen-18-1', 'hd-porn',
    'japanese-gay', 'bareback-gay', 'pov', 'red-head', 'vintage', 'black-gay', 'massage-gay', 'euro-gay',
    'daddy-gay', 'asian-gay', 'twink-18', 'latino-gay', 'muscle-gay', 'fetish-gay', 'party', 'solo-male-gay',
    'euro', 'blowjob-gay', 'compilation', 'big-dick-gay', 'small-tits', 'pornstar-gay', 'webcam', 'group-gay',
    'gay', 'interracial-gay', 'threesome', 'bear-gay', 'rough-sex', 'college-18', 'squirt', 'hunks-gay',
    'creampie-gay', 'double-penetration', 'popular-with-women', 'bisexual-male', 'vintage-gay', 'massage',
    'college-18-1', 'gangbang', 'role-play', 'straight-guys-gay', 'transgender', 'public-gay', 'reality-gay',
    'cartoon', 'school-18', 'babysitter-18', 'casting', 'smoking', 'solo-male', 'feet', 'french', 'german',
    'british', 'italian', 'arab', 'russian', 'czech', 'indian', 'brazilian', 'korean', 'vr', '60fps-1',
    'vr-gay', 'hd-porn-gay', 'interactive', 'japanese', 'exclusive', 'music', 'pussy-licking', 'ffm', 'fmm',
    'verified-amateurs', 'verified-models', 'behind-the-scenes', 'old-young-18', 'parody', 'pissing', 'sfw',
    'described-video', 'cosplay', 'cuckold', 'amateur-gay', 'handjob-gay', 'uncut-gay', 'rough-sex-gay',
    'jock-gay', 'mature-gay', 'webcam-gay', 'cumshot-gay', 'casting-gay', 'pov-gay', 'compilation-gay',
    'chubby-gay', 'military-gay', 'feet-gay', 'cartoon-gay', 'step-fantasy', 'verified-couples', 'solo-female',
    'female-orgasm', 'muscular-men', 'romantic', 'scissoring', 'strap-on', 'tattooed-men-gay', 'tattooed-women',
    'trans-with-girl', 'trans-with-guy', 'fingering', 'trans-male', '360-1', '180-1', '2d', '3d', 'voyeur',
    'pov-1', 'uncensored', 'uncensored-1', 'verified-amateurs-gay', 'closed-captions', 'closed-captions-gay'
]

_sort_map = {
    'recent': 'mr',
    'views': 'mv',
    'rated': 'tr',
    'longuest': 'lg'
}

_period_map = {
    'day': 't',
    'week': 'w',
    'month': 'm',
    'year': 'y'
}

_section_map = {
    'post': 'posts',
    'photo': 'albums',
    'video': 'videos',
    'comment': 'comments',
    'favorite': 'favourite',
    'playlist': 'playlists'
}

def _craft_category(args: Iterable[category]) -> str:
    '''
    Craft a category list into a url-valid list.
    '''
    
    if isinstance(args, str):
        return args
    
    if args:
        return '-'.join(args)

def _craft_boolean(b: bool | None) -> str:
    '''
    Craft a boolean into a url-valid int.
    '''
    
    if b is not None:
        return int(bool(b))

# EOF