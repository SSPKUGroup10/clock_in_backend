import requests

from util import show_call

@show_call
def test_get():
    ping_url = "http://127.0.0.1:8000/test/"
    r = requests.get(ping_url)

    assert r.status_code == 200

    print(r.text)
    print(r.status_code)
    print(r.json())

@show_call
def test_post():
    ping_url = "http://127.0.0.1:8000/test/"
    r = requests.post(ping_url, json={"hello": "this is a post data"})
    print(r.status_code)
    print(r.text)


test_get()
test_post()



