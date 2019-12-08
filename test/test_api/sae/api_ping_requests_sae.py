import requests

ping_url = "https://zxzx.applinzi.com/api/v1/test/"


def test_get():
    r = requests.get(ping_url)
    print(r.text)
    print(r.status_code)
    print(r.json())


def test_post():
    r = requests.post(ping_url, json={"hello": "this is a post data"})
    print(r.status_code)
    print(r.text)


test_get()
test_post()

