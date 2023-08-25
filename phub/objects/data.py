from typing import Self, Literal
from dataclasses import dataclass, field

from .. import utils

@dataclass
class Tag:
    name: str
    count: int = field(default = None, repr = False)
    
@dataclass
class Like:
    up: int
    down: int
    
    ratings: float = field(repr = False)


class _BaseCategory:
    '''
    Represents a category.
    '''
    
    def __init__(self, id: str | int, name: str) -> None:
        '''
        Initialise a new category object.
        '''
        
        self.name = name
        self.id = id
    
    def __repr__(self) -> str:
        
        return f'phub.Category({self.name})'
    
    def __str__(self) -> str:
        
        return self.id
    
    def __or__(self, __value: Self) -> Self:
        '''
        Concatenate 2 categories.
        '''
        
        if not isinstance(__value, Category):
            raise TypeError('value must be category.')
        
        return Category(f'{self.id}-{__value.id}',
                        f'{self.name} & {__value.name}')
    
    def __eq__(self, __value: Self) -> bool:
        '''
        Compare 2 objects.
        '''
        
        if not isinstance(__value, Category):
            raise TypeError('value must be category.')
        
        return self.id == __value.id

class Category(_BaseCategory):
    '''
    Represents a category.
    '''
    
    #@START-CATEGORY
    ASIAN                 = _BaseCategory(   1, 'asian                ' )
    ORGY                  = _BaseCategory(   2, 'orgy                 ' )
    AMATEUR               = _BaseCategory(   3, 'amateur              ' )
    BIG_ASS               = _BaseCategory(   4, 'big-ass              ' )
    BABE                  = _BaseCategory(   5, 'babe                 ' )
    BBW                   = _BaseCategory(   6, 'bbw                  ' )
    BIG_DICK              = _BaseCategory(   7, 'big-dick             ' )
    BIG_TITS              = _BaseCategory(   8, 'big-tits             ' )
    BLONDE                = _BaseCategory(   9, 'blonde               ' )
    BONDAGE               = _BaseCategory(  10, 'bondage              ' )
    BRUNETTE              = _BaseCategory(  11, 'brunette             ' )
    CELEBRITY             = _BaseCategory(  12, 'celebrity            ' )
    BLOWJOB               = _BaseCategory(  13, 'blowjob              ' )
    BUKKAKE               = _BaseCategory(  14, 'bukkake              ' )
    CREAMPIE              = _BaseCategory(  15, 'creampie             ' )
    CUMSHOT               = _BaseCategory(  16, 'cumshot              ' )
    EBONY                 = _BaseCategory(  17, 'ebony                ' )
    FETISH                = _BaseCategory(  18, 'fetish               ' )
    FISTING               = _BaseCategory(  19, 'fisting              ' )
    HANDJOB               = _BaseCategory(  20, 'handjob              ' )
    HARDCORE              = _BaseCategory(  21, 'hardcore             ' )
    MASTURBATION          = _BaseCategory(  22, 'masturbation         ' )
    TOYS                  = _BaseCategory(  23, 'toys                 ' )
    PUBLIC                = _BaseCategory(  24, 'public               ' )
    INTERRACIAL           = _BaseCategory(  25, 'interracial          ' )
    LATINA                = _BaseCategory(  26, 'latina               ' )
    LESBIAN               = _BaseCategory(  27, 'lesbian              ' )
    MATURE                = _BaseCategory(  28, 'mature               ' )
    MILF                  = _BaseCategory(  29, 'milf                 ' )
    PORNSTAR              = _BaseCategory(  30, 'pornstar             ' )
    REALITY               = _BaseCategory(  31, 'reality              ' )
    FUNNY                 = _BaseCategory(  32, 'funny                ' )
    STRIPTEASE            = _BaseCategory(  33, 'striptease           ' )
    ANAL                  = _BaseCategory(  35, 'anal                 ' )
    HENTAI                = _BaseCategory(  36, 'hentai               ' )
    TEEN_18_1             = _BaseCategory(  37, 'teen-18-1            ' )
    HD_PORN               = _BaseCategory(  38, 'hd-porn              ' )
    JAPANESE_GAY          = _BaseCategory(  39, 'japanese-gay         ' )
    BAREBACK_GAY          = _BaseCategory(  40, 'bareback-gay         ' )
    POV                   = _BaseCategory(  41, 'pov                  ' )
    RED_HEAD              = _BaseCategory(  42, 'red-head             ' )
    VINTAGE               = _BaseCategory(  43, 'vintage              ' )
    BLACK_GAY             = _BaseCategory(  44, 'black-gay            ' )
    MASSAGE_GAY           = _BaseCategory(  45, 'massage-gay          ' )
    EURO_GAY              = _BaseCategory(  46, 'euro-gay             ' )
    DADDY_GAY             = _BaseCategory(  47, 'daddy-gay            ' )
    ASIAN_GAY             = _BaseCategory(  48, 'asian-gay            ' )
    TWINK_18              = _BaseCategory(  49, 'twink-18             ' )
    LATINO_GAY            = _BaseCategory(  50, 'latino-gay           ' )
    MUSCLE_GAY            = _BaseCategory(  51, 'muscle-gay           ' )
    FETISH_GAY            = _BaseCategory(  52, 'fetish-gay           ' )
    PARTY                 = _BaseCategory(  53, 'party                ' )
    SOLO_MALE_GAY         = _BaseCategory(  54, 'solo-male-gay        ' )
    EURO                  = _BaseCategory(  55, 'euro                 ' )
    BLOWJOB_GAY           = _BaseCategory(  56, 'blowjob-gay          ' )
    COMPILATION           = _BaseCategory(  57, 'compilation          ' )
    BIG_DICK_GAY          = _BaseCategory(  58, 'big-dick-gay         ' )
    SMALL_TITS            = _BaseCategory(  59, 'small-tits           ' )
    PORNSTAR_GAY          = _BaseCategory(  60, 'pornstar-gay         ' )
    WEBCAM                = _BaseCategory(  61, 'webcam               ' )
    GROUP_GAY             = _BaseCategory(  62, 'group-gay            ' )
    GAY                   = _BaseCategory(  63, 'gay                  ' )
    INTERRACIAL_GAY       = _BaseCategory(  64, 'interracial-gay      ' )
    THREESOME             = _BaseCategory(  65, 'threesome            ' )
    BEAR_GAY              = _BaseCategory(  66, 'bear-gay             ' )
    ROUGH_SEX             = _BaseCategory(  67, 'rough-sex            ' )
    COLLEGE_18            = _BaseCategory(  68, 'college-18           ' )
    SQUIRT                = _BaseCategory(  69, 'squirt               ' )
    HUNKS_GAY             = _BaseCategory(  70, 'hunks-gay            ' )
    CREAMPIE_GAY          = _BaseCategory(  71, 'creampie-gay         ' )
    DOUBLE_PENETRATION    = _BaseCategory(  72, 'double-penetration   ' )
    POPULAR_WITH_WOMEN    = _BaseCategory(  73, 'popular-with-women   ' )
    BISEXUAL_MALE         = _BaseCategory(  76, 'bisexual-male        ' )
    VINTAGE_GAY           = _BaseCategory(  77, 'vintage-gay          ' )
    MASSAGE               = _BaseCategory(  78, 'massage              ' )
    COLLEGE_18_1          = _BaseCategory(  79, 'college-18-1         ' )
    GANGBANG              = _BaseCategory(  80, 'gangbang             ' )
    ROLE_PLAY             = _BaseCategory(  81, 'role-play            ' )
    STRAIGHT_GUYS_GAY     = _BaseCategory(  82, 'straight-guys-gay    ' )
    TRANSGENDER           = _BaseCategory(  83, 'transgender          ' )
    PUBLIC_GAY            = _BaseCategory(  84, 'public-gay           ' )
    REALITY_GAY           = _BaseCategory(  85, 'reality-gay          ' )
    CARTOON               = _BaseCategory(  86, 'cartoon              ' )
    SCHOOL_18             = _BaseCategory(  88, 'school-18            ' )
    BABYSITTER_18         = _BaseCategory(  89, 'babysitter-18        ' )
    CASTING               = _BaseCategory(  90, 'casting              ' )
    SMOKING               = _BaseCategory(  91, 'smoking              ' )
    SOLO_MALE             = _BaseCategory(  92, 'solo-male            ' )
    FEET                  = _BaseCategory(  93, 'feet                 ' )
    FRENCH                = _BaseCategory(  94, 'french               ' )
    GERMAN                = _BaseCategory(  95, 'german               ' )
    BRITISH               = _BaseCategory(  96, 'british              ' )
    ITALIAN               = _BaseCategory(  97, 'italian              ' )
    ARAB                  = _BaseCategory(  98, 'arab                 ' )
    RUSSIAN               = _BaseCategory(  99, 'russian              ' )
    CZECH                 = _BaseCategory( 100, 'czech                ' )
    INDIAN                = _BaseCategory( 101, 'indian               ' )
    BRAZILIAN             = _BaseCategory( 102, 'brazilian            ' )
    KOREAN                = _BaseCategory( 103, 'korean               ' )
    VR                    = _BaseCategory( 104, 'vr                   ' )
    _60FPS_1              = _BaseCategory( 105, '60fps-1              ' )
    VR_GAY                = _BaseCategory( 106, 'vr-gay               ' )
    HD_PORN_GAY           = _BaseCategory( 107, 'hd-porn-gay          ' )
    INTERACTIVE           = _BaseCategory( 108, 'interactive          ' )
    JAPANESE              = _BaseCategory( 111, 'japanese             ' )
    EXCLUSIVE             = _BaseCategory( 115, 'exclusive            ' )
    MUSIC                 = _BaseCategory( 121, 'music                ' )
    PUSSY_LICKING         = _BaseCategory( 131, 'pussy-licking        ' )
    VERIFIED_AMATEURS     = _BaseCategory( 138, 'verified-amateurs    ' )
    VERIFIED_MODELS       = _BaseCategory( 139, 'verified-models      ' )
    BEHIND_THE_SCENES     = _BaseCategory( 141, 'behind-the-scenes    ' )
    OLD_YOUNG_18          = _BaseCategory( 181, 'old-young-18         ' )
    PARODY                = _BaseCategory( 201, 'parody               ' )
    PISSING               = _BaseCategory( 211, 'pissing              ' )
    SFW                   = _BaseCategory( 221, 'sfw                  ' )
    DESCRIBED_VIDEO       = _BaseCategory( 231, 'described-video      ' )
    COSPLAY               = _BaseCategory( 241, 'cosplay              ' )
    CUCKOLD               = _BaseCategory( 242, 'cuckold              ' )
    AMATEUR_GAY           = _BaseCategory( 252, 'amateur-gay          ' )
    HANDJOB_GAY           = _BaseCategory( 262, 'handjob-gay          ' )
    UNCUT_GAY             = _BaseCategory( 272, 'uncut-gay            ' )
    ROUGH_SEX_GAY         = _BaseCategory( 312, 'rough-sex-gay        ' )
    JOCK_GAY              = _BaseCategory( 322, 'jock-gay             ' )
    MATURE_GAY            = _BaseCategory( 332, 'mature-gay           ' )
    WEBCAM_GAY            = _BaseCategory( 342, 'webcam-gay           ' )
    CUMSHOT_GAY           = _BaseCategory( 352, 'cumshot-gay          ' )
    CASTING_GAY           = _BaseCategory( 362, 'casting-gay          ' )
    POV_GAY               = _BaseCategory( 372, 'pov-gay              ' )
    COMPILATION_GAY       = _BaseCategory( 382, 'compilation-gay      ' )
    CHUBBY_GAY            = _BaseCategory( 392, 'chubby-gay           ' )
    MILITARY_GAY          = _BaseCategory( 402, 'military-gay         ' )
    FEET_GAY              = _BaseCategory( 412, 'feet-gay             ' )
    CARTOON_GAY           = _BaseCategory( 422, 'cartoon-gay          ' )
    STEP_FANTASY          = _BaseCategory( 444, 'step-fantasy         ' )
    VERIFIED_COUPLES      = _BaseCategory( 482, 'verified-couples     ' )
    SOLO_FEMALE           = _BaseCategory( 492, 'solo-female          ' )
    FEMALE_ORGASM         = _BaseCategory( 502, 'female-orgasm        ' )
    MUSCULAR_MEN          = _BaseCategory( 512, 'muscular-men         ' )
    ROMANTIC              = _BaseCategory( 522, 'romantic             ' )
    SCISSORING            = _BaseCategory( 532, 'scissoring           ' )
    STRAP_ON              = _BaseCategory( 542, 'strap-on             ' )
    TATTOOED_MEN_GAY      = _BaseCategory( 552, 'tattooed-men-gay     ' )
    TATTOOED_WOMEN        = _BaseCategory( 562, 'tattooed-women       ' )
    TRANS_WITH_GIRL       = _BaseCategory( 572, 'trans-with-girl      ' )
    TRANS_WITH_GUY        = _BaseCategory( 582, 'trans-with-guy       ' )
    FINGERING             = _BaseCategory( 592, 'fingering            ' )
    TRANS_MALE            = _BaseCategory( 602, 'trans-male           ' )
    _360_1                = _BaseCategory( 612, '360-1                ' )
    _180_1                = _BaseCategory( 622, '180-1                ' )
    _2D                   = _BaseCategory( 632, '2d                   ' )
    _3D                   = _BaseCategory( 642, '3d                   ' )
    VOYEUR                = _BaseCategory( 682, 'voyeur               ' )
    POV_1                 = _BaseCategory( 702, 'pov-1                ' )
    UNCENSORED            = _BaseCategory( 712, 'uncensored           ' )
    UNCENSORED_1          = _BaseCategory( 722, 'uncensored-1         ' )
    VERIFIED_AMATEURS_GAY = _BaseCategory( 731, 'verified-amateurs-gay' )
    CLOSED_CAPTIONS       = _BaseCategory( 732, 'closed-captions      ' )
    CLOSED_CAPTIONS_GAY   = _BaseCategory( 742, 'closed-captions-gay  ' )
    FFM                   = _BaseCategory( 761, 'ffm                  ' )
    FMM                   = _BaseCategory( 771, 'fmm                  ' )
    #@END-CATEGORY


