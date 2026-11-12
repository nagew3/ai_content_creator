#!/usr/bin/env python3
"""
run_daily.py — Process quotidien machine à contenu LinkedIn
Exécuté par Claude Code chaque matin à 7h via tâche programmée.

Ce script est l'orchestrateur technique. Claude Code reste le cerveau
qui lit les fichiers, analyse les signaux et génère les posts.
"""

import os
import json
import datetime
import feedparser
import praw
import requests
from pathlib import Path
from dotenv import load_dotenv

# ── Config ─────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).parent
load_dotenv(ROOT / "config.env")

TODAY = datetime.date.today().isoformat()
CACHE_DIR = ROOT / "cache" / TODAY
LOG_FILE = ROOT / "logs" / "run.log"


# ── Helpers ────────────────────────────────────────────────────────────────────

def log(message: str, ok: bool = True):
    prefix = "✓" if ok else "✗"
    line = f"[{TODAY} {datetime.datetime.now().strftime('%H:%M')}] {prefix} {message}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def load_source_lines(filename: str) -> list[str]:
    """Retourne les lignes non-vides et non-commentées d'un fichier source."""
    path = ROOT / "sources" / filename
    if not path.exists():
        return []
    lines = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            lines.append(line)
    return lines


def cache_exists() -> bool:
    return CACHE_DIR.exists() and any(CACHE_DIR.iterdir())


def save_cache(name: str, data):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / f"{name}.json"
    with open(path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_cache(name: str) -> list | dict | None:
    path = CACHE_DIR / f"{name}.json"
    if path.exists():
        return json.loads(path.read_text())
    return None


# ── Étape 1 : Veille ──────────────────────────────────────────────────────────

def scrape_rss() -> list[dict]:
    """Récupère les articles des dernières 24h depuis les flux RSS."""
    feeds = load_source_lines("rss_feeds.txt")
    cutoff = datetime.datetime.now() - datetime.timedelta(hours=24)
    articles = []

    for url in feeds:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                published = entry.get("published_parsed")
                if published:
                    pub_dt = datetime.datetime(*published[:6])
                    if pub_dt < cutoff:
                        continue
                articles.append({
                    "source": "rss",
                    "feed": url,
                    "title": entry.get("title", ""),
                    "summary": entry.get("summary", "")[:300],
                    "url": entry.get("link", ""),
                    "date": entry.get("published", ""),
                })
        except Exception as e:
            log(f"ERREUR RSS {url} : {e}", ok=False)

    log(f"RSS — {len(articles)} articles récupérés")
    return articles


def scrape_reddit() -> list[dict]:
    """Récupère les top posts de la semaine sur les subreddits configurés."""
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT", "linkedin-content-bot/1.0")

    if not client_id or not client_secret:
        log("ERREUR Reddit : clés API manquantes dans config.env", ok=False)
        return []

    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
        )

        lines = load_source_lines("reddit_targets.txt")
        subreddits = [l for l in lines if l.startswith("r/")]
        keywords = [l.replace("keyword:", "") for l in lines if l.startswith("keyword:")]

        posts = []

        for sub in subreddits:
            try:
                for post in reddit.subreddit(sub[2:]).top(time_filter="week", limit=10):
                    top_comments = []
                    post.comments.replace_more(limit=0)
                    for comment in list(post.comments)[:5]:
                        top_comments.append(comment.body[:200])

                    posts.append({
                        "source": "reddit",
                        "subreddit": sub,
                        "title": post.title,
                        "text": post.selftext[:300],
                        "score": post.score,
                        "num_comments": post.num_comments,
                        "url": post.url,
                        "top_comments": top_comments,
                    })
            except Exception as e:
                log(f"ERREUR Reddit {sub} : {e}", ok=False)

        log(f"Reddit — {len(posts)} posts récupérés")
        return posts

    except Exception as e:
        log(f"ERREUR Reddit (init) : {e}", ok=False)
        return []


