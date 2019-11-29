import requests

from test.util import show_call


@show_call
def test_post():
    ping_url = "http://127.0.0.1:8000/test/model/"
    data = {
        "attr1": "abc",
        "attr2": 12,
        "attr3": "2019-10-24 11:11:11"
    }
    r = requests.post(ping_url, json=data)
    print(r.status_code)
    print(r.text)


test_post()



