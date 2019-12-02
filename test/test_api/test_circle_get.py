import requests as R

from util import show_call


@show_call
def test_circles_get():
    ping_url = "http://127.0.0.1:8000/circles/"
    r = R.get(ping_url)
    print(r.status_code)
    print(r.text)


test_circles_get()



