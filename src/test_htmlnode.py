import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode
from textnode import TextNode, TextType
from htmlnode import text_node_to_html_node
from htmlnode import text_node_to_html_node
from textnode import TextNode, TextType


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

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_to_html_with_multiple_children(self):
        c1 = LeafNode("li", "one")
        c2 = LeafNode("li", "two")
        parent = ParentNode("ul", [c1, c2])
        self.assertEqual(parent.to_html(), "<ul><li>one</li><li>two</li></ul>")

    def test_to_html_nested_parents(self):
        inner = ParentNode("section", [LeafNode("p", "x")])
        outer = ParentNode("article", [inner])
        self.assertEqual(outer.to_html(), "<article><section><p>x</p></section></article>")

    def test_to_html_with_no_children(self):
        parent = ParentNode("div", [])
        self.assertEqual(parent.to_html(), "<div></div>")

    def test_to_html_with_string_child(self):
        parent = ParentNode("p", ["raw text"])
        self.assertEqual(parent.to_html(), "<p>raw text</p>")

    def test_to_html_raises_when_children_none(self):
        parent = ParentNode("div", None)
        with self.assertRaises(ValueError):
            parent.to_html()

    def test_to_html_raises_when_tag_none(self):
        parent = ParentNode(None, [LeafNode("span", "c")])
        with self.assertRaises(ValueError):
            parent.to_html()

    def test_text(self):
        node = TextNode("This is a text node", TextType.PLAIN_TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_bold(self):
        node = TextNode("boldy", TextType.BOLD_TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "boldy")

    def test_italic(self):
        node = TextNode("it", TextType.ITALIC_TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "i")

    def test_code(self):
        node = TextNode("print(1)", TextType.CODE_TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "code")

    def test_link(self):
        node = TextNode("Click", TextType.LINK_TEXT, url="https://example.com")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.props, {"href": "https://example.com"})

    def test_text_node_to_html_node_plain(self):
        tn = TextNode("plain", TextType.PLAIN_TEXT)
        node = text_node_to_html_node(tn)
        self.assertIsInstance(node, LeafNode)
        self.assertIsNone(node.tag)
        self.assertEqual(node.value, "plain")

    def test_text_node_to_html_node_bold_italic_code(self):
        b = TextNode("bold", TextType.BOLD_TEXT)
        i = TextNode("ital", TextType.ITALIC_TEXT)
        c = TextNode("x=1", TextType.CODE_TEXT)
        self.assertEqual(text_node_to_html_node(b).to_html(), "<b>bold</b>")
        self.assertEqual(text_node_to_html_node(i).to_html(), "<i>ital</i>")
        self.assertEqual(text_node_to_html_node(c).to_html(), "<code>x=1</code>")

    def test_text_node_to_html_node_link(self):
        tn = TextNode("click", TextType.LINK_TEXT, url="https://ex.com")
        node = text_node_to_html_node(tn)
        self.assertEqual(node.to_html(), '<a href="https://ex.com">click</a>')

    def test_text_node_to_html_node_unsupported_raises(self):
        # pick an enum member we didn't implement, e.g. UNDERLINE_TEXT
        tn = TextNode("u", TextType.UNDERLINE_TEXT)
        with self.assertRaises(ValueError):
            text_node_to_html_node(tn)


if __name__ == "__main__":
    unittest.main()
