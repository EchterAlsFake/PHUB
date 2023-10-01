![PHUB](https://github.com/Egsagon/PHUB/blob/master/assets/banner.png)

# PHUB - An API for PornHub.

PHUB is an hybrid API for Pornhub. It is able to communicate with Pornhub
using both web-scraping and Pornhub's HubTraffic API. It is
able to access most used or useful PH features, such as video searching,
accessing account features, video downloading, and a lot more.

> ⚠️ This project is probably against Pornhub TOS. Use at your own risks.

## Installation

- Install using `pip` (python `3.11` or higher required, recommended version): 
```sh
pip install --upgrade phub
```

- Or from this repo to get latest fixes/features:
```sh
pip install --upgrade git+https://github.com/Egsagon/PHUB.git
```

- Or, if you need a lower python version (down to `3.9`)
```
pip install phub==4.0b0
# Or, dev branch
pip install --upgrade git+https://github.com/Egsagon/PHUB.git@py-3.9
```

## Quickstart

```python
import phub
from phub.locals import *

# Initialise a client
client = phub.Client()

# Fetch and download a video
video = client.get('https://...')
video.download('my-video.mp4', Quality.BEST)

# Fetch user videos
user = client.get_user('this-user')
for video in user.videos:
    print(video.title)

# Perform a research
for video in client.search('my-query'):
    print(video.title)

# Connect to an account
client = phub.Client('my-username', 'my-password')

# Access account history, liked and recommended stuff
client.account.watched
client.account.liked
client.account.recommended
```

You can check out the other available features
in the [docs](https://phub.readthedocs.io).

## License

PHUB uses GPLv3. See the `LICENSE` file.

## TODO

- [ ] Make downloading more stable
- [ ] User search filters
- [ ] Fix FFMPEG and threaded downloader

## Contributing

Feel free to contribute to this project by submiting
feature requests, issues, bugs, or whatever.
