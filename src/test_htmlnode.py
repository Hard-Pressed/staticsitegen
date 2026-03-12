import unittest

from htmlnode import (
    HTMLNode,
    LeafNode,
    ParentNode,
    extract_title,
    text_node_to_html_node,
    split_nodes_delimiter,
    split_nodes_link,
    split_nodes_image,
    text_to_textnodes,
    markdown_to_html_node,
)
from textnode import TextNode, TextType
from htmlnode import extract_markdown_images, extract_markdown_links
from htmlnode import markdown_to_blocks



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

    def test_extract_markdown_images(self):
        text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        imgs = extract_markdown_images(text)
        self.assertEqual(
            imgs,
            [("rick roll", "https://i.imgur.com/aKaOqIh.gif"), ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg")],
        )

    def test_extract_markdown_images_single(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_markdown_links(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        links = extract_markdown_links(text)
        self.assertEqual(
            links,
            [("to boot dev", "https://www.boot.dev"), ("to youtube", "https://www.youtube.com/@bootdotdev")],
        )

    def test_split_nodes_delimiter_basic(self):
        node = TextNode("This is text with a `code block` word", TextType.PLAIN_TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE_TEXT)
        self.assertEqual(len(new_nodes), 3)
        self.assertEqual(new_nodes[0].text, "This is text with a ")
        self.assertEqual(new_nodes[0].text_type, TextType.PLAIN_TEXT)
        self.assertEqual(new_nodes[1].text, "code block")
        self.assertEqual(new_nodes[1].text_type, TextType.CODE_TEXT)
        self.assertEqual(new_nodes[2].text, " word")
        self.assertEqual(new_nodes[2].text_type, TextType.PLAIN_TEXT)

    def test_split_nodes_delimiter_no_delimiter(self):
        node = TextNode("no delim here", TextType.PLAIN_TEXT)
        out = split_nodes_delimiter([node], "`", TextType.CODE_TEXT)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].text, "no delim here")

    def test_split_nodes_delimiter_unmatched_raises(self):
        node = TextNode("starts ` but no end", TextType.PLAIN_TEXT)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "`", TextType.CODE_TEXT)

    def test_split_nodes_delimiter_preserves_non_text(self):
        leaf = LeafNode("p", "x")
        node = TextNode("plain", TextType.PLAIN_TEXT)
        out = split_nodes_delimiter([leaf, node], "`", TextType.CODE_TEXT)
        # leaf should be preserved as-is and text node should be converted
        self.assertIs(out[0], leaf)
        self.assertIsInstance(out[1], TextNode)

    def test_split_nodes_link_basic(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.PLAIN_TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertEqual(len(new_nodes), 4)
        self.assertEqual(new_nodes[0].text, "This is text with a link ")
        self.assertEqual(new_nodes[1].text, "to boot dev")
        self.assertEqual(new_nodes[1].text_type, TextType.LINK_TEXT)
        self.assertEqual(new_nodes[1].url, "https://www.boot.dev")
        self.assertEqual(new_nodes[2].text, " and ")
        self.assertEqual(new_nodes[3].text, "to youtube")
        self.assertEqual(new_nodes[3].url, "https://www.youtube.com/@bootdotdev")

    def test_split_nodes_image_basic(self):
        node = TextNode(
            "This is text with an image ![alt](https://i.imgur.com/zjjcJKZ.png)",
            TextType.PLAIN_TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertEqual(len(new_nodes), 2)
        self.assertEqual(new_nodes[0].text, "This is text with an image ")
        self.assertEqual(new_nodes[1].text, "alt")
        self.assertEqual(new_nodes[1].text_type, TextType.IMAGE)
        self.assertEqual(new_nodes[1].url, "https://i.imgur.com/zjjcJKZ.png")

    def test_split_images_multiple(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.PLAIN_TEXT,
        )
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("This is text with an ", TextType.PLAIN_TEXT),
            TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
            TextNode(" and another ", TextType.PLAIN_TEXT),
            TextNode("second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_text_to_textnodes_complex(self):
        src = (
            "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        )
        nodes = text_to_textnodes(src)
        expected = [
            TextNode("This is ", TextType.PLAIN_TEXT),
            TextNode("text", TextType.BOLD_TEXT),
            TextNode(" with an ", TextType.PLAIN_TEXT),
            TextNode("italic", TextType.ITALIC_TEXT),
            TextNode(" word and a ", TextType.PLAIN_TEXT),
            TextNode("code block", TextType.CODE_TEXT),
            TextNode(" and an ", TextType.PLAIN_TEXT),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.PLAIN_TEXT),
            TextNode("link", TextType.LINK_TEXT, "https://boot.dev"),
        ]
        self.assertEqual(nodes, expected)

    def test_split_nodes_link_unmatched_raises(self):
        node = TextNode("start [unclosed", TextType.PLAIN_TEXT)
        with self.assertRaises(ValueError):
            split_nodes_link([node])

    def test_split_nodes_image_unmatched_raises(self):
        node = TextNode("broken ![alt](no closing", TextType.PLAIN_TEXT)
        with self.assertRaises(ValueError):
            split_nodes_image([node])

    def test_markdown_to_blocks(self):
        md = """# Heading

This is a paragraph.

- item 1
- item 2
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["# Heading", "This is a paragraph.", "- item 1\n- item 2"])    

    def test_markdown_to_blocks_strips_and_ignores_empty(self):
        md = "\n\n  # Hi  \n\n\n  \nParagraph  \n\n"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["# Hi", "Paragraph"]) 

    def test_markdown_to_blocks_multiple_double_newlines(self):
        md = "A\n\nB\n\n\n\nC"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["A", "B", "C"]) 

    def test_markdown_to_blocks_empty_or_none(self):
        self.assertEqual(markdown_to_blocks(""), [])
        self.assertEqual(markdown_to_blocks(None), [])

    def test_extract_title_returns_h1_text(self):
        self.assertEqual(extract_title("# Hello"), "Hello")

    def test_extract_title_strips_whitespace(self):
        self.assertEqual(extract_title("#   Hello World   "), "Hello World")

    def test_extract_title_ignores_non_h1_headers(self):
        markdown = "## Subtitle\n\n# Real Title\n\nParagraph text"
        self.assertEqual(extract_title(markdown), "Real Title")

    def test_extract_title_raises_without_h1(self):
        markdown = "## Subtitle\n\nParagraph text"
        with self.assertRaises(ValueError):
            extract_title(markdown)

    def test_markdown_to_html_node_heading_and_paragraph(self):
        md = "# Hello\n\nThis is **bold** and _italic_."
        root = markdown_to_html_node(md)
        self.assertEqual(
            root.to_html(),
            "<div><h1>Hello</h1><p>This is <b>bold</b> and <i>italic</i>.</p></div>",
        )

    def test_markdown_to_html_node_list(self):
        md = "- one\n- two\n- three"
        root = markdown_to_html_node(md)
        self.assertEqual(root.to_html(), "<div><ul><li>one</li><li>two</li><li>three</li></ul></div>")

    def test_markdown_to_html_node_code_block(self):
        md = "```\nprint(1)\n```"
        root = markdown_to_html_node(md)
        self.assertEqual(root.to_html(), "<div><pre><code>print(1)</code></pre></div>")

    def test_markdown_to_html_node_blockquote(self):
        md = "> This is a quote"
        root = markdown_to_html_node(md)
        self.assertEqual(root.to_html(), "<div><blockquote>This is a quote</blockquote></div>")

    def test_markdown_to_html_node_image_and_link(self):
        md = "This has an ![alt](https://img) and a [link](https://ex)"
        root = markdown_to_html_node(md)
        self.assertEqual(
            root.to_html(),
            "<div><p>This has an <img src=\"https://img\" alt=\"alt\" /> and a <a href=\"https://ex\">link</a></p></div>",
        )


if __name__ == "__main__":
    unittest.main()
