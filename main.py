import requests
import re
import json
import os

URL = "https://www.up-manga.com/jujutsu-kaisen-ep-119/"
SAVE_DIR = "images2"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.up-manga.com/"
}


def get_images_from_ts_reader(html: str) -> list[str]:
    # pattern = r'"sources"\s*:\s*(\[[\s\S]*?\])'
    # match = re.search(pattern, html)

    pattern = r'"images"\s*:\s*(\[[\s\S]*?\])'
    match = re.search(pattern, html)

    if not match:
        raise Exception("Not found sources in ts_reader.run")

    # sources = json.loads(match.group(1))
    # images = sources[0]["images"]

    images_raw = match.group(1)
    images = json.loads(images_raw)

    return images


def download_images(images: list[str]):
    os.makedirs(SAVE_DIR, exist_ok=True)

    for i, img_url in enumerate(images, start=1):
        filename = f"{SAVE_DIR}/{i:03}.jpg"
        print(f"[+] Loading.. {filename}")

        r = requests.get(img_url, headers=HEADERS, timeout=15)
        r.raise_for_status()

        with open(filename, "wb") as f:
            f.write(r.content)


def main():
    print("[*] Loading website")
    html = requests.get(URL, headers=HEADERS).text

    print("[*] Export image list from ts_reader")
    images = get_images_from_ts_reader(html)

    print(f"[+] Image founded: {len(images)}")
    download_images(images)

    print("[✓] Successfully")


if __name__ == "__main__":
    main()