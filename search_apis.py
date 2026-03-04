#!/usr/bin/env python3
"""
Social Media API Search Tool
Search and filter APIs from the collection

Usage:
    python search_apis.py --platform linkedin
    python search_apis.py --keyword "email"
    python search_apis.py --max-price 2
    python search_apis.py --platform instagram --keyword "followers"
"""

import argparse
import json
import re
from typing import List, Dict

# API database (subset of popular APIs - full list has 3,268)
APIS = [
    {
        "name": "LinkedIn Profile Scraper",
        "platform": "linkedin",
        "price_per_1k": 2.0,
        "auth_required": False,
        "best_for": ["profiles", "work_history", "skills"],
        "speed": "fast",
        "rating": 4.8,
        "url": "https://apify.com/dataweave/linkedin-profile-scraper"
    },
    {
        "name": "LinkedIn Email Scraper",
        "platform": "linkedin",
        "price_per_1k": 2.0,
        "auth_required": False,
        "best_for": ["emails", "contact_info"],
        "speed": "fast",
        "rating": 4.5,
        "url": "https://apify.com/x_guru/linkedin-email-scraper-no-cookies"
    },
    {
        "name": "LinkedIn Company Scraper",
        "platform": "linkedin",
        "price_per_1k": 2.0,
        "auth_required": False,
        "best_for": ["company_data", "employee_count"],
        "speed": "fast",
        "rating": 4.6,
        "url": "https://apify.com/dev_fusion/linkedin-company-scraper"
    },
    {
        "name": "LinkedIn Sales Navigator",
        "platform": "linkedin",
        "price_per_1k": 20.0,
        "auth_required": True,
        "best_for": ["verified_leads", "enterprise"],
        "speed": "fast",
        "rating": 4.9,
        "url": "https://apify.com/solana/advanced-linkedin-sales-navigator-scraper-verified-leads"
    },
    {
        "name": "Instagram Post Scraper",
        "platform": "instagram",
        "price_per_1k": 3.0,
        "auth_required": False,
        "best_for": ["posts", "videos", "metadata"],
        "speed": "medium",
        "rating": 4.7,
        "url": "https://apify.com/scrapearchitect/instagram-post-video-scraper-video-post-downloader"
    },
    {
        "name": "Instagram Profile Scraper (Pay Per Result)",
        "platform": "instagram",
        "price_per_1k": 0.50,
        "auth_required": False,
        "best_for": ["bulk_profiles", "posts"],
        "speed": "fast",
        "rating": 4.8,
        "url": "https://apify.com/apidojo/instagram-scraper"
    },
    {
        "name": "Instagram Followers Scraper",
        "platform": "instagram",
        "price_per_1k": 3.0,
        "auth_required": False,
        "best_for": ["followers", "following"],
        "speed": "medium",
        "rating": 4.4,
        "url": "https://apify.com/louisdeconinck/instagram-followers-scraper"
    },
    {
        "name": "Instagram Comments Scraper",
        "platform": "instagram",
        "price_per_1k": 0.50,
        "auth_required": False,
        "best_for": ["comments", "engagement"],
        "speed": "fast",
        "rating": 4.6,
        "url": "https://apify.com/apidojo/instagram-comments-scraper"
    },
    {
        "name": "Tweet Scraper",
        "platform": "twitter",
        "price_per_1k": 0.40,
        "auth_required": False,
        "best_for": ["tweets", "search", "profiles"],
        "speed": "very_fast",
        "rating": 4.9,
        "url": "https://apify.com/apidojo/tweet-scraper"
    },
    {
        "name": "Twitter/X Profile Scraper",
        "platform": "twitter",
        "price_per_1k": 0.40,
        "auth_required": False,
        "best_for": ["profiles", "user_data"],
        "speed": "very_fast",
        "rating": 4.7,
        "url": "https://apify.com/apidojo/twitter-user-scraper"
    },
    {
        "name": "Twitter Thread Scraper",
        "platform": "twitter",
        "price_per_1k": 2.0,
        "auth_required": False,
        "best_for": ["threads", "conversations"],
        "speed": "medium",
        "rating": 4.5,
        "url": "https://apify.com/yellowchimp/twitterx"
    },
    {
        "name": "TikTok Video Downloader",
        "platform": "tiktok",
        "price_per_1k": 2.0,
        "auth_required": False,
        "best_for": ["video_download", "no_watermark"],
        "speed": "very_fast",
        "rating": 4.8,
        "url": "https://apify.com/scrapearchitect/tiktok-video-audio-mp3-downloader"
    },
    {
        "name": "TikTok Profile Scraper (Pay Per Result)",
        "platform": "tiktok",
        "price_per_1k": 0.30,
        "auth_required": False,
        "best_for": ["profiles", "bulk"],
        "speed": "very_fast",
        "rating": 4.9,
        "url": "https://apify.com/apidojo/tiktok-profile-scraper"
    },
    {
        "name": "TikTok Comments Scraper",
        "platform": "tiktok",
        "price_per_1k": 0.30,
        "auth_required": False,
        "best_for": ["comments", "engagement"],
        "speed": "very_fast",
        "rating": 4.7,
        "url": "https://apify.com/apidojo/tiktok-comments-scraper"
    },
    {
        "name": "TikTok Transcriber",
        "platform": "tiktok",
        "price_per_1k": 5.0,
        "auth_required": False,
        "best_for": ["transcripts", "ai_analysis"],
        "speed": "medium",
        "rating": 4.6,
        "url": "https://apify.com/ingeniela/tiktok-video-transcriber"
    },
    {
        "name": "YouTube Scraper (Pay Per Result)",
        "platform": "youtube",
        "price_per_1k": 0.40,
        "auth_required": False,
        "best_for": ["videos", "channels", "search"],
        "speed": "very_fast",
        "rating": 4.8,
        "url": "https://apify.com/apidojo/youtube-scraper"
    },
    {
        "name": "YouTube Transcriber",
        "platform": "youtube",
        "price_per_1k": 3.0,
        "auth_required": False,
        "best_for": ["transcripts", "subtitles"],
        "speed": "medium",
        "rating": 4.7,
        "url": "https://apify.com/agentx/youtube-video-transcriber"
    },
    {
        "name": "YouTube Channel Scraper",
        "platform": "youtube",
        "price_per_1k": 0.40,
        "auth_required": False,
        "best_for": ["channel_data", "bulk_videos"],
        "speed": "very_fast",
        "rating": 4.6,
        "url": "https://apify.com/apidojo/youtube-channel-scraper"
    },
    {
        "name": "Facebook Video Downloader",
        "platform": "facebook",
        "price_per_1k": 3.0,
        "auth_required": False,
        "best_for": ["videos", "downloads"],
        "speed": "medium",
        "rating": 4.5,
        "url": "https://apify.com/scrapearchitect/facebook-video-downloader"
    },
    {
        "name": "Telegram Group Members",
        "platform": "telegram",
        "price_per_1k": 5.0,
        "auth_required": True,
        "best_for": ["members", "groups"],
        "speed": "medium",
        "rating": 4.6,
        "url": "https://apify.com/agentx/telegram-group-members"
    },
    {
        "name": "Reddit Subreddit Scraper",
        "platform": "reddit",
        "price_per_1k": 2.0,
        "auth_required": False,
        "best_for": ["posts", "comments", "subreddits"],
        "speed": "fast",
        "rating": 4.7,
        "url": "https://apify.com/agentx/subreddit-scraper"
    },
    {
        "name": "Leads Generator",
        "platform": "multi",
        "price_per_1k": 3.0,
        "auth_required": False,
        "best_for": ["leads", "emails", "b2b"],
        "speed": "fast",
        "rating": 4.5,
        "url": "https://apify.com/microworlds/leads-generator"
    },
    {
        "name": "Social Media Trend Scraper",
        "platform": "multi",
        "price_per_1k": 10.0,
        "auth_required": False,
        "best_for": ["trends", "analytics", "6_platforms"],
        "speed": "medium",
        "rating": 4.8,
        "url": "https://apify.com/manju4k/social-media-trend-scraper-6-in-1-ai-analysis"
    }
]


