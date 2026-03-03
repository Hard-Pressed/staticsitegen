from enum import Enum

class TextType(Enum):
    PLAIN_TEXT = 1
    BOLD_TEXT = 2
    ITALIC_TEXT = 3
    UNDERLINE_TEXT = 4
    STRIKETHROUGH_TEXT = 5
    LINK_TEXT = 6
    CODE_TEXT = 7
    QUOTE_TEXT = 8
    HIGHLIGHTED_TEXT = 9
    SUBSCRIPT_TEXT = 10
    SUPERSCRIPT_TEXT = 11

class TextNode:
    def __init__(self, text: str, text_type: TextType = TextType.PLAIN_TEXT, url: str = None):
        self.text = text
        self.text_type = text_type
        self.url = url  # Used only for LINK_TEXT

    def __eq__(self, other):
        if not isinstance(other, TextNode):
            return NotImplemented
        return (
            self.text == other.text
            and self.text_type == other.text_type
            and self.url == other.url
        )
    def __repr__(self):
        return f"TextNode(text={self.text!r}, text_type={self.text_type}, url={self.url!r})"