Here’s a **modern, elegant, and fully-featured `README.md`** tailored for `hfydl.py`, blending aesthetics, usage instructions, the man page, and showing off the capabilities (including a preview `.gif`):

---

````markdown
# 📘 HFYDL – Reddit HFY Storybook Generator

![example usage](example.gif)

**hfydl** is a smart Reddit crawler that transforms "Humanity, Fuck Yeah" (HFY) stories into beautifully structured eBooks. Using language models and vector similarity, it auto-discovers story chains and exports them into polished formats like **EPUB**, **PDF**, **Markdown**, and **JSON**.

---

## ✨ Features

- 🔗 **Story Chain Discovery**  
  Automatically follows Reddit post chains using semantic similarity.

- 📄 **Clean, Chaptered Output**  
  All stories are saved as readable, paginated chapters.

- 🧠 **Vector Similarity Navigation**  
  Powered by [`minishlab/potion-base-8M`](https://huggingface.co/minishlab/potion-base-8M) for meaningful link selection.

- ✍️ **Editable URL List**  
  Pause and tweak the discovered chain using your `$EDITOR`.

- 🎨 **Export Formats Galore**  
  Output your HFY masterpiece in:
  `epub`, `pdf`, `markdown`, `html`, `docx`, `odt`, `json`, and more (via Pandoc).

- 📚 **Cover Support**  
  Add a cover image to EPUB exports for that final polish.

---

## 🛠️ Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
````

You also need **Pandoc** for format conversion:

```bash
# Debian/Ubuntu
sudo apt install pandoc

# macOS
brew install pandoc

# Windows
choco install pandoc
```

Optional (for PDF export):

```bash
sudo apt install texlive
```

---

## 🚀 Usage

```bash
hfydl [options] [REDDIT_URL]
```

### 🔍 Crawl a Reddit HFY story and export as EPUB:

```bash
hfydl https://www.reddit.com/r/HFY/comments/abc123/story_title
```

### 📜 Use a file of links and export to Markdown:

```bash
hfydl -from-list links.txt -format markdown
```

### 🧪 Save the crawl list without downloading:

```bash
hfydl https://reddit.com/... -crawl-only story.txt
```

### 🖋️ Edit discovered URLs before export:

```bash
hfydl -edit https://reddit.com/...
```

---

## ⚙️ Command-line Options

| Option             | Description                                                           |
| ------------------ | --------------------------------------------------------------------- |
| `-edit`            | Edit the list of discovered URLs before exporting.                    |
| `-crawl-only FILE` | Only crawl and save the URL chain to file (no downloading/exporting). |
| `-from-list FILE`  | Read URLs from a file instead of crawling.                            |
| `-format FORMAT`   | Output format (e.g. `epub`, `pdf`, `markdown`, `json`, `html`, etc.). |
| `-cover IMAGE`     | Optional cover image for EPUB export.                                 |
| `-temperature VAL` | Similarity threshold (0.0–1.0) for following links (default: `0.5`).  |
| `URL`              | Starting Reddit post (if `-from-list` is not used).                   |

---

## 📁 File Structure

| File                  | Description                                |
| --------------------- | ------------------------------------------ |
| `hfydl.py`            | Main crawler and formatter script.         |
| `example.gif`         | Demo of live crawling + output generation. |
| `requirements.txt`    | Python dependencies.                       |
| `~/.cache/model2vec/` | Cached embedding model files.              |

---

## 📄 Man Page Summary

```
NAME
    hfydl – reddit HFY story crawler and formatter

SYNOPSIS
    hfydl [-edit] [-crawl-only FILE] [-from-list FILE]
          [-format FORMAT] [-cover IMAGE] [-temperature VALUE]
          [URL]

DESCRIPTION
    Crawls a Reddit HFY chain and exports it as a storybook in your format
    of choice. Uses vector similarity to follow links that match the
    ongoing narrative.

OPTIONS
    -edit                Edit discovered URL list.
    -crawl-only FILE     Save crawled URLs to file only.
    -from-list FILE      Load URLs from file instead of crawling.
    -format FORMAT       Output type: epub, pdf, markdown, json, etc.
    -cover IMAGE         Add a cover image (epub only).
    -temperature VALUE   Cosine similarity threshold [0.0–1.0].

EXAMPLES
    hfydl https://reddit.com/r/HFY/...     # Crawl and export
    hfydl -from-list urls.txt -format pdf  # Use file, output PDF

AUTHOR
    🦎 Lizard Demon (u/lizrd_demon)
```

---

## 🧠 Behind the Scenes

* **Semantic Crawling**: The crawler uses vector similarity via `model2vec.StaticModel` to decide which Reddit links continue the narrative.
* **Smart Formatting**: Chapters are titled, attributed to authors, and formatted with typographic finesse.
* **Pandoc Power**: Output conversion is handled by [Pandoc](https://pandoc.org), enabling rich, flexible export options.

---

## ❤️ Contribute

Found a cool use case or feature idea?
Open an issue or ping `u/lizrd_demon` on Reddit. PRs welcome!

---

## 📜 License

MIT – Free as in "fuck yeah, humanity."

```

Let me know if you want the README to include badges (e.g. PyPI, license, demo link), or if you want it rendered in a specific theme like GitHub dark/light mode.
```