def search_apis(
    platform: str = None,
    keyword: str = None,
    max_price: float = None,
    min_rating: float = None,
    auth_required: bool = None,
    limit: int = 10
) -> List[Dict]:
    """Search and filter APIs based on criteria"""
    
    results = APIS.copy()
    
    # Filter by platform
    if platform:
        platform = platform.lower()
        results = [api for api in results if api["platform"] == platform]
    
    # Filter by keyword (search in name and best_for)
    if keyword:
        keyword = keyword.lower()
        results = [
            api for api in results
            if keyword in api["name"].lower()
            or any(keyword in use.lower() for use in api["best_for"])
        ]
    
    # Filter by max price
    if max_price:
        results = [api for api in results if api["price_per_1k"] <= max_price]
    
    # Filter by min rating
    if min_rating:
        results = [api for api in results if api["rating"] >= min_rating]
    
    # Filter by auth requirement
    if auth_required is not None:
        results = [api for api in results if api["auth_required"] == auth_required]
    
    # Sort by rating (descending)
    results.sort(key=lambda x: x["rating"], reverse=True)
    
    return results[:limit]


def display_results(results: List[Dict]):
    """Display search results in a formatted table"""
    
    if not results:
        print("\n❌ No APIs found matching your criteria.")
        return
    
    print(f"\n✅ Found {len(results)} API(s):\n")
    print("-" * 120)
    print(f"{'Platform':<12} {'Name':<35} {'Price/1K':<10} {'Auth':<6} {'Rating':<8} {'Best For'}")
    print("-" * 120)
    
    for api in results:
        auth = "Yes" if api["auth_required"] else "No"
        best_for = ", ".join(api["best_for"][:2])
        print(f"{api['platform']:<12} {api['name'][:34]:<35} ${api['price_per_1k']:<9.2f} {auth:<6} ⭐{api['rating']:<6.1f} {best_for}")
    
    print("-" * 120)
    print("\n💡 Tip: Use --url flag to get full URLs for any API")