class _BaseQuality:
    
    def __init__(self, value: Literal['best', 'half', 'worst'] | int | Self) -> None:
        '''
        Initialise a new quality object.
        '''
        
        self.value = value
        
        if isinstance(value, _BaseQuality):
            self.value = value.value
        
        if isinstance(self.value, str):
            assert self.value.lower() in ('best', 'half', 'worst')
    
    def select(self, qualities: dict) -> str:
        '''
        Select among a list of qualities.
        
        Args:
            quals (dict): A dict containing qualities and URLs.
        
        Returns:
            str: The chosen quality URL.
        '''
        
        keys = list(qualities.keys())
        
        if isinstance(self.value, str):
            # Get approximative quality
            
            if self.value == 'best': return qualities[max(keys)]
            elif self.value == 'worst': return qualities[min(keys)]
            else: return qualities[ sorted(keys)[ len(keys) // 2 ] ]
        
        elif isinstance(self.value, int):
            # Get exact quality or nearest
            
            if (s:= str(self.value)) in keys: return qualities[s]
            else: return qualities[utils.closest(keys, self.value)]
        
        # This should not happen
        raise TypeError('Internal error: quality type is', type(self.value))

class Quality(_BaseQuality):
    '''
    Represents a video quality.
    '''
    
    BEST = _BaseQuality('best')
    HALF = _BaseQuality('half')
    WORST = _BaseQuality('worst')
    
# EOF