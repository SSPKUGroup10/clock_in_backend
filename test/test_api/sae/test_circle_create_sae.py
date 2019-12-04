import requests

from test.util import show_call

sae_url = "https://2019group10.applinzi.com"

@show_call
def test_circle_create():
    ping_url = sae_url + "/circles/"
    data = {
        "name": "7点钟起床群",
        "type": "GET_UP",
        "start_at": "2019-10-24 11:11:11",
        "end_at": "2020-10-24 11:11:11",
        "desc": "早睡早起身体好",
        "check_rule": "7点之前必须起床，然后发一张穿好衣服的照片",
        "circle_master_id": 1

    }
    r = requests.post(ping_url, json=data)
    print(r.status_code)
    print(r.text)


if __name__ == '__main__':
    test_circle_create()




