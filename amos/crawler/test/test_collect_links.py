from collect_links import CollectLinks
from mock import patch, PropertyMock


class Chrome:
    def get(self, url):
        response_html = """
            <!DOCTYPE html>
            <html>
            <head>
            <title>Welcome to my fun page</title>
            <meta charset="UTF-8">
            </head>
            <body>
            <h2>Search Python.org</h2>
            <form action="/">
                <input id="id-search-field" name="search" />
            </form>
            <img>Test Image</img>
            </body>
            </html>
            """

        return response_html

    def find_element_by_tag_name(self, name):
        return Element()

    def find_elements(self, by, value):
        return [Image()]

    def close(self):
        pass


class Element:
    def send_keys(self, key):
        pass


class Image:
    def get_attribute(self, attribute):
        return "http://www.test.com"


def get_html():
    return "test"


def test_pinterest():
    collect = CollectLinks(no_gui=True, no_driver=False)
    with patch("collect_links.CollectLinks.browser", create=True, new_callable=PropertyMock, return_value=Chrome()):
        result = collect.pinterest("test", "Berlin")
        assert result == ["http://www.test.com"]
