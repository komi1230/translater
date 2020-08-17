import requests

API_URL = "https://script.google.com/macros/s/AKfycbzbGAw0pHReRyBeLH1uKH_8OmLTLOY95mLTvuQVH6ZUeOAa-b_a/exec"

def translate(text, source="ja", target="en"):
    URL = API_URL
    URL += "?text=" + text
    URL += "&source=" + source + "&target=" + target

    res = requests.get(URL).json()

    return res["text"]
