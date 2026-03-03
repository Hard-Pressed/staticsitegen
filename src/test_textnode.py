import unittest

from textnode import TextNode, TextType


class TestTextNode(unittest.TestCase):
    def test_eq_same_text_type_and_url(self):
        node1 = TextNode("This is a text node", TextType.BOLD_TEXT, "https://example.com")
        node2 = TextNode("This is a text node", TextType.BOLD_TEXT, "https://example.com")
        self.assertEqual(node1, node2)

    def test_not_eq_different_text(self):
        node1 = TextNode("Text A", TextType.PLAIN_TEXT)
        node2 = TextNode("Text B", TextType.PLAIN_TEXT)
        self.assertNotEqual(node1, node2)

    def test_not_eq_different_text_type(self):
        node1 = TextNode("Same text", TextType.PLAIN_TEXT)
        node2 = TextNode("Same text", TextType.ITALIC_TEXT)
        self.assertNotEqual(node1, node2)

    def test_eq_both_urls_none(self):
        node1 = TextNode("No URL", TextType.LINK_TEXT, None)
        node2 = TextNode("No URL", TextType.LINK_TEXT, None)
        self.assertEqual(node1, node2)

    def test_not_eq_one_url_none(self):
        node1 = TextNode("Link", TextType.LINK_TEXT, None)
        node2 = TextNode("Link", TextType.LINK_TEXT, "https://example.com")
        self.assertNotEqual(node1, node2)


if __name__ == "__main__":
    unittest.main()