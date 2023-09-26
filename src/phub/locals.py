'''
Dynamic file.
'''

from typing import Union

from .objects import Param, NO_PARAM
from .objects import _BaseQuality

class Quality(_BaseQuality):
    '''
    Represents a video quality.
    Can also be represented as an int
    or string.
    '''
    
    BEST  = _BaseQuality('best' )
    HALF  = _BaseQuality('half' )
    WORST = _BaseQuality('worst')

class Section:
    '''
    Represents a Feed filter section.
    '''
    
    ALL            = Param('section', ''                , single = True)
    POST           = Param('section', 'posts'           , single = True)
    PHOTO          = Param('section', 'albums'          , single = True)
    VIDEO          = Param('section', 'videos'          , single = True)
    CHANNEL_VIDEO  = Param('section', 'channels'        , single = True)
    COMMENT        = Param('section', 'comments'        , single = True)
    FAVORITE       = Param('section', 'favourite'       , single = True)
    PLAYLIST       = Param('section', 'playlists'       , single = True)
    VERIFIED_VIDEO = Param('section', 'pornstars_models', single = True)

class Production:
    '''
    Represents a production type.
    '''
    
    HOMEMADE     = HOME = Param('p', 'homemade'    , single = True)
    PROFESSIONAL = PRO  = Param('p', 'professional', single = True)

