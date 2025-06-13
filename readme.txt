HFYDL(1)                    General Commands Manual                   HFYDL(1)

NAME
     hfydl – reddit HFY story crawler and formatter

SYNOPSIS
     hfydl [-edit] [-crawl-only FILE] [-from-list FILE]
           [-format FORMAT] [-cover IMAGE] [-temperature VALUE]
           [URL]

DESCRIPTION
     hfydl crawls a chain of "Humanity, Fuck Yeah" (HFY) stories on Reddit,
     starting from a given post URL, and assembles them into a clean,
     publishable format such as EPUB, PDF, Markdown, or JSON.

     Story links are followed by vector similarity, allowing narrative chains
     to be automatically discovered. All posts are fetched, cleaned, and
     saved as chapters in the desired output format.

OPTIONS
     -edit
           Open the list of discovered URLs in your $EDITOR before exporting.

     -crawl-only FILE
           Save the list of crawled URLs to a file and exit. No downloading or
           exporting is performed.

     -from-list FILE
           Instead of crawling, read Reddit post URLs (one per line) from a
           file.

     -format FORMAT
           Output format for the book. Supported formats include:

           epub, pdf, markdown (md), json, html, docx, odt, rtf, txt,
           asciidoc, latex, pptx, beamer, and many others supported by Pandoc.

           Default is epub.

     -cover IMAGE
           Optional cover image for EPUB export.

     -temperature VALUE
           Cosine similarity threshold for story continuation, from 0.0
           (loose) to 1.0 (strict). Default: 0.5.

OPERANDS
     URL
           The initial Reddit post to begin crawling from. If omitted, use
           -from-list to provide posts.

INSTALLATION
     Install dependencies via pip and system tools:

           python3 -m venv venv
           . venv/bin/activate
           pip install -r requirements.txt

     You also need a working Pandoc installation for format conversion:

           sudo apt install pandoc            # Debian/Ubuntu
           brew install pandoc                # macOS
           choco install pandoc               # Windows

     Optionally, install a LaTeX engine (e.g., texlive) for PDF output.

FILES
     ~/.cache/model2vec/
           Stores the pretrained story embedding model.

ENVIRONMENT
     $EDITOR
           Used if -edit is specified. Defaults to nano or notepad.

EXIT STATUS
     The hfydl utility exits 0 on success, and >0 if an error occurs.

EXAMPLES
     Crawl a Reddit story and export as EPUB:

           hfydl https://www.reddit.com/r/HFY/comments/abc123/story_title

     Use a list of links from a file and export as Markdown:

           hfydl -from-list links.txt -format markdown

     Crawl only and save the URL chain:

           hfydl https://reddit.com/... -crawl-only story.txt

AUTHORS
     Lizard Demon - Find me over on reddit u/lizrd_demon.