def display_details(results: List[Dict]):
    """Display detailed information about each API"""
    
    for i, api in enumerate(results, 1):
        print(f"\n{'='*80}")
        print(f"{i}. {api['name']}")
        print(f"{'='*80}")
        print(f"   Platform:     {api['platform'].capitalize()}")
        print(f"   Price:        ${api['price_per_1k']}/1,000 requests")
        print(f"   Auth Required: {'Yes' if api['auth_required'] else 'No'}")
        print(f"   Rating:       ⭐ {api['rating']}/5.0")
        print(f"   Speed:        {api['speed'].replace('_', ' ').title()}")
        print(f"   Best For:     {', '.join(api['best_for'])}")
        print(f"   URL:          {api['url']}")


def main():
    parser = argparse.ArgumentParser(
        description="Search and filter Social Media Scraping APIs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python search_apis.py --platform linkedin
  python search_apis.py --keyword "video"
  python search_apis.py --max-price 1.0
  python search_apis.py --platform instagram --keyword "followers"
  python search_apis.py --min-rating 4.7 --limit 5
  python search_apis.py --no-auth --max-price 2.0
        """
    )
    
    parser.add_argument("--platform", "-p", 
                        choices=["linkedin", "instagram", "twitter", "tiktok", "youtube", "facebook", "telegram", "reddit", "multi"],
                        help="Filter by platform")
    
    parser.add_argument("--keyword", "-k",
                        help="Search by keyword (name or use case)")
    
    parser.add_argument("--max-price", "-m", type=float,
                        help="Maximum price per 1K requests")
    
    parser.add_argument("--min-rating", "-r", type=float,
                        help="Minimum rating (0-5)")
    
    parser.add_argument("--auth", action="store_true",
                        help="Show only APIs requiring authentication")
    
    parser.add_argument("--no-auth", action="store_true",
                        help="Show only APIs NOT requiring authentication")
    
    parser.add_argument("--limit", "-l", type=int, default=10,
                        help="Maximum results to show (default: 10)")
    
    parser.add_argument("--details", "-d", action="store_true",
                        help="Show detailed information")
    
    args = parser.parse_args()
    
    # Determine auth filter
    auth_required = None
    if args.auth:
        auth_required = True
    elif args.no_auth:
        auth_required = False
    
    # Search APIs
    results = search_apis(
        platform=args.platform,
        keyword=args.keyword,
        max_price=args.max_price,
        min_rating=args.min_rating,
        auth_required=auth_required,
        limit=args.limit
    )
    
    # Display results
    if args.details:
        display_details(results)
    else:
        display_results(results)
    
    print(f"\n📊 Total APIs in database: {len(APIS)} (Full collection: 3,268)")
    print("💡 See COMPARISON.md for detailed comparisons")


if __name__ == "__main__":
    main()