class Category:
    '''
    Represents a video search category.
    '''
    
    #START@CATEGORIES
    ASIAN                 = Param( 'category', '1@asian'              )
    ORGY                  = Param( 'category', '2@orgy'               )
    AMATEUR               = Param( 'category', '3@amateur'            )
    BIG_ASS               = Param( 'category', '4@big-ass'            )
    BABE                  = Param( 'category', '5@babe'               )
    BBW                   = Param( 'category', '6@bbw'                )
    BIG_DICK              = Param( 'category', '7@big-dick'           )
    BIG_TITS              = Param( 'category', '8@big-tits'           )
    BLONDE                = Param( 'category', '9@blonde'             )
    BONDAGE               = Param( 'category', '10@bondage'           )
    BRUNETTE              = Param( 'category', '11@brunette'          )
    CELEBRITY             = Param( 'category', '12@celebrity'         )
    BLOWJOB               = Param( 'category', '13@blowjob'           )
    BUKKAKE               = Param( 'category', '14@bukkake'           )
    CREAMPIE              = Param( 'category', '15@creampie'          )
    CUMSHOT               = Param( 'category', '16@cumshot'           )
    EBONY                 = Param( 'category', '17@ebony'             )
    FETISH                = Param( 'category', '18@fetish'            )
    FISTING               = Param( 'category', '19@fisting'           )
    HANDJOB               = Param( 'category', '20@handjob'           )
    HARDCORE              = Param( 'category', '21@hardcore'          )
    MASTURBATION          = Param( 'category', '22@masturbation'      )
    TOYS                  = Param( 'category', '23@toys'              )
    PUBLIC                = Param( 'category', '24@public'            )
    INTERRACIAL           = Param( 'category', '25@interracial'       )
    LATINA                = Param( 'category', '26@latina'            )
    LESBIAN               = Param( 'category', '27@lesbian'           )
    MATURE                = Param( 'category', '28@mature'            )
    MILF                  = Param( 'category', '29@milf'              )
    PORNSTAR              = Param( 'category', '30@pornstar'          )
    REALITY               = Param( 'category', '31@reality'           )
    FUNNY                 = Param( 'category', '32@funny'             )
    STRIPTEASE            = Param( 'category', '33@striptease'        )
    ANAL                  = Param( 'category', '35@anal'              )
    HENTAI                = Param( 'category', '36@hentai'            )
    TEEN_18_1             = Param( 'category', '37@teen-18-1'         )
    HD_PORN               = Param( 'category', '38@hd-porn'           )
    JAPANESE_GAY          = Param( 'category', '39@japanese-gay'      )
    BAREBACK_GAY          = Param( 'category', '40@bareback-gay'      )
    POV                   = Param( 'category', '41@pov'               )
    RED_HEAD              = Param( 'category', '42@red-head'          )
    VINTAGE               = Param( 'category', '43@vintage'           )
    BLACK_GAY             = Param( 'category', '44@black-gay'         )
    MASSAGE_GAY           = Param( 'category', '45@massage-gay'       )
    EURO_GAY              = Param( 'category', '46@euro-gay'          )
    DADDY_GAY             = Param( 'category', '47@daddy-gay'         )
    ASIAN_GAY             = Param( 'category', '48@asian-gay'         )
    TWINK_18              = Param( 'category', '49@twink-18'          )
    LATINO_GAY            = Param( 'category', '50@latino-gay'        )
    MUSCLE_GAY            = Param( 'category', '51@muscle-gay'        )
    FETISH_GAY            = Param( 'category', '52@fetish-gay'        )
    PARTY                 = Param( 'category', '53@party'             )
    SOLO_MALE_GAY         = Param( 'category', '54@solo-male-gay'     )
    EURO                  = Param( 'category', '55@euro'              )
    BLOWJOB_GAY           = Param( 'category', '56@blowjob-gay'       )
    COMPILATION           = Param( 'category', '57@compilation'       )
    BIG_DICK_GAY          = Param( 'category', '58@big-dick-gay'      )
    SMALL_TITS            = Param( 'category', '59@small-tits'        )
    PORNSTAR_GAY          = Param( 'category', '60@pornstar-gay'      )
    WEBCAM                = Param( 'category', '61@webcam'            )
    GROUP_GAY             = Param( 'category', '62@group-gay'         )
    GAY                   = Param( 'category', '63@gay'               )
    INTERRACIAL_GAY       = Param( 'category', '64@interracial-gay'   )
    THREESOME             = Param( 'category', '65@threesome'         )
    BEAR_GAY              = Param( 'category', '66@bear-gay'          )
    ROUGH_SEX             = Param( 'category', '67@rough-sex'         )
    COLLEGE_18            = Param( 'category', '68@college-18'        )
    SQUIRT                = Param( 'category', '69@squirt'            )
    HUNKS_GAY             = Param( 'category', '70@hunks-gay'         )
    CREAMPIE_GAY          = Param( 'category', '71@creampie-gay'      )
    DOUBLE_PENETRATION    = Param( 'category', '72@double-penetration')
    POPULAR_WITH_WOMEN    = Param( 'category', '73@popular-with-women')
    BISEXUAL_MALE         = Param( 'category', '76@bisexual-male'     )
    VINTAGE_GAY           = Param( 'category', '77@vintage-gay'       )
    MASSAGE               = Param( 'category', '78@massage'           )
    COLLEGE_18_1          = Param( 'category', '79@college-18-1'      )
    GANGBANG              = Param( 'category', '80@gangbang'          )
    ROLE_PLAY             = Param( 'category', '81@role-play'         )
    STRAIGHT_GUYS_GAY     = Param( 'category', '82@straight-guys-gay' )
    TRANSGENDER           = Param( 'category', '83@transgender'       )
    PUBLIC_GAY            = Param( 'category', '84@public-gay'        )
    REALITY_GAY           = Param( 'category', '85@reality-gay'       )
    CARTOON               = Param( 'category', '86@cartoon'           )
    SCHOOL_18             = Param( 'category', '88@school-18'         )
    BABYSITTER_18         = Param( 'category', '89@babysitter-18'     )
    CASTING               = Param( 'category', '90@casting'           )
    SMOKING               = Param( 'category', '91@smoking'           )
    SOLO_MALE             = Param( 'category', '92@solo-male'         )
    FEET                  = Param( 'category', '93@feet'              )
    FRENCH                = Param( 'category', '94@french'            )
    GERMAN                = Param( 'category', '95@german'            )
    BRITISH               = Param( 'category', '96@british'           )
    ITALIAN               = Param( 'category', '97@italian'           )
    ARAB                  = Param( 'category', '98@arab'              )
    RUSSIAN               = Param( 'category', '99@russian'           )
    CZECH                 = Param( 'category', '100@czech'            )
    INDIAN                = Param( 'category', '101@indian'           )
    BRAZILIAN             = Param( 'category', '102@brazilian'        )
    KOREAN                = Param( 'category', '103@korean'           )
    VR                    = Param( 'category', '104@vr'               )
    _60FPS_1              = Param( 'category', '105@60fps-1'          )
    VR_GAY                = Param( 'category', '106@vr-gay'           )
    HD_PORN_GAY           = Param( 'category', '107@hd-porn-gay'      )
    INTERACTIVE           = Param( 'category', '108@interactive'      )
    JAPANESE              = Param( 'category', '111@japanese'         )
    EXCLUSIVE             = Param( 'category', '115@exclusive'        )
    MUSIC                 = Param( 'category', '121@music'            )
    PUSSY_LICKING         = Param( 'category', '131@pussy-licking'    )
    VERIFIED_AMATEURS     = Param( 'category', '138@verified-amateurs')
    VERIFIED_MODELS       = Param( 'category', '139@verified-models'  )
    BEHIND_THE_SCENES     = Param( 'category', '141@behind-the-scenes')
    OLD_YOUNG_18          = Param( 'category', '181@old-young-18'     )
    PARODY                = Param( 'category', '201@parody'           )
    PISSING               = Param( 'category', '211@pissing'          )
    SFW                   = Param( 'category', '221@sfw'              )
    DESCRIBED_VIDEO       = Param( 'category', '231@described-video'  )
    COSPLAY               = Param( 'category', '241@cosplay'          )
    CUCKOLD               = Param( 'category', '242@cuckold'          )
    AMATEUR_GAY           = Param( 'category', '252@amateur-gay'      )
    HANDJOB_GAY           = Param( 'category', '262@handjob-gay'      )
    UNCUT_GAY             = Param( 'category', '272@uncut-gay'        )
    ROUGH_SEX_GAY         = Param( 'category', '312@rough-sex-gay'    )
    JOCK_GAY              = Param( 'category', '322@jock-gay'         )
    MATURE_GAY            = Param( 'category', '332@mature-gay'       )
    WEBCAM_GAY            = Param( 'category', '342@webcam-gay'       )
    CUMSHOT_GAY           = Param( 'category', '352@cumshot-gay'      )
    CASTING_GAY           = Param( 'category', '362@casting-gay'      )
    POV_GAY               = Param( 'category', '372@pov-gay'          )
    COMPILATION_GAY       = Param( 'category', '382@compilation-gay'  )
    CHUBBY_GAY            = Param( 'category', '392@chubby-gay'       )
    MILITARY_GAY          = Param( 'category', '402@military-gay'     )
    FEET_GAY              = Param( 'category', '412@feet-gay'         )
    CARTOON_GAY           = Param( 'category', '422@cartoon-gay'      )
    STEP_FANTASY          = Param( 'category', '444@step-fantasy'     )
    VERIFIED_COUPLES      = Param( 'category', '482@verified-couples' )
    SOLO_FEMALE           = Param( 'category', '492@solo-female'      )
    FEMALE_ORGASM         = Param( 'category', '502@female-orgasm'    )
    MUSCULAR_MEN          = Param( 'category', '512@muscular-men'     )
    ROMANTIC              = Param( 'category', '522@romantic'         )
    SCISSORING            = Param( 'category', '532@scissoring'       )
    STRAP_ON              = Param( 'category', '542@strap-on'         )
    TATTOOED_MEN_GAY      = Param( 'category', '552@tattooed-men-gay' )
    TATTOOED_WOMEN        = Param( 'category', '562@tattooed-women'   )
    TRANS_WITH_GIRL       = Param( 'category', '572@trans-with-girl'  )
    TRANS_WITH_GUY        = Param( 'category', '582@trans-with-guy'   )
    FINGERING             = Param( 'category', '592@fingering'        )
    TRANS_MALE            = Param( 'category', '602@trans-male'       )
    _360_1                = Param( 'category', '612@360-1'            )
    _180_1                = Param( 'category', '622@180-1'            )
    _2D                   = Param( 'category', '632@2d'               )
    _3D                   = Param( 'category', '642@3d'               )
    VOYEUR                = Param( 'category', '682@voyeur'           )
    POV_1                 = Param( 'category', '702@pov-1'            )
    UNCENSORED            = Param( 'category', '712@uncensored'       )
    UNCENSORED_1          = Param( 'category', '722@uncensored-1'     )
    VERIFIED_AMATEURS_GAY = Param( 'category', '731@verified-amateurs-gay')
    CLOSED_CAPTIONS       = Param( 'category', '732@closed-captions'  )
    CLOSED_CAPTIONS_GAY   = Param( 'category', '742@closed-captions-gay')
    FFM                   = Param( 'category', '761@ffm'              )
    FMM                   = Param( 'category', '771@fmm'              )
    #END@CATEGORIES

