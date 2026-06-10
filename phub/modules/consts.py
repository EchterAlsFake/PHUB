import re
import math
import json
from bs4 import BeautifulSoup
from curl_cffi import delete

try:
    import lxml
    parser = "lxml" # Faster speeds, but more dependencies

except (ModuleNotFoundError, ImportError):
    parser = "html.parser" # Fallback to classic HTML parser (will work fine)

INCREMENT = 30
KNOWN_PRIME_FACTORS = [2, 3, 5]
HEADERS = {
    'Accept': '*/*',
    'Accept-Language': 'en,en-US',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0',
    'Referer': 'https://www.pornhub.com/',
    'Origin': 'https://www.pornhub.com',
}

COOKIES = {
    'accessAgeDisclaimerPH': '1',
    'accessAgeDisclaimerUK': '1',
    'accessPH': '1',
    'age_verified': '1',
    'cookieBannerState': '1',
    'platform': 'pc'
}


HOST = "https://www.pornhub.com/"
LOGIN_PAYLOAD = {
    'from': 'pc_login_modal_:homepage_redesign',
}

# REGEX for Video extraction:
REGEX_VIDEO_FLASHVARS = re.compile(r"var\s+flashvars_\d+\s*=\s*(\{.*?\});", re.DOTALL)

# REGEX FOR SHORTIES
REGEX_SHORTIES_FLASHVARS = re.compile(r'JSON_SHORTIES = insertAfterNthPosition\((.*?)', re.DOTALL)

# Regex for playlists and tokens
REGEX_TOKEN = re.compile(r'token\s*=\s*"([^"]+)"')


def extractor_gifs(html_content: str) -> list:
    links = []
    soup = BeautifulSoup(html_content, parser)
    
    # Try multiple possible containers for GIFs
    containers = [
        soup.find("div", class_="gifsWrapperProfile"),
        soup.find("div", class_="gifsWrapper hideLastItemLarge"),
        soup.find("div", class_="gifsWrapper"),
        soup.find("ul", class_="gifs"),
        soup.find("div", id="gifSearchListing"),
    ]
    
    # Find the first non-None container
    main_div = next((c for c in containers if c is not None), soup)

    for a_tag in main_div.find_all("a", href=True):
        href = a_tag.get("href")
        # Ensure it's a GIF link (usually /gif/ followed by digits) and not a duplicate
        if href.startswith("/gif/") and any(char.isdigit() for char in href):
            full_url = f"https://www.pornhub.com{href}"
            if full_url not in links:
                links.append(full_url)

    return list(set(links))


def extractor_videos(html_content: str) -> list:
    results = []
    soup = BeautifulSoup(html_content, parser)
    
    # Try different sections
    video_blocks = soup.find_all(["li", "div"], class_=re.compile(r"pcVideoListItem|videoBox"))

    if not video_blocks:
        # Fallback to finding all link tags if blocks aren't found
        a_tags = soup.find_all("a", href=re.compile(r"/view_video\.php\?viewkey="))
        for a_tag in a_tags:
            href = a_tag.get("href")
            url = f"https://www.pornhub.com{href}"
            if any(r["url"] == url for r in results):
                continue
            results.append({"url": url, "from_search": True})
        return results

    for block in video_blocks:
        try:
            # Find the link tag which contains the URL and title
            a_tag = block.find("a", href=re.compile(r"/view_video"))
            if not a_tag:
                continue
                
            href = a_tag.get("href")
            if not href:
                continue
                
            url = f"https://www.pornhub.com{href}"
            if any(r["url"] == url for r in results):
                continue

            title = a_tag.get("title") or (a_tag.find("img").get("alt") if a_tag.find("img") else "")
            if not title:
                # Try finding title in a separate link or span
                title_link = block.find("a", class_="title") or block.find("span", class_="title")
                title = title_link.text.strip() if title_link else ""
            
            # Extract duration if available
            duration_var = block.find("var", class_="duration")
            duration = duration_var.text.strip() if duration_var else None
            
            # Extract thumbnail
            img_tag = block.find("img")
            thumb = img_tag.get("data-src") or img_tag.get("src") if img_tag else None

            results.append({
                "url": url,
                "title": title,
                "duration": duration,
                "thumb": thumb,
                "from_search": True
            })
        except Exception:
            continue

    return results


def extractor_hubtraffic(json_content: str) -> list:
    """
    Extractor for HubTraffic API (Webmaster API) which returns JSON.
    Returns a list of dictionaries containing video data.
    """
    try:
        data = json.loads(json_content)
        videos = data.get("videos")
        if not videos:
            return []

        # We return the whole dict for each video so the iterator can pass it to Video object
        return videos
    except json.JSONDecodeError:
        return []


def extractor_videos_from_playlist_page(html_content: str) -> list:
    links = []
    soup = BeautifulSoup(html_content, parser)
    
    # Search for all 'a' tags with an href containing "/view_video.php?viewkey="
    # Use re.compile for regex matching in find_all
    for a_tag in soup.find_all("a", href=re.compile(r"/view_video\.php\?viewkey=")):
        href = a_tag.get("href")
        if href:
            # Ensure the URL is absolute
            if not href.startswith("https://www.pornhub.com"):
                links.append(f"https://www.pornhub.com{href}")
            else:
                links.append(href)
    return list(set(links))


def extractor_videos_playlist(content: str) -> list:
    links = []
    html_to_parse = None

    try:
        # Attempt to parse as JSON first
        data = json.loads(content)
        html_to_parse = data.get("html")
    except json.JSONDecodeError:
        # If it's not JSON, assume it's raw HTML
        html_to_parse = content

    if html_to_parse:
        soup = BeautifulSoup(html_to_parse, parser)
        # Search for common patterns for video links in playlist chunks
        # These patterns are derived from inspecting typical Pornhub playlist HTML
        
        # Search for all 'a' tags with an href containing "/view_video.php?viewkey="
        for a_tag in soup.find_all("a", href=re.compile(r"/view_video\.php\?viewkey=")):
            href = a_tag.get("href")
            if href:
                if not href.startswith("https://www.pornhub.com"):
                    links.append(f"https://www.pornhub.com{href}")
                else:
                    links.append(href)

    return list(set(links))


def extractor_users(html_content: str) -> list:
    """
    Extractor for users, models and pornstars.
    """
    soup = BeautifulSoup(html_content, parser)
    users = []
    # Matches the user links in the subscriptions/followers pages
    for a_tag in soup.find_all("a", class_="userLink", href=True):
        href = a_tag.get("href")
        if href.startswith("/"):
            url = f"https://www.pornhub.com{href}"
            if url not in users:
                users.append(url)

    return list(set(users))