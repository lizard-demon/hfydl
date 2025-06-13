#!/usr/bin/env python3

#!/usr/bin/env python3

import os, re, json, sys, argparse, tempfile, subprocess
from pathlib import Path
from urllib.parse import urljoin, urldefrag
import requests, numpy as np
import pypandoc
from bs4 import BeautifulSoup
from model2vec import StaticModel

HEADERS = {'User-Agent': 'HFY-Navigator'}
model = StaticModel.from_pretrained("minishlab/potion-base-8M")


def say(msg): print(f"• {msg}")
def info(msg): print(f"→ {msg}")
def warn(msg): print(f"⚠️ {msg}", file=sys.stderr)
def done(msg): print(f"✔️ {msg}")
def norm(u): return urldefrag(u)[0].rstrip('/')
def cosine(a, b): return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
def slug(s): return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def fetch(url):
    try:
        html = requests.get(url, headers=HEADERS, timeout=10).text
        soup = BeautifulSoup(html, 'html.parser')
        return soup, soup.select_one('a[href^="/user/"]')
    except requests.RequestException as e:
        warn(f"Failed to fetch {url}: {e}")
        return BeautifulSoup("", "html.parser"), None


def crawl(seed, temperature=0.5):
    visited, chain, titles, vecs = set(), [], [], []
    op = None

    def links(url, title=None):
        soup, op_a = fetch(url)
        nonlocal op
        if not op and op_a:
            op = op_a.text.strip()
        result = []
        for a in soup.select('a[href]'):
            href = norm(urljoin(url, a['href']))
            t = a.text.strip()
            if not t or len(t) > 120 or 'comments' not in href or href in visited:
                continue
            try:
                v = model.encode([t])[0]
                avg = np.mean(vecs, axis=0) if vecs else v
                if titles and cosine(v, avg) < temperature:
                    warn(f"↓ Skipping (too different): {t}")
                    continue
                result.append((href, t, v))
            except Exception as e:
                warn(f"Encoding error on '{t}': {e}")
        return result

    def walk(url, t=None, d=0):
        url = norm(url)
        if url in visited:
            return
        visited.add(url)
        info(f"[{d+1}] {url}")
        chain.append(url)
        if t:
            try:
                v = model.encode([t])[0]
                titles.append(t)
                vecs.append(v)
            except Exception as e:
                warn(f"Vectorization failed: {e}")
        for href, t, _ in links(url, t):
            walk(href, t, d + 1)
            break

    say("Crawling story chain:")
    walk(seed)
    done(f"Found {len(chain)} post(s).")
    return chain


def fetch_posts(urls):
    all, titles, authors = [], [], []
    for u in urls:
        try:
            j = requests.get(u + "/.json", headers=HEADERS, timeout=10).json()
            post = j[0]['data']['children'][0]['data']
            t, b, a = post['title'], post['selftext'].strip(), post['author']
            if b:
                info(f"✓ {t} (u/{a})")
                titles.append(t)
                authors.append(a)
                all.append((t, a, b))
            else:
                warn(f"Empty post: {u}")
        except (requests.RequestException, KeyError, IndexError, json.JSONDecodeError) as e:
            warn(f"Error parsing {u}: {e}")
    return all, titles, max(set(authors), key=authors.count) if authors else "Anonymous"


def prefix(words):
    split = [re.findall(r'\w+', w.lower()) for w in words]
    if not split:
        return "Untitled"
    first = split[0]
    for i, w in enumerate(first):
        if any(len(s) <= i or s[i] != w for s in split):
            return " ".join(first[:i]).title() or "Untitled"
    return " ".join(first).title()


def write_md(posts, title, author, path):
    md = "\n\n\\newpage\n\n".join(f"# {t}\n\n*by u/{a}*\n\n{b}" for t, a, b in posts)
    Path(path).write_text(md, encoding='utf-8')
    done(f"Markdown: {path}")


def write_json(posts, title, author, path):
    doc = {
        "title": title,
        "author": author,
        "chapters": [{"title": t, "author": a, "body": b} for t, a, b in posts]
    }
    Path(path).write_text(json.dumps(doc, indent=2), encoding='utf-8')
    done(f"JSON: {path}")


def convert(posts, title, author, fmt, out, cover=None):
    if fmt in ("markdown", "md"):
        return write_md(posts, title, author, out)
    if fmt == "json":
        return write_json(posts, title, author, out)

    md = "\n\n\\newpage\n\n".join(f"# {t}\n\n*by u/{a}*\n\n{b}" for t, a, b in posts)
    css = "body { font-family: serif; margin: 5%; line-height: 1.6; }"
    with tempfile.TemporaryDirectory() as tmp:
        Path(tmp, "in.md").write_text(md, encoding='utf-8')
        Path(tmp, "style.css").write_text(css)
        args = [
            f"--metadata=title:{title}",
            f"--metadata=author:{author}",
            "--toc", "--toc-depth=2", "--css=style.css", "--split-level=1"
        ]
        if fmt == "epub" and cover:
            args.append(f"--epub-cover-image={cover}")
        try:
            pypandoc.convert_file(Path(tmp, "in.md"), fmt, outputfile=os.path.abspath(out), extra_args=args, cworkdir=tmp)
            done(f"{fmt.upper()}: {out}")
        except RuntimeError as e:
            warn(f"Conversion failed: {e}")
            sys.exit(1)


def edit(path):
    try:
        subprocess.run([os.environ.get("EDITOR", "nano" if os.name != "nt" else "notepad"), path])
    except Exception as e:
        warn(f"Editor failed: {e}")


def main():
    a = argparse.ArgumentParser(description="📘 Reddit story chain to EPUB/MD/JSON/PDF/etc")
    a.add_argument("url", nargs="?", help="Starting Reddit URL")
    a.add_argument("--edit", action="store_true", help="Edit URL list before export")
    a.add_argument("--crawl-only", metavar="FILE", help="Save crawl list to file")
    a.add_argument("--from-list", metavar="FILE", help="Read URLs from file")
    a.add_argument("--format", default="epub", help="Output format: epub, pdf, markdown, json, html, docx, odt...")
    a.add_argument("--cover", help="Optional cover image")
    a.add_argument("--temperature", type=float, default=0.5, help="Similarity temperature (0.0–1.0)")
    args = a.parse_args()

    if args.from_list:
        urls = Path(args.from_list).read_text().splitlines()
    elif args.url:
        urls = crawl(args.url, temperature=args.temperature)
        if args.crawl_only:
            Path(args.crawl_only).write_text("\n".join(urls))
            done(f"Saved to {args.crawl_only}")
            return
    else:
        a.error("Provide a Reddit URL or --from-list")

    if args.edit:
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".txt") as f:
            f.write("\n".join(urls))
            f.flush()
            edit(f.name)
            urls = Path(f.name).read_text().splitlines()

    posts, titles, author = fetch_posts(urls)
    title = prefix(titles)
    ext = "json" if args.format == "json" else "md" if "md" in args.format else args.format
    out = slug(title) + f".{ext}"
    convert(posts, title, author, args.format, out, cover=args.cover)


os.environ["TOKENIZERS_PARALLELISM"] = "false"

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        warn("Interrupted by user.")
        sys.exit(130)
    except Exception as e:
        warn(f"Unhandled error: {e.__class__.__name__}: {e}")
        sys.exit(1)

