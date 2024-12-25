import pandas as pd
import requests
import logging
import time

from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def fetch_urls(apply_dict, stock_code, desc, i):
    params = {
        "q": desc + "amazon uk",
        "tbm": "isch",
        "content-type": "image/png",
    }

    html = requests.get("https://www.google.com/search", params=params)
    soup = BeautifulSoup(html.text, "html.parser")

    images_url = [img["src"] for img in soup.select("img")]

    apply_dict["item_id"].append(stock_code)
    apply_dict["description"].append(desc)

    try:
        apply_dict["image_url"].append(images_url[1])
        logger.info(f"save image url: {images_url[1]}. ITEM #{i}")
    except IndexError:
        apply_dict["image_url"].append("")
        logger.warning("image not found.")

    time.sleep(1)


def main():
    apply = dict()
    apply["item_id"] = []
    apply["description"] = []
    apply["image_url"] = []
    df = pd.read_csv("../raw_data/prepared.csv")

    copy = df[["StockCode", "Description"]]
    copy = copy.drop_duplicates(subset=["StockCode"])

    for i, tup in enumerate(copy[["StockCode", "Description"]].values):
        stock_code, desc = tup
        fetch_urls(apply_dict=apply,
                   stock_code=stock_code,
                   desc=desc,
                   i=i)

    item_image = pd.DataFrame(apply)
    item_image.to_csv("image_item.csv")


if __name__ == "__main__":
    main()
