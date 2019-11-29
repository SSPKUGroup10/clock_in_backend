import requests

from util import show_call

ping_url = "https://2019group10.applinzi.com/test/"


@show_call
def test_get():

    r = requests.get(ping_url)
    assert r.status_code == 200

    print(r.text)
    print(r.status_code)
    print(r.json())


@show_call
def test_post():
    r = requests.post(ping_url, json={"hello": "this is a post data"})
    print(r.status_code)
    print(r.text)


test_get()
test_post()

