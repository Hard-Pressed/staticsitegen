import unittest

from htmlnode import HTMLNode, LeafNode


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

    def test_leafnode_to_html_renders_plain_tag(self):
        node = LeafNode("p", "This is a paragraph of text.")
        self.assertEqual(node.to_html(), "<p>This is a paragraph of text.</p>")

    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_h1(self):
        node = LeafNode("h1", "Main title")
        self.assertEqual(node.to_html(), "<h1>Main title</h1>")

    def test_leaf_to_html_code(self):
        node = LeafNode("code", "print('ok')")
        self.assertEqual(node.to_html(), "<code>print('ok')</code>")

    def test_leafnode_to_html_renders_with_props(self):
        node = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
        self.assertEqual(node.to_html(), '<a href="https://www.google.com">Click me!</a>')

    def test_leafnode_to_html_returns_raw_text_when_tag_is_none(self):
        node = LeafNode(None, "Raw text")
        self.assertEqual(node.to_html(), "Raw text")

    def test_leafnode_to_html_raises_when_value_is_none(self):
        node = LeafNode("p", None)
        with self.assertRaises(ValueError):
            node.to_html()

    def test_leafnode_repr_excludes_children(self):
        node = LeafNode("span", "chip", {"class": "pill"})
        self.assertEqual(
            repr(node),
            "LeafNode(tag='span', value='chip', props={'class': 'pill'})",
        )


if __name__ == "__main__":
    unittest.main()
