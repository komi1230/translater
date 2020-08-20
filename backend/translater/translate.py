import re
import requests


API_URL = "https://script.google.com/macros/s/AKfycbzbGAw0pHReRyBeLH1uKH_8OmLTLOY95mLTvuQVH6ZUeOAa-b_a/exec"

def translate(text, target="en"):
    source = cjk_detect(text)
    
    if source is "en":
        target = "ja"

    if source is "ja":
        target = "en"

    if source is "zh":
        target = "ja"

    URL = API_URL
    URL += "?text=" + text
    URL += "&source=" + source + "&target=" + target

    res = requests.get(URL).json()

    return res["text"]


def cjk_detect(texts):
    # korean
    if re.search("[\uac00-\ud7a3]", texts):
        return "ko"
    # japanese
    if re.search("[\u3040-\u30ff]", texts):
        return "ja"
    # chinese
    if re.search("[\u4e00-\u9FFF]", texts):
        return "zh"
    return "en"


if __name__ == "__main__":
    text = "私は東京に住んでいます"
    print(cjk_detect(text))
