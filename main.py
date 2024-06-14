import argparse
from urllib.request import urlopen

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

if __name__ == "__main__":
    main(parser.parse_args())