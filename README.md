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
  Pause and tweak the url list using your `$EDITOR`.  

- 📄 **Well Formatted Output**  
  All stories are saved as readable, paginated chapters, with a table of contents.

- 📚 **Cover Support**  
  Add a cover image to EPUB exports for that final polish.

- 💋 **Simple(ish)**  
  Only ~220 lines of python... Well as simple as you can make something like this.

---

## 🛠️ Installation

### Prerequisites

You need to have the following installed:

* `python3`
* `pandoc`
* (optional) if you want pdfs: [pandoc pdf engine](https://pandoc.org/MANUAL.html#option--pdf-engine)

### Unix-Based Install

```bash
# Download Project
git clone https://github.com/lizard-demon/hfydl
cd hfydl

# Create a virtual enviroment
python3 -m venv venv

# Enter the virtual enviroment
source ./venv/bin/activate

# Install Depedancies
pip install -r requirements.txt

# Make code executable
sudo chmod +x hfydl

# Now you have a working downloader
./hfydl -h
```

***Note:***

*If you ever want to use this tool again, you will need to re-enter your venv.*

```bash
cd hfydl                    # go to git folder
source ./venv/bin/activate  # enter your venv
./hfydl -h                  # now you can use it
deactivate                  # exits the venv
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

***🖋️ Interrupt and edit the url list before downloading:***

```bash
./hfydl --edit "https://reddit.com/..."
```

***🧪 Save the url list without downloading:***

```bash
./hfydl "https://reddit.com/..." --crawl-only links.txt
```

***📜 Download url list without crawling:***

```bash
./hfydl --from-list links.txt --format markdown
```

---

## ⚙️ Command-line Options

| Option              | Description                                                           |
| ------------------- | --------------------------------------------------------------------- |
| `--edit [EDITOR]`   | Edit the list of discovered URLs before exporting.                    |
| `--format FORMAT`   | Output format (e.g. `epub`, `pdf`, `markdown`, `json`, `html`, etc.). |
| `--cover IMAGE`     | Optional cover image for EPUB export.                                 |
| `--crawl-only FILE` | Only crawl and save the URL list to file (no downloading/exporting).  |
| `--from-list FILE`  | Only download and export from a file (no crawling).                   |
| `--temperature VAL` | Similarity threshold (0.0–1.0) for following links (default: `0.5`).  |
| `URL`               | Starting Reddit post (if `--from-list` is not used).                  |

---

## ❤️ Contribute

I'm homeless. Food money is appriciated. 

https://ko-fi.com/lizard_demon

