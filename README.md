Here’s a **brutally simple and beautiful** `README.md` for your script:

---

# HFYDL — Reddit HFY Story to EPUB

**Turn an HFY story chain on Reddit into a clean, offline EPUB.**
Scrapes linked "Next" posts. Bundles them into an ebook. Nothing else.

---

## ✨ Features

* Follows “Next” links across posts
* Grabs only the post text and author
* Styles the output cleanly
* Outputs a single `.epub` file
* Optional cover support

---

## 🛠️ Installation

```bash
# 1. Create and activate a virtual environment (if you don't already have one)
python3 -m venv venv
source venv/bin/activate

# 2. Install the dependencies
pip install requests beautifulsoup4 pypandoc
```

---

## 📚 Usage

```bash
./hfydl.py "https://reddit.com/r/HFY/comments/xxxxxx/story_part_1/"
```

### Optional flags:

```bash
-o FILE       # output filename (default: story.epub)
-t TITLE      # title of the book
-a AUTHOR     # author name
-c IMAGE      # path to a cover image (optional)
```

### Example:

```bash
./hfydl.py "https://old.reddit.com/r/HFY/comments/abcd1234/my_story_part_1/" \
  -o fuckaliens.epub \
  -t "Humans Fuck Alens! (not like that)" \
  -a "u/humansrule" \
  -c deadalien.jpg
```

---

## 🧼 Output

* EPUB file: ready to sideload into your e-reader
* Clean formatting, headers, and page breaks
* Compatible with most readers (tested with Calibre, Kindle, KOReader)

---

## ✅ Dependencies

* Python 3.x
* [requests](https://pypi.org/project/requests/)
* [beautifulsoup4](https://pypi.org/project/beautifulsoup4/)
* [pypandoc](https://pypi.org/project/pypandoc/)
* [pandoc](https://pandoc.org/) — must be installed and available in your PATH
  * [Download](https://pandoc.org/installing.html)

---

## 💡 Tips

* Ensure you use the first post in the series.
* Requires the story to be chained with “next”. Capitalization is irrelivant.
* If a post has no text (`selftext`), it will be skipped.

---

## 🐛 Caveats

* Doesn’t support image posts or external links.
* Won’t detect custom next/previous link formats.
* Reddit API quirks may cause occasional hiccups.

---

## 📄 License

GPL3 License. Fuck corpos.
