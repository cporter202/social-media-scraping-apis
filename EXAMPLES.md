# Social Media Scraping APIs - Code Examples

Quick start examples for popular APIs in this collection.

## Prerequisites

All examples use **Apify API**. Get your free API token at [apify.com](https://apify.com).

```bash
export APIFY_TOKEN="your_token_here"
```

---

## LinkedIn Profile Scraper

Extract LinkedIn profile data without cookies.

### cURL
```bash
curl -X POST "https://api.apify.com/v2/acts/dataweave~linkedin-profile-scraper/run-sync-get-dataset-items?token=$APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "profileUrls": ["https://www.linkedin.com/in/john-doe"],
    "proxy": { "useApifyProxy": true }
  }'
```

### Python
```python
import requests

response = requests.post(
    "https://api.apify.com/v2/acts/dataweave~linkedin-profile-scraper/run-sync-get-dataset-items",
    headers={"Content-Type": "application/json"},
    json={
        "token": "your_token",
        "profileUrls": ["https://www.linkedin.com/in/john-doe"],
        "proxy": {"useApifyProxy": True}
    }
)

data = response.json()
for profile in data:
    print(f"Name: {profile.get('firstName')} {profile.get('lastName')}")
    print(f"Headline: {profile.get('headline')}")
    print(f"Experience: {len(profile.get('experience', []))} positions")
```

### Node.js
```javascript
const response = await fetch('https://api.apify.com/v2/acts/dataweave~linkedin-profile-scraper/run-sync-get-dataset-items', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    token: process.env.APIFY_TOKEN,
    profileUrls: ['https://www.linkedin.com/in/john-doe'],
    proxy: { useApifyProxy: true }
  })
});

const data = await response.json();
console.log(data);
```

---

## Instagram Post Scraper

Download Instagram posts, videos, and metadata.

### Python
```python
import requests

# Scrape Instagram post
response = requests.post(
    "https://api.apify.com/v2/acts/scrapearchitect~instagram-post-video-scraper-video-post-downloader/run-sync-get-dataset-items",
    headers={"Content-Type": "application/json"},
    json={
        "token": "your_token",
        "urls": ["https://www.instagram.com/p/ABC123/"],
        "downloadVideo": True
    }
)

post = response.json()[0]
print(f"Caption: {post.get('caption')}")
print(f"Likes: {post.get('likesCount')}")
print(f"Video URL: {post.get('videoUrl')}")
```

---

## Twitter/X Tweet Scraper

Extract tweets without API limits.

### Python
```python
import requests

# Search tweets by keyword
response = requests.post(
    "https://api.apify.com/v2/acts/apidojo~tweet-scraper/run-sync-get-dataset-items",
    headers={"Content-Type": "application/json"},
    json={
        "token": "your_token",
        "searchTerms": ["#AI", "machine learning"],
        "maxItems": 100,
        "sort": "latest"
    }
)

tweets = response.json()
for tweet in tweets:
    print(f"@{tweet.get('author', {}).get('userName')}: {tweet.get('text')[:100]}...")
```

---

## YouTube Channel Scraper

Collect videos and metadata from YouTube channels.

### Python
```python
import requests

response = requests.post(
    "https://api.apify.com/v2/acts/apidojo~youtube-channel-scraper/run-sync-get-dataset-items",
    headers={"Content-Type": "application/json"},
    json={
        "token": "your_token",
        "channelUrls": ["https://www.youtube.com/@ChannelName"],
        "maxResults": 50
    }
)

videos = response.json()
for video in videos:
    print(f"Title: {video.get('title')}")
    print(f"Views: {video.get('viewCount')}")
    print(f"Published: {video.get('uploadDate')}")
```

---

## TikTok Video Downloader

Download TikTok videos without watermark.

### Python
```python
import requests

response = requests.post(
    "https://api.apify.com/v2/acts/scrapearchitect~tiktok-video-audio-mp3-downloader/run-sync-get-dataset-items",
    headers={"Content-Type": "application/json"},
    json={
        "token": "your_token",
        "urls": ["https://www.tiktok.com/@user/video/123456"],
        "downloadVideo": True,
        "removeWatermark": True
    }
)

video = response.json()[0]
print(f"Download URL: {video.get('videoUrlNoWatermark')}")
print(f"Views: {video.get('playCount')}")
print(f"Likes: {video.get('diggCount')}")
```

---

## Advanced: Batch Processing

Process multiple URLs efficiently.

### Python
```python
import requests
import time

def scrape_profiles(urls, actor_id):
    """Batch scrape LinkedIn profiles"""
    
    # Start actor run
    response = requests.post(
        f"https://api.apify.com/v2/acts/{actor_id}/runs",
        headers={"Content-Type": "application/json"},
        json={
            "token": "your_token",
            "profileUrls": urls
        }
    )
    
    run_id = response.json()["data"]["id"]
    
    # Wait for completion
    while True:
        status = requests.get(
            f"https://api.apify.com/v2/actor-runs/{run_id}",
            headers={"Authorization": "Bearer your_token"}
        ).json()
        
        if status["data"]["status"] in ["SUCCEEDED", "FAILED"]:
            break
        time.sleep(5)
    
    # Get results
    dataset_id = status["data"]["defaultDatasetId"]
    results = requests.get(
        f"https://api.apify.com/v2/datasets/{dataset_id}/items",
        headers={"Authorization": "Bearer your_token"}
    ).json()
    
    return results

# Example usage
urls = [
    "https://www.linkedin.com/in/user1",
    "https://www.linkedin.com/in/user2",
    "https://www.linkedin.com/in/user3"
]

profiles = scrape_profiles(urls, "dataweave~linkedin-profile-scraper")
```

---

## Error Handling

Always handle errors gracefully.

### Python
```python
import requests
from requests.exceptions import RequestException

def safe_scrape(url, payload):
    try:
        response = requests.post(url, json=payload, timeout=300)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        print(f"Request failed: {e}")
        return None
    except ValueError as e:
        print(f"Invalid JSON: {e}")
        return None
```

---

## Rate Limiting

Be respectful of API limits.

### Python
```python
import time
import requests

def rate_limited_scrape(urls, delay=2):
    """Scrape with delay between requests"""
    results = []
    for url in urls:
        result = scrape_single(url)
        results.append(result)
        time.sleep(delay)  # Wait between requests
    return results
```

---

## More Examples

Check the [API directory](./social-media-apis-3268/) for specific examples for each API.

## Need Help?

- 📖 [Apify Documentation](https://docs.apify.com/)
- 💬 [Apify Discord](https://discord.gg/apify)
- 🐛 [Report Issues](https://github.com/cporter202/social-media-scraping-apis/issues)

---

**Happy Scraping!** 🚀
