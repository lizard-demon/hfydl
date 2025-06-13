# 📘 HFYDL – Reddit Story Downloader [v0.1 *beta*]

`hfydl` is a smart Reddit crawler that transforms "Humanity, Fuck Yeah" (HFY) stories into beautifully structured eBooks.

![example usage](example.gif)


## ✨ Features

- 🔗 **Story Chain Discovery**  
  Using heuristic and semantic embeddings, it attempts to follow a chain of reddit posts with similar titles.

- 🎨 **Export Formats Galore**  
  Output your HFY masterpiece in:
  `epub`, `pdf`, `markdown`, `html`, `docx`, `odt`, `json`, and more (via Pandoc).

- ✍️ **Handcraft the Chapter List**  
  Pause and tweak the post chain using your `$EDITOR`.  

- 📄 **Well Formatted Output**  
  All stories are saved as readable, paginated chapters, with a table of contents.

- 📚 **Cover Support**  
  Add a cover image to EPUB exports for that final polish.

- 💋 **Simple(ish)**  
  Only ~220 lines of python... Well as simple as you can make something like this.

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

Make it executable:
```bash
sudo chmod +x hfydl
```

---

## 🚀 Usage

```bash
./hfydl [options] [REDDIT_URL]
```

***🔍 Crawl a Reddit HFY story and export as EPUB:***

```bash
./hfydl "https://www.reddit.com/r/HFY/comments/abc123/story_title"
```

***📜 Use a file of links and export to Markdown:***

```bash
./hfydl --from-list links.txt --format markdown
```

***🧪 Save the crawl list without downloading:***

```bash
./hfydl https://reddit.com/... --crawl-only story.txt
```

***🖋️ Edit discovered URLs before export:***

```bash
./hfydl --edit https://reddit.com/...
```

---

## ⚙️ Command-line Options

| Option              | Description                                                           |
| ------------------- | --------------------------------------------------------------------- |
| `--edit`            | Edit the list of discovered URLs before exporting.                    |
| `--crawl-only FILE` | Only crawl and save the URL chain to file (no downloading/exporting). |
| `--from-list FILE`  | Read URLs from a file instead of crawling.                            |
| `--format FORMAT`   | Output format (e.g. `epub`, `pdf`, `markdown`, `json`, `html`, etc.). |
| `--cover IMAGE`     | Optional cover image for EPUB export.                                 |
| `--temperature VAL` | Similarity threshold (0.0–1.0) for following links (default: `0.5`).  |
| `URL`               | Starting Reddit post (if `--from-list` is not used).                   |

---

## 📁 File Structure

| File                  | Description                                |
| --------------------- | ------------------------------------------ |
| `hfydl`               | Main crawler and formatter script.         |
| `requirements.txt`    | Python dependencies.                       |

---

## ❤️ Contribute

I'm homeless. Food money is appriciated. 

https://ko-fi.com/lizard_demon

