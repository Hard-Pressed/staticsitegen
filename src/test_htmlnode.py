import unittest

from htmlnode import HTMLNode


class TestHTMLNode(unittest.TestCase):
    def test_props_to_html_with_multiple_attributes(self):
        node = HTMLNode(
            tag="a",
            props={
                "href": "https://www.google.com",
                "target": "_blank",
            },
        )
        self.assertEqual(
            node.props_to_html(),
            ' href="https://www.google.com" target="_blank"',
        )

    def test_props_to_html_with_none_props_returns_empty_string(self):
        node = HTMLNode(tag="p", value="hello", props=None)
        self.assertEqual(node.props_to_html(), "")

    def test_props_to_html_with_empty_props_returns_empty_string(self):
        node = HTMLNode(tag="div", children=[], props={})
        self.assertEqual(node.props_to_html(), "")

    def test_repr_includes_all_fields(self):
        child = HTMLNode(tag="span", value="child")
        node = HTMLNode(tag="p", value="parent", children=[child], props={"class": "x"})
        expected = (
            "HTMLNode(tag='p', value='parent', children=[HTMLNode(tag='span', value='child', "
            "children=None, props=None)], props={'class': 'x'})"
        )
        self.assertEqual(repr(node), expected)


if __name__ == "__main__":
    unittest.main()
