'''
Dynamic file.
'''

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
    ASIAN                 = Param( 'category', '1@asian'              , reverse = True)
    ORGY                  = Param( 'category', '2@orgy'               , reverse = True)
    AMATEUR               = Param( 'category', '3@amateur'            , reverse = True)
    BIG_ASS               = Param( 'category', '4@big-ass'            , reverse = True)
    BABE                  = Param( 'category', '5@babe'               , reverse = True)
    BBW                   = Param( 'category', '6@bbw'                , reverse = True)
    BIG_DICK              = Param( 'category', '7@big-dick'           , reverse = True)
    BIG_TITS              = Param( 'category', '8@big-tits'           , reverse = True)
    BLONDE                = Param( 'category', '9@blonde'             , reverse = True)
    BONDAGE               = Param( 'category', '10@bondage'           , reverse = True)
    BRUNETTE              = Param( 'category', '11@brunette'          , reverse = True)
    CELEBRITY             = Param( 'category', '12@celebrity'         , reverse = True)
    BLOWJOB               = Param( 'category', '13@blowjob'           , reverse = True)
    BUKKAKE               = Param( 'category', '14@bukkake'           , reverse = True)
    CREAMPIE              = Param( 'category', '15@creampie'          , reverse = True)
    CUMSHOT               = Param( 'category', '16@cumshot'           , reverse = True)
    EBONY                 = Param( 'category', '17@ebony'             , reverse = True)
    FETISH                = Param( 'category', '18@fetish'            , reverse = True)
    FISTING               = Param( 'category', '19@fisting'           , reverse = True)
    HANDJOB               = Param( 'category', '20@handjob'           , reverse = True)
    HARDCORE              = Param( 'category', '21@hardcore'          , reverse = True)
    MASTURBATION          = Param( 'category', '22@masturbation'      , reverse = True)
    TOYS                  = Param( 'category', '23@toys'              , reverse = True)
    PUBLIC                = Param( 'category', '24@public'            , reverse = True)
    INTERRACIAL           = Param( 'category', '25@interracial'       , reverse = True)
    LATINA                = Param( 'category', '26@latina'            , reverse = True)
    LESBIAN               = Param( 'category', '27@lesbian'           , reverse = True)
    MATURE                = Param( 'category', '28@mature'            , reverse = True)
    MILF                  = Param( 'category', '29@milf'              , reverse = True)
    PORNSTAR              = Param( 'category', '30@pornstar'          , reverse = True)
    REALITY               = Param( 'category', '31@reality'           , reverse = True)
    FUNNY                 = Param( 'category', '32@funny'             , reverse = True)
    STRIPTEASE            = Param( 'category', '33@striptease'        , reverse = True)
    ANAL                  = Param( 'category', '35@anal'              , reverse = True)
    HENTAI                = Param( 'category', '36@hentai'            , reverse = True)
    TEEN_18_1             = Param( 'category', '37@teen-18-1'         , reverse = True)
    HD_PORN               = Param( 'category', '38@hd-porn'           , reverse = True)
    JAPANESE_GAY          = Param( 'category', '39@japanese-gay'      , reverse = True)
    BAREBACK_GAY          = Param( 'category', '40@bareback-gay'      , reverse = True)
    POV                   = Param( 'category', '41@pov'               , reverse = True)
    RED_HEAD              = Param( 'category', '42@red-head'          , reverse = True)
    VINTAGE               = Param( 'category', '43@vintage'           , reverse = True)
    BLACK_GAY             = Param( 'category', '44@black-gay'         , reverse = True)
    MASSAGE_GAY           = Param( 'category', '45@massage-gay'       , reverse = True)
    EURO_GAY              = Param( 'category', '46@euro-gay'          , reverse = True)
    DADDY_GAY             = Param( 'category', '47@daddy-gay'         , reverse = True)
    ASIAN_GAY             = Param( 'category', '48@asian-gay'         , reverse = True)
    TWINK_18              = Param( 'category', '49@twink-18'          , reverse = True)
    LATINO_GAY            = Param( 'category', '50@latino-gay'        , reverse = True)
    MUSCLE_GAY            = Param( 'category', '51@muscle-gay'        , reverse = True)
    FETISH_GAY            = Param( 'category', '52@fetish-gay'        , reverse = True)
    PARTY                 = Param( 'category', '53@party'             , reverse = True)
    SOLO_MALE_GAY         = Param( 'category', '54@solo-male-gay'     , reverse = True)
    EURO                  = Param( 'category', '55@euro'              , reverse = True)
    BLOWJOB_GAY           = Param( 'category', '56@blowjob-gay'       , reverse = True)
    COMPILATION           = Param( 'category', '57@compilation'       , reverse = True)
    BIG_DICK_GAY          = Param( 'category', '58@big-dick-gay'      , reverse = True)
    SMALL_TITS            = Param( 'category', '59@small-tits'        , reverse = True)
    PORNSTAR_GAY          = Param( 'category', '60@pornstar-gay'      , reverse = True)
    WEBCAM                = Param( 'category', '61@webcam'            , reverse = True)
    GROUP_GAY             = Param( 'category', '62@group-gay'         , reverse = True)
    GAY                   = Param( 'category', '63@gay'               , reverse = True)
    INTERRACIAL_GAY       = Param( 'category', '64@interracial-gay'   , reverse = True)
    THREESOME             = Param( 'category', '65@threesome'         , reverse = True)
    BEAR_GAY              = Param( 'category', '66@bear-gay'          , reverse = True)
    ROUGH_SEX             = Param( 'category', '67@rough-sex'         , reverse = True)
    COLLEGE_18            = Param( 'category', '68@college-18'        , reverse = True)
    SQUIRT                = Param( 'category', '69@squirt'            , reverse = True)
    HUNKS_GAY             = Param( 'category', '70@hunks-gay'         , reverse = True)
    CREAMPIE_GAY          = Param( 'category', '71@creampie-gay'      , reverse = True)
    DOUBLE_PENETRATION    = Param( 'category', '72@double-penetration', reverse = True)
    POPULAR_WITH_WOMEN    = Param( 'category', '73@popular-with-women', reverse = True)
    BISEXUAL_MALE         = Param( 'category', '76@bisexual-male'     , reverse = True)
    VINTAGE_GAY           = Param( 'category', '77@vintage-gay'       , reverse = True)
    MASSAGE               = Param( 'category', '78@massage'           , reverse = True)
    COLLEGE_18_1          = Param( 'category', '79@college-18-1'      , reverse = True)
    GANGBANG              = Param( 'category', '80@gangbang'          , reverse = True)
    ROLE_PLAY             = Param( 'category', '81@role-play'         , reverse = True)
    STRAIGHT_GUYS_GAY     = Param( 'category', '82@straight-guys-gay' , reverse = True)
    TRANSGENDER           = Param( 'category', '83@transgender'       , reverse = True)
    PUBLIC_GAY            = Param( 'category', '84@public-gay'        , reverse = True)
    REALITY_GAY           = Param( 'category', '85@reality-gay'       , reverse = True)
    CARTOON               = Param( 'category', '86@cartoon'           , reverse = True)
    SCHOOL_18             = Param( 'category', '88@school-18'         , reverse = True)
    BABYSITTER_18         = Param( 'category', '89@babysitter-18'     , reverse = True)
    CASTING               = Param( 'category', '90@casting'           , reverse = True)
    SMOKING               = Param( 'category', '91@smoking'           , reverse = True)
    SOLO_MALE             = Param( 'category', '92@solo-male'         , reverse = True)
    FEET                  = Param( 'category', '93@feet'              , reverse = True)
    FRENCH                = Param( 'category', '94@french'            , reverse = True)
    GERMAN                = Param( 'category', '95@german'            , reverse = True)
    BRITISH               = Param( 'category', '96@british'           , reverse = True)
    ITALIAN               = Param( 'category', '97@italian'           , reverse = True)
    ARAB                  = Param( 'category', '98@arab'              , reverse = True)
    RUSSIAN               = Param( 'category', '99@russian'           , reverse = True)
    CZECH                 = Param( 'category', '100@czech'            , reverse = True)
    INDIAN                = Param( 'category', '101@indian'           , reverse = True)
    BRAZILIAN             = Param( 'category', '102@brazilian'        , reverse = True)
    KOREAN                = Param( 'category', '103@korean'           , reverse = True)
    VR                    = Param( 'category', '104@vr'               , reverse = True)
    _60FPS_1              = Param( 'category', '105@60fps-1'          , reverse = True)
    VR_GAY                = Param( 'category', '106@vr-gay'           , reverse = True)
    HD_PORN_GAY           = Param( 'category', '107@hd-porn-gay'      , reverse = True)
    INTERACTIVE           = Param( 'category', '108@interactive'      , reverse = True)
    JAPANESE              = Param( 'category', '111@japanese'         , reverse = True)
    EXCLUSIVE             = Param( 'category', '115@exclusive'        , reverse = True)
    MUSIC                 = Param( 'category', '121@music'            , reverse = True)
    PUSSY_LICKING         = Param( 'category', '131@pussy-licking'    , reverse = True)
    VERIFIED_AMATEURS     = Param( 'category', '138@verified-amateurs', reverse = True)
    VERIFIED_MODELS       = Param( 'category', '139@verified-models'  , reverse = True)
    BEHIND_THE_SCENES     = Param( 'category', '141@behind-the-scenes', reverse = True)
    OLD_YOUNG_18          = Param( 'category', '181@old-young-18'     , reverse = True)
    PARODY                = Param( 'category', '201@parody'           , reverse = True)
    PISSING               = Param( 'category', '211@pissing'          , reverse = True)
    SFW                   = Param( 'category', '221@sfw'              , reverse = True)
    DESCRIBED_VIDEO       = Param( 'category', '231@described-video'  , reverse = True)
    COSPLAY               = Param( 'category', '241@cosplay'          , reverse = True)
    CUCKOLD               = Param( 'category', '242@cuckold'          , reverse = True)
    AMATEUR_GAY           = Param( 'category', '252@amateur-gay'      , reverse = True)
    HANDJOB_GAY           = Param( 'category', '262@handjob-gay'      , reverse = True)
    UNCUT_GAY             = Param( 'category', '272@uncut-gay'        , reverse = True)
    ROUGH_SEX_GAY         = Param( 'category', '312@rough-sex-gay'    , reverse = True)
    JOCK_GAY              = Param( 'category', '322@jock-gay'         , reverse = True)
    MATURE_GAY            = Param( 'category', '332@mature-gay'       , reverse = True)
    WEBCAM_GAY            = Param( 'category', '342@webcam-gay'       , reverse = True)
    CUMSHOT_GAY           = Param( 'category', '352@cumshot-gay'      , reverse = True)
    CASTING_GAY           = Param( 'category', '362@casting-gay'      , reverse = True)
    POV_GAY               = Param( 'category', '372@pov-gay'          , reverse = True)
    COMPILATION_GAY       = Param( 'category', '382@compilation-gay'  , reverse = True)
    CHUBBY_GAY            = Param( 'category', '392@chubby-gay'       , reverse = True)
    MILITARY_GAY          = Param( 'category', '402@military-gay'     , reverse = True)
    FEET_GAY              = Param( 'category', '412@feet-gay'         , reverse = True)
    CARTOON_GAY           = Param( 'category', '422@cartoon-gay'      , reverse = True)
    STEP_FANTASY          = Param( 'category', '444@step-fantasy'     , reverse = True)
    VERIFIED_COUPLES      = Param( 'category', '482@verified-couples' , reverse = True)
    SOLO_FEMALE           = Param( 'category', '492@solo-female'      , reverse = True)
    FEMALE_ORGASM         = Param( 'category', '502@female-orgasm'    , reverse = True)
    MUSCULAR_MEN          = Param( 'category', '512@muscular-men'     , reverse = True)
    ROMANTIC              = Param( 'category', '522@romantic'         , reverse = True)
    SCISSORING            = Param( 'category', '532@scissoring'       , reverse = True)
    STRAP_ON              = Param( 'category', '542@strap-on'         , reverse = True)
    TATTOOED_MEN_GAY      = Param( 'category', '552@tattooed-men-gay' , reverse = True)
    TATTOOED_WOMEN        = Param( 'category', '562@tattooed-women'   , reverse = True)
    TRANS_WITH_GIRL       = Param( 'category', '572@trans-with-girl'  , reverse = True)
    TRANS_WITH_GUY        = Param( 'category', '582@trans-with-guy'   , reverse = True)
    FINGERING             = Param( 'category', '592@fingering'        , reverse = True)
    TRANS_MALE            = Param( 'category', '602@trans-male'       , reverse = True)
    _360_1                = Param( 'category', '612@360-1'            , reverse = True)
    _180_1                = Param( 'category', '622@180-1'            , reverse = True)
    _2D                   = Param( 'category', '632@2d'               , reverse = True)
    _3D                   = Param( 'category', '642@3d'               , reverse = True)
    VOYEUR                = Param( 'category', '682@voyeur'           , reverse = True)
    POV_1                 = Param( 'category', '702@pov-1'            , reverse = True)
    UNCENSORED            = Param( 'category', '712@uncensored'       , reverse = True)
    UNCENSORED_1          = Param( 'category', '722@uncensored-1'     , reverse = True)
    VERIFIED_AMATEURS_GAY = Param( 'category', '731@verified-amateurs-gay', reverse = True)
    CLOSED_CAPTIONS       = Param( 'category', '732@closed-captions'  , reverse = True)
    CLOSED_CAPTIONS_GAY   = Param( 'category', '742@closed-captions-gay', reverse = True)
    FFM                   = Param( 'category', '761@ffm'              , reverse = True)
    FMM                   = Param( 'category', '771@fmm'              , reverse = True)
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
    
    # Video HD
    HD = Param('hd', '1')

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


constant = Category | Production | Sort | Param

_allowed_sort_types = NO_PARAM._concat(
    Sort.VIDEO_TOP_RATED,
    Sort.VIDEO_MOST_VIEWS
)

_sort_period_types  = NO_PARAM._concat(
    Sort.DAYLY,
    Sort.WEEKLY,
    Sort.MONTHLY,
    Sort.YEARLY
)

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