def scrape_twitter() -> list[dict]:
    """Récupère les tweets des comptes et mots-clés configurés."""
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
    if not bearer_token:
        log("ERREUR Twitter : TWITTER_BEARER_TOKEN manquant dans config.env", ok=False)
        return []

    headers = {"Authorization": f"Bearer {bearer_token}"}
    lines = load_source_lines("twitter_accounts.txt")

    handles = [l.split("|")[0].strip() for l in lines if l.startswith("@")]
    keywords = [l.replace("keyword:", "").strip() for l in lines if l.startswith("keyword:")]

    tweets = []

    # Tweets par compte
    for handle in handles:
        username = handle.lstrip("@")
        try:
            # Récupérer l'user ID
            r = requests.get(
                f"https://api.twitter.com/2/users/by/username/{username}",
                headers=headers,
                timeout=10,
            )
            if r.status_code != 200:
                log(f"ERREUR Twitter @{username} : {r.status_code}", ok=False)
                continue
            user_id = r.json()["data"]["id"]

            # Récupérer les 20 derniers tweets
            r = requests.get(
                f"https://api.twitter.com/2/users/{user_id}/tweets",
                headers=headers,
                params={
                    "max_results": 20,
                    "tweet.fields": "public_metrics,created_at",
                    "start_time": (datetime.datetime.utcnow() - datetime.timedelta(days=7)).isoformat() + "Z",
                },
                timeout=10,
            )
            if r.status_code == 200:
                for tweet in r.json().get("data", []):
                    metrics = tweet.get("public_metrics", {})
                    tweets.append({
                        "source": "twitter",
                        "account": handle,
                        "text": tweet["text"],
                        "likes": metrics.get("like_count", 0),
                        "retweets": metrics.get("retweet_count", 0),
                        "replies": metrics.get("reply_count", 0),
                        "date": tweet.get("created_at", ""),
                    })
        except Exception as e:
            log(f"ERREUR Twitter @{username} : {e}", ok=False)

    # Recherche par mots-clés
    for kw in keywords:
        try:
            query = f"{kw} lang:fr -is:retweet"
            r = requests.get(
                "https://api.twitter.com/2/tweets/search/recent",
                headers=headers,
                params={
                    "query": query,
                    "max_results": 20,
                    "tweet.fields": "public_metrics,created_at",
                },
                timeout=10,
            )
            if r.status_code == 200:
                for tweet in r.json().get("data", []):
                    metrics = tweet.get("public_metrics", {})
                    tweets.append({
                        "source": "twitter",
                        "keyword": kw,
                        "text": tweet["text"],
                        "likes": metrics.get("like_count", 0),
                        "retweets": metrics.get("retweet_count", 0),
                        "replies": metrics.get("reply_count", 0),
                        "date": tweet.get("created_at", ""),
                    })
        except Exception as e:
            log(f"ERREUR Twitter keyword '{kw}' : {e}", ok=False)

    # Trier par engagement
    tweets.sort(key=lambda t: t.get("likes", 0) + t.get("retweets", 0) * 2, reverse=True)

    log(f"Twitter — {len(tweets)} tweets récupérés")
    return tweets


def scrape_linkedin_via_apify() -> list[dict]:
    """Récupère les derniers posts LinkedIn via Apify."""
    apify_token = os.getenv("APIFY_TOKEN")
    if not apify_token:
        log("ERREUR LinkedIn/Apify : APIFY_TOKEN manquant dans config.env", ok=False)
        return []

    targets = load_source_lines("linkedin_targets.txt")
    profile_urls = [l.split("|")[0].strip() for l in targets]

    if not profile_urls:
        log("LinkedIn — aucun profil configuré dans linkedin_targets.txt")
        return []

    try:
        # Lancer l'actor Apify
        run_url = f"https://api.apify.com/v2/acts/johnvc~linkedin-posts-api/runs"
        r = requests.post(
            run_url,
            headers={"Authorization": f"Bearer {apify_token}"},
            json={
                "profileUrls": profile_urls,
                "maxPostsPerProfile": 10,
            },
            timeout=30,
        )

        if r.status_code not in (200, 201):
            log(f"ERREUR LinkedIn/Apify : {r.status_code} — {r.text[:200]}", ok=False)
            return []

        run_id = r.json()["data"]["id"]

        # Attendre la fin du run (polling simple)
        import time
        for _ in range(30):
            time.sleep(5)
            status_r = requests.get(
                f"https://api.apify.com/v2/actor-runs/{run_id}",
                headers={"Authorization": f"Bearer {apify_token}"},
                timeout=10,
            )
            if status_r.json()["data"]["status"] in ("SUCCEEDED", "FAILED", "ABORTED"):
                break

        # Récupérer les résultats
        dataset_id = status_r.json()["data"]["defaultDatasetId"]
        items_r = requests.get(
            f"https://api.apify.com/v2/datasets/{dataset_id}/items",
            headers={"Authorization": f"Bearer {apify_token}"},
            timeout=15,
        )

        posts = []
        for item in items_r.json():
            # Ignorer les lignes d'erreur et d'avis, garder seulement les posts
            if item.get("result_type") != "post":
                continue
            posts.append({
                "source": "linkedin",
                "profile": item.get("authorUrl", ""),
                "text": item.get("text", "")[:400],
                "likes": item.get("numLikes", 0),
                "comments": item.get("numComments", 0),
                "date": item.get("datePosted", ""),
            })

        log(f"LinkedIn — {len(posts)} posts récupérés")
        return posts

    except Exception as e:
        log(f"ERREUR LinkedIn/Apify : {e}", ok=False)
        return []


