import requests

def send_zoom(URL, text, seq, lang="en-US"):
    API_URL = URL
    API_URL += "&seq={}".format(seq)
    API_URL += "&lang={}".format(lang)

    headers={'Content-Type': 'text/plain'}
    res = requests.post(API_URL, text.encode("utf-8"), headers=headers)
    
    return res
