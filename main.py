import argparse
from urllib.request import urlopen
from ebooklib import epub
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser(
    description="",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.add_argument("--url")
parser.add_argument("--type", default="post")

def createChapterFromPostURL(postUrl):
    page = urlopen(postUrl)
    html_bytes = page.read()
    html = html_bytes.decode("utf-8")
    soup = BeautifulSoup(html, 'html.parser')
    content = soup.find('div', id="postBody")
    title = soup.find('h1', class_="Typography-root Typography-display3 PostsPageTitle-root")
    title = title.get_text()
    author = soup.find('a', class_="UsersNameDisplay-noColor")
    author = author.get_text()

    chapter = epub.EpubHtml(title=title,
                    file_name=title + '.xhtml',
                    lang='en',
                    uid=title)
    
    chapter.set_content("<h1>" + str(title) + "</h1>" + str(content))
    return chapter, author

def createEbookFromPost(url):
    book = epub.EpubBook()

    chapter, author = createChapterFromPostURL(url)
    book.add_item(chapter)

    book.set_title(chapter.title)
    book.set_identifier(chapter.title)
    book.add_author(author)
    book.set_language('en')
    description = "The post \"" + chapter.title + "\", formatted as an .epub."
    book.add_metadata('DC', 'description', description)

    book.toc = (epub.Link(chapter.file_name, chapter.title, chapter.title),)
    book.spine = [chapter]
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    epub.write_epub(chapter.title + '.epub', book)
    print("Successfully created ebook!")
    

def createEbookFromSequence(url):
    print("Not yet implemented.")
    # Scrape URLs for all the posts
    # Create chapters for each of the posts
    # Add authors
    # Scrape title
    # Set title

def main(args):
    if args.type == "post":
        createEbookFromPost(args.url)
    elif args.type == "sequence":
        createEbookFromSequence(args.url)

if __name__ == "__main__":
    main(parser.parse_args())