# ── Étape 1 (suite) : YouTube via yt-dlp ─────────────────────────────────────

def scrape_youtube() -> list[dict]:
    """Récupère titres, descriptions et engagement des dernières vidéos via yt-dlp."""
    import subprocess

    lines = load_source_lines("youtube_channels.txt")
    channel_urls = [l.split("|")[0].strip() for l in lines]

    if not channel_urls:
        log("YouTube — aucune chaîne configurée dans youtube_channels.txt")
        return []

    videos = []

    for url in channel_urls:
        try:
            cmd = [
                "yt-dlp",
                "--flat-playlist",
                "--playlist-items", "1-10",
                "--print", '{"title": %(title)j, "url": "https://youtu.be/%(id)s", "views": %(view_count)s, "description": %(description)j}',
                "--no-warnings",
                url,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            for line in result.stdout.splitlines():
                try:
                    video = json.loads(line)
                    video["source"] = "youtube"
                    video["channel"] = url
                    videos.append(video)
                except json.JSONDecodeError:
                    pass

        except Exception as e:
            log(f"ERREUR YouTube {url} : {e}", ok=False)

    log(f"YouTube — {len(videos)} vidéos récupérées")
    return videos


# ── Main ───────────────────────────────────────────────────────────────────────

def run():
    log("═══ Début du process quotidien ═══")

    # Cache déjà présent → on skip le scraping
    if cache_exists():
        log("Cache existant détecté — scraping ignoré, utilisation du cache")
        return load_all_from_cache()

    # Scraping de toutes les sources
    rss_data = scrape_rss()
    reddit_data = scrape_reddit()
    twitter_data = scrape_twitter()
    linkedin_data = scrape_linkedin_via_apify()
    youtube_data = scrape_youtube()

    # Sauvegarde du cache
    save_cache("rss_raw", rss_data)
    save_cache("reddit_raw", reddit_data)
    save_cache("twitter_raw", twitter_data)
    save_cache("linkedin_raw", linkedin_data)
    save_cache("youtube_raw", youtube_data)

    total = len(rss_data) + len(reddit_data) + len(twitter_data) + len(linkedin_data) + len(youtube_data)
    log(f"Veille OK — {total} signaux bruts collectés au total")

    return {
        "rss": rss_data,
        "reddit": reddit_data,
        "twitter": twitter_data,
        "linkedin": linkedin_data,
        "youtube": youtube_data,
    }


def load_all_from_cache() -> dict:
    return {
        "rss": load_cache("rss_raw") or [],
        "reddit": load_cache("reddit_raw") or [],
        "twitter": load_cache("twitter_raw") or [],
        "linkedin": load_cache("linkedin_raw") or [],
        "youtube": load_cache("youtube_raw") or [],
    }


if __name__ == "__main__":
    data = run()
    total = sum(len(v) for v in data.values())
    print(f"\n→ {total} signaux disponibles dans cache/{TODAY}/")
    print("→ Claude Code peut maintenant analyser les signaux et générer le post.")
