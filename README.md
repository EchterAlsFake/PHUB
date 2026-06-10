<h1 align="center">PornHub API</h1>

<div align="center">
    <a href="https://pepy.tech/project/phub"><img src="https://static.pepy.tech/badge/phub" alt="Downloads"></a>
    <a href="https://badge.fury.io/py/phub"><img src="https://badge.fury.io/py/phub.svg" alt="PyPI version" height="18"></a>
    <a href="https://echteralsfake.me/ci/PHUB/badge.svg"><img src="https://echteralsfake.me/ci/PHUB/badge.svg" alt="API Tests"/></a>
</div>

<br>

# Disclaimer
> [!IMPORTANT]
> This is an unofficial and unaffiliated project. Please read the full disclaimer before use:
> **[DISCLAIMER.md](https://github.com/EchterAlsFake/API_Docs/blob/master/Disclaimer.md)**
>
> By using this project you agree to comply with the target site’s rules, copyright/licensing requirements,
> and applicable laws. Do not use it to bypass access controls or scrape at disruptive rates.

# Features
- Fetch videos + metadata
- Download videos
- Fetch Channels
- Fetch Pornstars
- Fetch Models
- Fetch Users
- Fetch Shorts
- Fetch Playlists
- Search for videos
- Account Login
- Access your feed, watched, liked and recommended
- Asynchronous
- Built-in caching
- Easy interface
- Great type hinting

#### Networking Features
- HTTP 2.0 / HTTP 3.0
- Browser impersonation
- Custom JA3
- All proxy types
- Proxy authentication
- Speed Limit
- DNS over HTTPS
- And even more...
- All of this is configurable and can be adjusted as you like!

# Supported Platforms
This API has been tested and confirmed working on:

- Windows 11 (x64) 
- macOS Sequoia (x86_64)
- Linux (Arch) (x86_64)
- Android 16 (aarch64)

# Quickstart

> [!NOTE]
> Full Documentation: [here](https://github.com/EchterAlsFake/API_Docs/blob/master/Porn_APIs/PHUB.md)

```python
import asyncio
import phub

async def main():
    # Initialize an async client
    client = phub.Client()

    # Fetch and download a video
    video = await client.get_video('https://...')
    await video.ensure_html() # For Downloading the HTML Code needs to be retrieved!
    await video.download(quality="best", path="my-video.mp4") # See docs for more options

    # Fetch user videos
    user = await client.get_user('this-user')
    async for video in user.get_videos():
        print(video.title)

    # Perform a search
    async for video in client.search_videos('my-query'):
        print(video.title)

    # Connect to an account
    client = phub.Client(email='my-email', password='my-password', login=True)
    await asyncio.sleep(2) # Allow login task to finish
    
    # Alternatively, manually await login:
    # await client.login()

    # Access account history, liked and recommended stuff
    async for video in client.get_history():
        print(video.title)
        
    async for video in client.get_favorites():
        print(video.title)
        
    async for video in client.get_recommended():
        print(video.title)

if __name__ == "__main__":
    asyncio.run(main())
```

# License
PHUB uses LGPLv3. See the `LICENSE` file.

This repository was initiated and maintained by [Egsagon](https://github.com/Egsagon)
He doesn't have any time to maintain this and transferred me the ownership.
I'll do my best to maintain this repository functional.

# Donations
If you want to donate, I and Egsagon will gladly appreciate it. Donations will be split 50/50 between us. 
Please use PayPal for donating, as it makes it easier. Thanks a lot! 

- https://paypal.me/EchterAlsFake

# Contributing
Feel free to contribute to this project by submitting
feature requests, issues, bugs, or whatever.
