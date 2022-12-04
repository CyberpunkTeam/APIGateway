from app.utils.http_parser import HttpParser


def test_http_parser():
    params = {"email": "mfonseca@fi.uba.ar", "sort": 1}
    params_str = HttpParser.parse_params(params)
    assert params_str == "?email=mfonseca@fi.uba.ar&sort=1"
