# PHUB - An API wrapper for PornHub.

PHUB is an hybrid API for Pornhub. It is able to communicate with Pornhub
using both web-scraping and Pornhub's HubTraffic API. It is
able to access most used or useful PH features, such as video searching,
accessing account features, video downloading, and a lot more.

Learn more on the project [documentation](https://phub.readthedocs.io) and
[github page](https://github.com/Egsagon/PHUB).

## Installation

```sh
pip install --upgrade phub
```

## Quickstart

```python
import phub

client = phub.Client()

video = client.get(url = '...')
video.download('my-video.mp4', quality = 'best')
```