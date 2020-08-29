# booru-scraper: scrapes a booru for posts

`booru-scraper` is a Python script that scrapes a [booru](https://en.wiktionary.org/wiki/booru)-style (imageboard)[https://en.wikipedia.org/wiki/Imageboard#Danbooru-style_boards] for posts and sorts them in directories based on the searched tags. Only older boorus are supported, and `booru-scraper` is useful also if you have a copy of such a booru and want to sort its images in different fashions.

## Usage

    usage: booru-scraper.py [-h] [--booru BOORU] [--limit LIMIT] [--page PAGE] DIRECTORY [TAG [TAG ...]]

    Scrapes a booru for posts

    positional arguments:
      DIRECTORY      Where to fetch the posts to
      TAG            Any number of tags to search, searches across all tags if none specified

    optional arguments:
      -h, --help     show this help message and exit
      --booru BOORU  URL of the booru to use (default: http://localhost)
      --limit LIMIT  Number of posts to get from the page (default: 100)
      --page PAGE    Page number to start the search from (default: 1)

## Notes

The files are checked for checksum mismatches and re-fetched if necessary. The modification time of the file is set to the original upload date.

`booru-scraper` does not support specifying a range of pages to fetch to respect possible bandwidth limits on hosted boorus.
