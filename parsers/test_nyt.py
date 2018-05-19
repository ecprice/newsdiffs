from mock import patch

from nyt import NYTParser


@patch('parsers.baseparser.grab_url')
def test_old_format(mock_grab_url):
    from test_nyt_data import HTML_OLD_FORMAT
    mock_grab_url.return_value = HTML_OLD_FORMAT
    parser = NYTParser('https://www.nytimes.com/2018/05/18/us/school-shooting-santa-fe-texas.html')
    assert 'SANTA FE, Tex.' in parser.body


@patch('parsers.baseparser.grab_url')
def test_new_format(mock_grab_url):
    from test_nyt_data import HTML_NEW_FORMAT
    mock_grab_url.return_value = HTML_NEW_FORMAT
    parser = NYTParser('https://www.nytimes.com/2018/05/16/us/politics/mueller-trump-indictment.html')
    assert 'Trump' in parser.body
    assert len(parser.body.split('\n\n')) == 28

