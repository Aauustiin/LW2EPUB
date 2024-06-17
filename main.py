import argparse
from urllib.request import urlopen
from urllib.parse import urljoin
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
    book = epub.EpubBook()

    page = urlopen(url)
    html_bytes = page.read()
    html = html_bytes.decode("utf-8")
    soup = BeautifulSoup(html, 'html.parser')

    title = soup.find('h1', class_="Typography-root Typography-display2 SequencesPage-title")
    title = title.get_text()
    book.set_title(title)
    book.set_identifier(title)

    author = soup.find('a', class_="UsersNameDisplay-noColor")
    author = author.get_text()
    book.add_author(author)
    # authors = set()
    # authors.add(author)

    book.set_language('en')
    description = "The sequence \"" + title + "\", formatted as an .epub."
    book.add_metadata('DC', 'description', description)
    # initial_preamble = soup.find('div', class_="SequencesPage-description ContentStyles-base content ContentStyles-postBody")
    # Make html for initial preamble

    content = soup.find("div", class_="chapters-list")
    divs = content.findAll("div")

    post_urls = divs[0].findAll("span", class_="PostsTitle-eaTitleDesktopEllipsis")
    post_urls = map(lambda x : urljoin(url, x.find("a").get("href")), post_urls)
    chapters = map(lambda x : createChapterFromPostURL(x), post_urls)
    chapters, chapter_authors = zip(*chapters)
    # authors.add(chapter_authors)
    for chapter in chapters:
        book.add_item(chapter)

    # links = map(lambda x : epub.Link(x.file_name, x.title, x.title), chapters)
    # book.toc = tuple(links)
    # book.spine = chapters

    # for div in divs[1:]:
        # Scrape section title
        # Scrape section preamble
        # Make html for preamble
        # Scrape section post urls
        # Create chapter for each post
        # Add authors from chapters
    book.toc = tuple(map(lambda x : epub.Link(x.file_name, x.title, x.title), chapters))
    book.spine = chapters
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # for author in authors:
    #     book.add_author(author)

    epub.write_epub(title + '.epub', book)
    print("Successfully created ebook!")

def main(args):
    if args.type == "post":
        createEbookFromPost(args.url)
    elif args.type == "sequence":
        createEbookFromSequence(args.url)

if __name__ == "__main__":
    main(parser.parse_args())