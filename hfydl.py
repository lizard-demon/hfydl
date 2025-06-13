#!/usr/bin/env python3

import re, requests, argparse, os, sys, tempfile, subprocess, json
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urldefrag
from pathlib import Path
import pypandoc, numpy as np
from model2vec import StaticModel

say = lambda m: print(f"• {m}")
warn = lambda m: print(f"⚠️ {m}", file=sys.stderr)
done = lambda m: print(f"✔️ {m}")
info = lambda m: print(f"→ {m}")
normalize = lambda u: urldefrag(u)[0].rstrip('/')
HEADERS = {'User-Agent': 'HFY-Navigator'}
model = StaticModel.from_pretrained("minishlab/potion-base-8M")

def cosine(a, b): return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def crawl(start_url):
    visited, sequence, titles, vectors = set(), [], [], []
    op_author = None
    sim_threshold = 0.72
    def get_links(url, last_title):
        nonlocal op_author
        html = requests.get(url, headers=HEADERS).text
        soup = BeautifulSoup(html, 'html.parser')
        if not op_author:
            a = soup.select_one('a[href^="/user/"]')
            if a: op_author = a.text.strip()
        links = []
        for a in soup.select('a[href]'):
            href = normalize(urljoin(url, a['href']))
            if href in visited or 'comments' not in href: continue
            title = a.text.strip()
            if not title or len(title) > 120: continue
            try:
                vec = model.encode([title])[0]
                if len(titles) >= 3:
                    avg = np.mean(vectors, axis=0)
                    if cosine(vec, avg) < sim_threshold:
                        warn(f"↓ Skipping (too different): {title}")
                        continue
                links.append((href, title, vec))
            except: pass
        return links
    def walk(url, depth=0, last_title=None):
        url = normalize(url)
        if url in visited: return
        visited.add(url)
        info(f"[{depth+1}] {url}")
        sequence.append(url)
        if last_title:
            try:
                vec = model.encode([last_title])[0]
                titles.append(last_title)
                vectors.append(vec)
            except: pass
        for href, title, _ in get_links(url, last_title):
            walk(href, depth+1, title)
            break
    say("Crawling story chain:")
    walk(start_url)
    done(f"Found {len(sequence)} post(s).")
    return sequence

def download_posts(urls):
    posts, all_titles, all_authors = [], [], []
    for u in urls:
        try:
            j = requests.get(u + "/.json", headers=HEADERS).json()
            post = j[0]['data']['children'][0]['data']
            title, body = post['title'], post['selftext'].strip()
            author = post['author']
            if body:
                all_titles.append(title)
                all_authors.append(author)
                posts.append((title, author, body))
                info(f"✓ {title} (u/{author})")
            else: warn(f"Skipped (empty): {u}")
        except Exception as e:
            warn(f"Failed {u}: {e}")
    return posts, all_titles, most_common(all_authors)

def common_prefix(tokens_list):
    if not tokens_list: return ""
    prefix = tokens_list[0]
    for tokens in tokens_list[1:]:
        i = 0
        while i < len(prefix) and i < len(tokens) and prefix[i] == tokens[i]:
            i += 1
        prefix = prefix[:i]
    return " ".join(prefix).strip()

def most_common(items):
    return max(set(items), key=items.count) if items else "Anonymous"

def guess_title(titles):
    token_lists = [re.findall(r'\w+', t.lower()) for t in titles]
    prefix = common_prefix(token_lists)
    return prefix.title() if prefix else "Untitled"

def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

def write_markdown(posts, title, author, outname):
    md = "\n\n\\newpage\n\n".join(
        f"# {t}\n\n*by u/{a}*\n\n{b}" for t,a,b in posts
    )
    Path(outname).write_text(md, encoding='utf-8')
    done(f"Saved Markdown: {outname}")

def write_json(posts, title, author, outname):
    data = {
        "title": title,
        "author": author,
        "chapters": [
            {"title": t, "author": a, "body": b} for t,a,b in posts
        ]
    }
    Path(outname).write_text(json.dumps(data, indent=2), encoding='utf-8')
    done(f"Saved JSON: {outname}")

def make_output(posts, title, author, outname, fmt, cover=None):
    if fmt == "markdown":
        return write_markdown(posts, title, author, outname)
    if fmt == "json":
        return write_json(posts, title, author, outname)

    md = "\n\n\\newpage\n\n".join(
        f"# {t}\n\n*by u/{a}*\n\n{b}" for t,a,b in posts
    )
    css = """
    body { font-family: sans-serif; line-height: 1.6; margin: 5%; font-size: 1.05em; color: #111; background: #fff; }
    h1 { font-size: 1.6em; border-bottom: 1px solid #ccc; padding-bottom: 0.3em; }
    em { color: #555; }
    """
    with tempfile.TemporaryDirectory() as tmp:
        Path(tmp, "in.md").write_text(md, encoding='utf-8')
        Path(tmp, "style.css").write_text(css)
        args = [
            f"--metadata=title:{title}",
            f"--metadata=author:{author}",
            "--toc", "--toc-depth=2", "--css=style.css", "--split-level=1"
        ]
        if fmt == "epub" and cover and Path(cover).exists():
            args.append(f"--epub-cover-image={cover}")
        pypandoc.convert_file(
            os.path.join(tmp, "in.md"), to=fmt,
            outputfile=os.path.abspath(outname),
            extra_args=args, cworkdir=tmp
        )
    done(f"Saved {fmt.upper()}: {outname}")

def edit_file(path):
    subprocess.run([os.environ.get("EDITOR", "nano" if os.name != "nt" else "notepad"), path])

def main():
    p = argparse.ArgumentParser(description="📘 Convert Reddit HFY chains into documents")
    p.add_argument("url", nargs="?", help="Starting Reddit post URL")
    p.add_argument("--edit", action="store_true", help="Edit URL list before output")
    p.add_argument("--crawl-only", metavar="FILE", help="Crawl only, save URLs")
    p.add_argument("--from-list", metavar="FILE", help="Build output from URL list")
    p.add_argument("--format", default="epub", help="Output format (epub, pdf, markdown, json, html...)")
    p.add_argument("--cover", help="Optional cover image for EPUB")
    args = p.parse_args()

    if args.from_list:
        urls = Path(args.from_list).read_text().splitlines()
    elif args.url:
        urls = crawl(args.url)
        if args.crawl_only:
            Path(args.crawl_only).write_text("\n".join(urls))
            done(f"Saved to {args.crawl_only}")
            return
    else:
        p.error("Need a starting URL or --from-list")

    if args.edit:
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".txt") as f:
            f.write("\n".join(urls))
            f.flush()
            edit_file(f.name)
            urls = Path(f.name).read_text().splitlines()

    posts, titles, author = download_posts(urls)
    story_title = guess_title(titles)
    ext = "json" if args.format == "json" else "md" if args.format == "markdown" else args.format
    outname = slugify(story_title) + f".{ext}"
    make_output(posts, story_title, author, outname, args.format, cover=args.cover)

os.environ["TOKENIZERS_PARALLELISM"] = "false"
if __name__ == "__main__":
    main()

