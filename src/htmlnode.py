class HTMLNode:
	def __init__(self, tag=None, value=None, children=None, props=None):
		self.tag = tag
		self.value = value
		self.children = children
		self.props = props

	def to_html(self):
		raise NotImplementedError()

	def props_to_html(self):
		if not self.props:
			return ""

		return "".join([f' {key}="{value}"' for key, value in self.props.items()])

	def __repr__(self):
		return f"HTMLNode(tag={self.tag!r}, value={self.value!r}, children={self.children!r}, props={self.props!r})"


class LeafNode(HTMLNode):
	def __init__(self, tag, value, props=None):
		super().__init__(tag=tag, value=value, children=None, props=props)

	def __repr__(self):
		return f"LeafNode(tag={self.tag!r}, value={self.value!r}, props={self.props!r})"

	def to_html(self):
		if self.value is None:
			raise ValueError("All leaf nodes must have a value")

		if self.tag is None:
			return self.value

		return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"


class ParentNode(HTMLNode):
	def __init__(self, tag, children, props=None):
		# tag and children are required; ParentNode does not take a value
		super().__init__(tag=tag, value=None, children=children, props=props)

	def to_html(self):
		if self.tag is None:
			raise ValueError("Parent nodes must have a tag")

		if self.children is None:
			raise ValueError("Parent nodes must have children")

		inner_parts = []
		for child in self.children:
			if hasattr(child, "to_html"):
				inner_parts.append(child.to_html())
			else:
				inner_parts.append(str(child))

		inner = "".join(inner_parts)
		return f"<{self.tag}{self.props_to_html()}>{inner}</{self.tag}>"


def text_node_to_html_node(text_node):
	"""Convert a TextNode to a LeafNode according to TextType.

	Handles multiple TextType naming conventions (e.g., PLAIN_TEXT or TEXT).
	"""
	tt_name = getattr(text_node.text_type, "name", None)
	if tt_name is None:
		raise ValueError("Invalid TextNode: missing text_type")

	name = tt_name.upper()

	# Map possible names to handlers
	if name in ("PLAIN_TEXT", "TEXT"):
		return LeafNode(None, text_node.text)
	if name in ("BOLD_TEXT", "BOLD"):
		return LeafNode("b", text_node.text)
	if name in ("ITALIC_TEXT", "ITALIC"):
		return LeafNode("i", text_node.text)
	if name in ("CODE_TEXT", "CODE"):
		return LeafNode("code", text_node.text)
	if name in ("LINK_TEXT", "LINK"):
		return LeafNode("a", text_node.text, props={"href": text_node.url})
	if name in ("IMAGE", "IMAGE_TEXT", "IMAGE_TEXT", "IMG"):
		return LeafNode("img", "", props={"src": text_node.url, "alt": text_node.text})

	raise ValueError(f"Unhandled TextType: {text_node.text_type}")


def text_node_to_html_node_new(text_node):
	"""Convert a TextNode into a LeafNode according to TextType mappings.

	Supported mappings (based on `TextType` in `src/textnode.py`):
	- PLAIN_TEXT -> raw text (no tag)
	- BOLD_TEXT -> <b>
	- ITALIC_TEXT -> <i>
	- CODE_TEXT -> <code>
	- LINK_TEXT -> <a href="...">
	- IMAGE (if present in the TextType enum) -> <img src="..." alt="..." /> (value is empty string)

	Raises ValueError for unsupported text types.
	"""
	from textnode import TextType, TextNode

	if not isinstance(text_node, TextNode):
		raise TypeError("text_node must be a TextNode")

	t = text_node.text_type

	if t == TextType.PLAIN_TEXT:
		return LeafNode(None, text_node.text)

	if t == TextType.BOLD_TEXT:
		return LeafNode("b", text_node.text)

	if t == TextType.ITALIC_TEXT:
		return LeafNode("i", text_node.text)

	if t == TextType.CODE_TEXT:
		return LeafNode("code", text_node.text)

	if t == TextType.LINK_TEXT:
		return LeafNode("a", text_node.text, props={"href": text_node.url})

	# Optional IMAGE support if the enum defines it
	image_type = getattr(TextType, "IMAGE", None) or getattr(TextType, "IMAGE_TEXT", None)
	if image_type is not None and t == image_type:
		# prefer url as src if present, otherwise use text as src
		src = text_node.url or text_node.text
		return LeafNode("img", "", props={"src": src, "alt": text_node.text})

	raise ValueError(f"Unsupported TextType: {t}")