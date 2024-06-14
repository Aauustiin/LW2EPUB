import argparse
from urllib.request import urlopen
from ebooklib import epub

parser = argparse.ArgumentParser(
    description="",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.add_argument("--url")

def main(args):
    page = urlopen(args.url)
    html_bytes = page.read()
    html = html_bytes.decode("utf-8")
    print(html)
    book = epub.EpubBook()
    book.set_identifier('sample123456')
    book.set_title('Sample book')
    book.set_language('en')

    book.add_author('Aleksandar Erkalovic')
    book.add_metadata('DC', 'description', 'This is description for my book')
    book.add_metadata(None, 'meta', '', {'name': 'key', 'content': 'value'})

    # intro chapter
    c1 = epub.EpubHtml(title='Introduction',
                    file_name='intro.xhtml',
                    lang='en')
    c1.set_content(u'<html><body><h1>Introduction</h1><p>Introduction paragraph.</p></body></html>')

    # about chapter
    c2 = epub.EpubHtml(title='About this book',
                    file_name='about.xhtml')
    c2.set_content('<h1>About this book</h1><p>This is a book.</p>')
    book.add_item(c1)
    book.add_item(c2)
    style = 'body { font-family: Times, Times New Roman, serif; }'

    nav_css = epub.EpubItem(uid="style_nav",
                            file_name="style/nav.css",
                            media_type="text/css",
                            content=style)
    book.add_item(nav_css)
    book.toc = (epub.Link('intro.xhtml', 'Introduction', 'intro'),
              (
                epub.Section('Languages'),
                (c1, c2)
              )
            )
    book.spine = ['nav', c1, c2]
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    epub.write_epub('test.epub', book)
    print("Created ebook!")

if __name__ == "__main__":
    main(parser.parse_args())