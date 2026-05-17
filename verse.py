import requests
import re
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import os

book_abbrv_dict = {
    "genesis": "GEN",
    "exodus": "EXO",
    "leviticus": "LEV",
    "numbers": "NUM",
    "deuteronomy": "DEU",
    "joshua": "JOS",
    "judges": "JDG",
    "ruth": "RUT",
    "1samuel": "1SA",
    "2samuel": "2SA",
    "1kings": "1KI",
    "2kings": "2KI",
    "1chronicles": "1CH",
    "2chronicles": "2CH",
    "ezra": "EZR",
    "nehemiah": "NEH",
    "esther": "EST",
    "job": "JOB",
    "psalms": "PSA",
    "proverbs": "PRO",
    "ecclesiastes": "ECC",
    "songofsolomon": "SNG",
    "isaiah": "ISA",
    "jeremiah": "JER",
    "lamentations": "LAM",
    "ezekiel": "EZK",
    "daniel": "DAN",
    "hosea": "HOS",
    "joel": "JOL",
    "amos": "AMO",
    "obadiah": "OBA",
    "jonah": "JON",
    "micah": "MIC",
    "nahum": "NAM",
    "habakkuk": "HAB",
    "zephaniah": "ZEP",
    "haggai": "HAG",
    "zechariah": "ZEC",
    "malachi": "MAL",
    "matthew": "MAT",
    "mark": "MRK",
    "luke": "LUK",
    "john": "JHN",
    "acts": "ACT",
    "romans": "ROM",
    "1corinthians": "1CO",
    "2corinthians": "2CO",
    "galatians": "GAL",
    "ephesians": "EPH",
    "philippians": "PHP",
    "colossians": "COL",
    "1thessalonians": "1TH",
    "2thessalonians": "2TH",
    "1timothy": "1TI",
    "2timothy": "2TI",
    "titus": "TIT",
    "philemon": "PHM",
    "hebrews": "HEB",
    "james": "JAS",
    "1peter": "1PE",
    "2peter": "2PE",
    "1john": "1JN",
    "2john": "2JN",
    "3john": "3JN",
    "jude": "JUD",
    "revelation": "REV",
}

version_codes = [
    "de4e12af7f28f599-01",
    "03a021185023710b-01",
    "5b835ce16a1703ff-01",
    "3ea0147e32eebe47-01",
    "a33a100f04f2752e-01",
    "1e8ab327edbce67f-01",
    "e2588ba61891daa5-01",
]

session = requests.Session()
retry = Retry(total=3, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry)
session.mount("https://", adapter)


def http_get(url: str):
    response = session.get(
        url, headers={"api-key": os.environ.get("API_Key")}, timeout=5
    )
    if response.status_code == 200:
        return response.json()
    return {}


def get_verses(book: str, chapter: int, verse_num: int) -> list:
    book = book.replace(" ", "").lower()
    book_abbrv = book_abbrv_dict.get(book)

    all_verses: list[str] = []

    for version in version_codes:
        print(f"DEBUG: {version}")
        response = http_get(
            f"https://api.scripture.api.bible/v1/bibles/{version}/verses/{book_abbrv}.{chapter}.{verse_num}?content-type=html&include-notes=false&include-titles=false&include-chapter-numbers=false&include-verse-numbers=false&include-verse-spans=false&use-org-id=false"
        )
        # print(response)
        verse = str(response["data"]["content"])
        verse = re.sub(r"அத்தியாயம்\s*\d+", "", verse, flags=re.IGNORECASE)
        verse = re.sub(r"<.*?>", "", verse)
        if version == "1e8ab327edbce67f-01":
            verse = re.sub(r"\(.*?\)", "", verse)
        else:
            verse = re.sub(r"\u00B6\s", "", verse)
        # print("Verse:", verse)

        reference = response["data"]["reference"]
        # print("Ref:", reference)

        verse_with_ref = verse + "\n" + reference
        all_verses.append(verse_with_ref)

    print(all_verses)
    return all_verses


# get_verses("Genesis", 1, 1)
