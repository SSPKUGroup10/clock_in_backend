import requests as R

from util import show_call


@show_call
def test_circles_get():
    ping_url = "http://127.0.0.1:8000/circles/"
    r = R.get(ping_url)
    print(r.status_code)
    print(r.json())

@show_call
def test_cirlcle_get_by_id():
    ping_url = "http://127.0.0.1:8000/circles/1/"
    r = R.get(ping_url)
    print(r.json())


@show_call
def test_cirlcle_get_by_id():
    ping_url = "http://127.0.0.1:8000/circles/1/"
    r = R.get(ping_url)
    print(r.json())


@show_call
def test_cirlcle_update_by_id():
    ping_url = "http://127.0.0.1:8000/circles/1/"
    data = {
        'name': '新名字2'
    }
    r = R.put(ping_url, json=data)
    print(r.json())

@show_call
def test_cirlcle_delete_by_id():
    ping_url = "http://127.0.0.1:8000/circles/1/"
    r = R.delete(ping_url)
    print(r.json())


test_circles_get()
test_cirlcle_get_by_id()
test_cirlcle_update_by_id()
# test_cirlcle_delete_by_id()

