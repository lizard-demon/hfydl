#!/usr/bin/env python3
import re
import requests
from urllib.parse import urljoin, urlparse, urldefrag
from bs4 import BeautifulSoup
import pypandoc
from pathlib import Path
import tempfile
import os
import argparse
import sys
from model2vec import StaticModel
import numpy as np

# --- Constants ---
HEADERS = {'User-Agent': 'HFY-Navigator'}
NEXT_RE = re.compile(r'\bnext\b|\bpart\b', re.I)
NUM_RE = re.compile(r'\b(\d{1,3})\b')
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

# --- Cosine Similarity ---
def cosine_similarity(a, b):
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# --- Normalize URL: Remove fragment and trailing slash ---
def normalize_url(url):
    url, _ = urldefrag(url)
    return url.rstrip('/')

# --- Load Model2Vec Model Once ---
model = StaticModel.from_pretrained("minishlab/potion-base-8M")

# --- Heuristic Recursive Crawler ---
def crawl_hfy_story(start_url, max_depth=15):
    visited = set()
    sequence = []
    op_author = [None]

    def score(title, author, sub, last_title, last_sub, last_num):
        s = 0
        if author == op_author[0]:
            s += 3
        if sub == last_sub:
            s += 1
        if last_title:
            try:
                emb1 = model.encode([title])[0]
                emb2 = model.encode([last_title])[0]
                if cosine_similarity(emb1, emb2) > 0.8:
                    s += 2
            except Exception as e:
                warn(f"Similarity error: {e}")
        if (m := NUM_RE.search(title)):
            n = int(m.group(1))
            if last_num is not None and n == last_num + 1:
                s += 2
        return s

    def get_links(url, last_title, last_sub, last_num):
        html = requests.get(url, headers=HEADERS).text
        soup = BeautifulSoup(html, 'html.parser')
        if not op_author[0]:
            a = soup.select_one('a[href^="/user/"]')
            if a:
                op_author[0] = a.text.strip()
        links = []
        base = urlparse(url)
        for a in soup.select('a[href]'):
            href = normalize_url(urljoin(url, a['href']))
            if href in visited or 'comments' not in href:
                continue
            title = a.text.strip()
            if not title or len(title) > 120:
                continue
            author = a.get('data-click-id') or op_author[0]
            sub = urlparse(href).path.split('/')[2] if '/r/' in href else base.path.split('/')[2]
            score_val = score(title, author, sub, last_title, last_sub, last_num)
            if score_val:
                links.append((score_val, href, title, sub))
        return sorted(links, key=lambda x: -x[0])

    def walk(url, depth=0, last_title=None, last_num=None):
        if depth > max_depth:
            return
        url = normalize_url(url)
        if url in visited:
            return
        visited.add(url)
        info(f"[{depth+1}] {url}")
        sequence.append(url)
        candidates = get_links(url, last_title, urlparse(url).path.split('/')[2], last_num)
        for _, href, title, sub in candidates:
            num = int(NUM_RE.search(title).group(1)) if NUM_RE.search(title) else None
            return walk(href, depth+1, title, num)

    say("Crawling story chain:")
    walk(start_url)
    done(f"Found {len(sequence)} post(s).")
    return '\n'.join(sequence)

# --- EPUB Generator ---
def reddit_ebook(
    urls_text, output_file="reddit.epub",
    title="Title",
    author="Author",
    cover_image=None
):
    urls = [normalize_url(u.strip()) for u in urls_text.splitlines() if u.strip()]
    posts = []
    say(f"Downloading {len(urls)} Reddit post(s)...")
    for i, url in enumerate(urls, 1):
        jurl = url + '/.json'
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
            '--split-level=1'
        ]
        if cover_image and Path(cover_image).exists():
            args.append(f'--epub-cover-image={cover_image}')
        pypandoc.convert_file(md_path, to='epub', outputfile=os.path.abspath(output_file), extra_args=args, cworkdir=tmpdir)
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

os.environ["TOKENIZERS_PARALLELISM"] = "false"
if __name__ == "__main__":
    main()

