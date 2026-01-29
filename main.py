import requests
import re
import json
import os

# URL = "https://www.tanuki-manga.com/lupin-the-third-28/"
# SAVE_DIR = "images4"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.up-manga.com/"
}


def extract_from_obfuscated_js(html: str) -> list[str] | None:
    urls = []

    eval_blocks = re.findall(
        r"eval\(function\(p,a,c,k,e,d\)\{[\s\S]+?\}\)\)",
        html
    )

    for js in eval_blocks:
        m = re.search(r"'([^']+)'\.split\('\|'\)", js)
        if not m:
            continue

        parts = m.group(1).split("|")

        try:
            # year = next(p for p in parts if re.fullmatch(r"\d{4}", p))
            # month = next(p for p in parts if p.isdigit() and len(p) == 2)
            # subdir = next(p for p in parts if re.fullmatch(r"[a-f0-9]{2}", p))
            year = parts[27]
            month = parts[26]
            subdir = parts[25]
            prefix = next(p for p in parts if re.fullmatch(r"[A-Z0-9]{5}", p))
            encoded = next(
                p for p in parts
                if re.fullmatch(r"[A-Za-z0-9+/=]{30,}", p)
            )
            timestamp = next(
                p for p in parts
                if p.isdigit() and len(p) == 10
            )

            url = (
                f"https://img.tanuki-manga.com/"
                f"{year}/{month}/{subdir}/"
                f"{prefix}-N-{encoded}-{timestamp}.jpg"
            )
            urls.append(url)

        except StopIteration:
            continue

    return urls or None


def get_images_from_ts_reader(html: str) -> list[str]:

    pattern = r'"images"\s*:\s*(\[[\s\S]*?\])'
    match = re.search(pattern, html)

    # if not match:
    #     raise Exception("Not found sources in ts_reader.run")

    if match:
        images_raw = match.group(1)
        images = json.loads(images_raw)

        print("[+] Found images via images array")
        return images
    
    images = extract_from_obfuscated_js(html)
    if images:
        print("[+] Found images via obfuscated JS")
        return images
    

    # return images

    raise Exception("Not found both pattern in source.")

def download_images(images: list[str], SAVE_DIR):
    os.makedirs(SAVE_DIR, exist_ok=True)

    for i, img_url in enumerate(images, start=1):
        filename = f"{SAVE_DIR}/{i:03}.jpg"
        print(f"[+] Loading.. {filename}")

        r = requests.get(img_url, headers=HEADERS, timeout=15)
        r.raise_for_status()

        with open(filename, "wb") as f:
            f.write(r.content)


def main():
    for i in range(108,226):
        URL = f"https://www.tanuki-manga.com/chainsaw-man-{i+1}/"
        SAVE_DIR = f"Chapter-{i+1}"

        print("[*] Loading website")
        html = requests.get(URL, headers=HEADERS).text

        print("[*] Export image list from ts_reader")
        images = get_images_from_ts_reader(html)

        print(f"[+] Image founded: {len(images)}")
        download_images(images, SAVE_DIR)

        print("[✓] Successfully")


if __name__ == "__main__":
    main()
