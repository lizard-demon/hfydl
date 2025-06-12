#!/usr/bin/env python3

import re
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import pypandoc
from pathlib import Path
import tempfile
import os
import argparse
import sys

# --- Constants ---
HEADERS = {'User-Agent': 'HFY-Navigator'}
NEXT_RE = re.compile(r'\bnext\b', re.I)

DEFAULT_CSS = """
body { font-family: sans-serif; line-height: 1.6; margin: 5%; font-size: 1.05em; color: #111; background: #fff; }
h1, h2, h3 { font-weight: 600; color: #222; margin-top: 2em; margin-bottom: 0.5em; }
h1 { font-size: 1.6em; border-bottom: 1px solid #ccc; padding-bottom: 0.3em; }
em { color: #555; font-style: italic; }
p { margin: 1em 0; }
"""

# --- Terminal Output Helpers ---
def say(msg): print(f"• {msg}")
def warn(msg): print(f"⚠️ {msg}", file=sys.stderr)
def done(msg): print(f"✔️ {msg}")
def info(msg): print(f"→ {msg}")

# --- Core Logic ---
def crawl_hfy_story(start_url):
    visited = set()
    sequence = []
    step = 1

    def next_link(url):
        html = requests.get(url, headers=HEADERS).text
        soup = BeautifulSoup(html, 'html.parser')
        visited.add(url)

        for a in soup.find_all('a', href=True):
            if NEXT_RE.search(a.text):
                full = urljoin(url, a['href'])
                if full not in visited:
                    return full

        for c in soup.select('div[data-testid="comment"]'):
            author = c.select_one('[data-testid="comment_author_link"]')
            if author and 'OP' in author.text.upper():
                for a in c.find_all('a', href=True):
                    if NEXT_RE.search(a.text):
                        full = urljoin(url, a['href'])
                        if full not in visited:
                            return full
        return None

    say("Crawling story chain:")
    while start_url:
        info(f"[{step}] {start_url}")
        sequence.append(start_url)
        start_url = next_link(start_url)
        step += 1

    done(f"Found {len(sequence)} post(s).")
    return '\n'.join(sequence)

def reddit_ebook(
    urls_text, output_file="reddit.epub",
    title="Title",
    author="Author",
    cover_image=None
):
    urls = [u.strip() for u in urls_text.splitlines() if u.strip()]
    posts = []

    say(f"Downloading {len(urls)} Reddit post(s)...")

    for i, url in enumerate(urls, 1):
        jurl = url.rstrip('/') + '/.json'
        try:
            data = requests.get(jurl, headers=HEADERS).json()
            post = data[0]['data']['children'][0]['data']
            title_ = post.get('title', f'Post {i}')
            author_ = post.get('author', 'unknown')
            body = post.get('selftext', '').strip()
            if body:
                info(f"✓ {title_} (u/{author_})")
                posts.append(f"# {title_}\n\n*by u/{author_}*\n\n{body}")
            else:
                warn(f"Skipped (empty): {url}")
        except Exception as e:
            warn(f"Error parsing {url}: {e}")

    if not posts:
        warn("No valid posts found.")
        return

    full_md = "\n\n\\newpage\n\n".join(posts)

    say("Converting to EPUB...")
    with tempfile.TemporaryDirectory() as tmpdir:
        md_path = os.path.join(tmpdir, "input.md")
        css_path = os.path.join(tmpdir, "style.css")

        Path(md_path).write_text(full_md, encoding='utf-8')
        Path(css_path).write_text(DEFAULT_CSS)

        args = [
            f'--metadata=title:{title}',
            f'--metadata=author:{author}',
            '--toc', '--toc-depth=2',
            '--css=style.css',
            '--split-level=1'  # ← replaces deprecated --epub-chapter-level
        ]

        if cover_image and Path(cover_image).exists():
            args.append(f'--epub-cover-image={cover_image}')

        pypandoc.convert_file(md_path, to='epub', outputfile=output_file, extra_args=args)

    done(f"EPUB saved: {output_file}")

# --- CLI Interface ---
def main():
    parser = argparse.ArgumentParser(
        description="📘 Convert a chain of HFY Reddit posts into a clean EPUB file."
    )
    parser.add_argument("url", help="Starting Reddit post URL (e.g. https://old.reddit.com/r/HFY/...)")
    parser.add_argument("-o", "--output", default="story.epub", help="Output EPUB file")
    parser.add_argument("-t", "--title", default="Title", help="Title for the ebook")
    parser.add_argument("-a", "--author", default="Author", help="Author name")
    parser.add_argument("-c", "--cover", help="Optional cover image (path to file)")
    args = parser.parse_args()

    links = crawl_hfy_story(args.url)
    reddit_ebook(
        links,
        output_file=args.output,
        title=args.title,
        author=args.author,
        cover_image=args.cover
    )

if __name__ == "__main__":
    main()
