import os
import requests
import base64

# from PIL import Image
from io import BytesIO
import re
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import json

# --- PLACE THIS AT THE TOP OF YOUR TEST/SCRIPT ---
# Manually load the local settings into os.environ for local testing
if os.path.exists("local.settings.json"):
    with open("local.settings.json") as f:
        config = json.load(f)
        # Pull everything from the "Values" section
        for key, value in config.get("Values", {}).items():
            os.environ[key] = value
# -------------------------------------------------

# # Now your regular code works exactly as expected!
# secret_key = os.environ.get("MySecretKey")
# print(secret_key)


# Dictionary mapping book names to their abbreviations used in the API
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

# List of language/version codes for
version_codes = [
    "de4e12af7f28f599-01",
    "03a021185023710b-01",
    "5b835ce16a1703ff-01",
    "3ea0147e32eebe47-01",
    "a33a100f04f2752e-01",
    "1e8ab327edbce67f-01",
    "e2588ba61891daa5-01",
]

# Set up a requests session with retry logic
session = requests.Session()
retry = Retry(total=3, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry)
session.mount("https://", adapter)


# Function to perform HTTP GET requests with retry logic
def http_get(url: str):
    response = session.get(
        url, headers={"api-key": os.environ.get("API_Key")}, timeout=5
    )
    if response.status_code == 200:
        return response.json()
    return {}


# Function to fetch verses from the API based on book, chapter, and verse number
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

        # Extract and clean the verse text from the API response
        verse = str(response["data"]["content"])
        verse = re.sub(
            r"அத்தியாயம்\s*\d+", "", verse, flags=re.IGNORECASE
        )  # Tamil formatting
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


def get_prompt(verse):
    return f"""Generate an image that is designed specifically for text overlay. 

        The artistic style should be clean to maintain visual simplicity, but can range from styles like classical, modern, minimalist, etc. The overall image must have low brightness and maintain a darker, muted colour value. The colour palette must not default to sepia or brown; instead, choose a diverse, rich, and varied colour scheme that is directly inspired by the emotion and theme of the provided verse. (Examples: use cool blues/greens for peace, deep purples for majesty, or muted reds/oranges for strength, and so on, according to the verse's theme).

        It is crucial that the intended area for the verse overlay remains completely clutter-free and smooth, avoiding bright highlights or busy textures that would interfere with white text legibility.

        You are to include subtle, symbolic details or related subjects based only on the content of the provided verse, according to the following options:
        Option 1: Leave a clear section at the top 70% of the image, and concentrate all symbolic details in the bottom section of the image.
        Option 2: Leave a completely clear section in the horizontal center of the image, and include subtle, small details at the top and bottom perimeters.
        Option 3: Leave a clear section at the bottom 70% of the image, and concentrate all symbolic details in the top section of the image.

        I will give you the verse. Please make the background themed to the verse. 
        Verse:
        "{verse}"

        Note: You will not overlay the verse text on the image, you will only return the image. I will overlay the text later. 
        """


# You will need to set these environment variables or edit the following values.
endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
deployment = os.environ.get("DEPLOYMENT_NAME")
api_version = os.environ.get("OPENAI_API_VERSION")
subscription_key = os.environ.get("AZURE_OPENAI_API_KEY")


def decode_and_save_image(b64_data, output_filename):
    # image = Image.open(BytesIO(base64.b64decode(b64_data)))
    # image.show()
    # image.save(output_filename)
    # Decode the base64 string back into raw file bytes
    image_bytes = base64.b64decode(b64_data)

    # Open a file in binary write mode ('wb') and dump the bytes into it
    with open(output_filename, "wb") as f:
        f.write(image_bytes)

    # Save image bytes as a txt file for debugging
    with open(f"{output_filename}.txt", "w") as f:
        f.write(b64_data)


def save_response(response_data, filename_prefix):
    for idx, item in enumerate(response_data["data"]):
        b64_img = item["b64_json"]
        # Save the b64 img as a txt file for debugging
        with open(f"{filename_prefix}_{idx+1}.txt", "w") as f:
            f.write(b64_img)
        filename = f"{filename_prefix}_{idx+1}.png"
        decode_and_save_image(b64_img, filename)
        print(f"Image saved to: '{filename}'")


def get_b64_from_response(response_data):
    for idx, item in enumerate(response_data["data"]):
        b64_img = item["b64_json"]
        return b64_img


def generate_image(verse):
    generation_url = endpoint
    generation_body = {
        "prompt": get_prompt(verse),
        "n": 1,
        "size": "1024x1024",
        "quality": "medium",
        "output_format": "png",
    }
    generation_response = requests.post(
        generation_url,
        headers={
            "Api-Key": subscription_key,
            "Content-Type": "application/json",
        },
        json=generation_body,
    ).json()
    save_response(generation_response, "generated_image")
    return get_b64_from_response(generation_response)


# # In addition to generating images, you can edit them.
# edit_url = f"{endpoint}{base_path}/edits{params}"
# edit_body = {
#     "prompt": "<IMAGE_PROMPT>",
#     "n": 1,
#     "size": "1024x1024",
#     "quality": "medium",
# }
# files = {
#     "image": (
#         "generated_image_1.png",
#         open("generated_image_1.png", "rb"),
#         "image/png",
#     ),
#     # You can use a mask to specify which parts of the image you want to edit.
#     # The mask must be the same size as the input image.
#     # "mask": ("mask.png", open("mask.png", "rb"), "image/png"),
# }
# edit_response = requests.post(
#     edit_url, headers={"Api-Key": subscription_key}, data=edit_body, files=files
# ).json()
# save_response(edit_response, "edited_image")