class Sort:
    '''
    Represents a specific sorting algorithm.
    '''
    
    # Video sorting    
    VIDEO_MOST_RECENT = Param('o', 'mr', single = True)
    VIDEO_MOST_VIEWS  = Param('o', 'mv', single = True)
    VIDEO_TOP_RATED   = Param('o', 'tr', single = True)
    VIDEO_LONGUEST    = Param('o', 'lg', single = True)
    
    # User sorting
    USER_POPULAR = Param('o', 'popular', single = True)
    USER_NEWEST  = Param('o', 'newest', single = True)
    
    # Time sorting
    ALL_TIME = Param('t', None, single = True)
    DAYLY    = Param('t', 't',  single = True)
    WEEKLY   = Param('t', 'w',  single = True)
    MONTHLY  = Param('t', 'm',  single = True)
    YEARLY   = Param('t', 'y',  single = True)

class Member:
    '''
    Represents specific filters for a member.
    '''
    
    # User type
    IS_ONLINE  = Param('online', '1')
    IS_MODEL   = Param('isPornhubModel', '1')
    IS_STAFF   = Param('staff', '1')
    
    # use account attributes
    HAS_AVATAR = Param('avatar', '1')
    HAS_VIDEOS    = Param('videos', '1')
    HAS_PHOTOS    = Param('photos', '1')
    HAS_PLAYLISTS = Param('playlists', '1')
    
    # Relationship
    SINGLE          = Param('relation', '1', single = True)
    TAKEN           = Param('relation', '2', single = True)
    OPEN_RELATION   = Param('relation', '3', single = True)
    
    # Gender
    GENDER_MALE          = Param('gender', '1',  single = True)
    GENDER_FEMALE        = Param('gender', '2',  single = True)
    GENDER_COUPLE        = Param('gender', '3',  single = True)
    GENDER_TRANS_FEMALE  = Param('gender', '5',  single = True)
    GENDER_FEMALE_COUPLE = Param('gender', '6',  single = True)
    GENDER_MALE_COUPLE   = Param('gender', '7',  single = True)
    GENDER_TRANS_MALE    = Param('gender', '9',  single = True)
    GENDER_OTHER         = Param('gender', '10', single = True)
    GENDER_NON_BINARY    = Param('gender', '11', single = True)
    
    # Into
    INTO_NONE   = Param('orientation', '0', single = True)
    INTO_MALE   = Param('orientation', '1', single = True)
    INTO_FEMALE = Param('orientation', '2', single = True)
    INTO_ALL    = Param('orientation', '3', single = True)
    
    # Offers
    OFFER_CUSTOM_VIDEOS = Param('offering', 'customvideo')
    OFFER_FAN_CLUBS     = Param('offering', 'fanclub')


constant = Union[Category, Production, Sort, Param]

FEED_CLASS_TO_CONST = {
    'stream_videos_uploaded': Section.VIDEO,
    'stream_favourites_videos': Section.FAVORITE,
    'stream_grouped_comments_videos': Section.COMMENT,
    'stream_subscriptions_pornstars': Section.VERIFIED_VIDEO,
    # etc.
}

__all__ = [
    'NO_PARAM',
    'Quality',
    'Section',
    'Production',
    'Category',
    'Sort',
    'constant',
    'Member'
]

# EOF