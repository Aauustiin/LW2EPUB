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
    
    chapter.set_content("<head><link rel=\"stylesheet\" href=\"style/0.css\"><link rel=\"stylesheet\" href=\"style/1.css\"><link rel=\"stylesheet\" href=\"style/2.css\"><link rel=\"stylesheet\" href=\"style/3.css\"><link rel=\"stylesheet\" href=\"style/4.css\"><link rel=\"stylesheet\" href=\"style/5.css\"></head>" + "<body><h1>" + str(title) + "</h1>" + str(content) + "</body>")
    return chapter, author

def createIntroChapter(preamble, title):
    intro = epub.EpubHtml(title="Preamble",
                    file_name=title + '.xhtml',
                    lang='en',
                    uid=title)
    intro.set_content("<h1>" + str(title) + "</h1><p>" + str(preamble) + "</p>")
    return intro

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

    book.set_language('en')
    description = "The sequence \"" + title + "\", formatted as an .epub."
    book.add_metadata('DC', 'description', description)

    link_tags = soup.find_all('link', rel='stylesheet')
    link_tags.extend(soup.find_all('link', rel='preload'))
    for i, link in enumerate(link_tags):
        href = link.get('href')
        if href:
            full_url = urljoin(url, href)
            css_response = urlopen(full_url)
            css_content = css_response.read().decode('utf-8')
            nav_css = epub.EpubItem(uid=f"style_{i}",
                                    file_name=f"style/{i}.css",
                                    media_type="text/css",
                                    content=css_content)
            book.add_item(nav_css)

    initial_preamble = soup.find('div', class_="SequencesPage-description ContentStyles-base content ContentStyles-postBody")
    frontmatter = createIntroChapter(initial_preamble, title)
    book.add_item(frontmatter)

    spine = [frontmatter, "nav"]
    toc = []

    content = soup.find("div", class_="chapters-list")
    sections = content.children

    for section in sections:
        post_urls = section.findAll("span", class_="PostsTitle-eaTitleDesktopEllipsis")
        post_urls = map(lambda x : urljoin(url, x.find("a").get("href")), post_urls)
        section_title = section.find("div", class_="ChaptersItem-title").get_text()
        section_preamble = section.find("div", class_="ChaptersItem-description ContentStyles-base content ContentStyles-postBody")
        section_intro = createIntroChapter(section_preamble, section_title)

        content = map(lambda x : createChapterFromPostURL(x), post_urls)
        chapters, authors = zip(*content)

        if section_title == "":
            toc.extend([epub.Link(x.file_name, x.title, x.title) for x in chapters])
        else:
            chapters = (section_intro,) + chapters
            toc.append((epub.Section(section_title), chapters))
        spine.extend(chapters)
    
    for chapter in spine[2:]:
        book.add_item(chapter)
    
    book.toc = toc
    book.spine = spine
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    epub.write_epub(title + '.epub', book)
    print("Successfully created ebook!")

def main(args):
    if args.type == "post":
        createEbookFromPost(args.url)
    elif args.type == "sequence":
        createEbookFromSequence(args.url)

if __name__ == "__main__":
    main(parser.parse_args())