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


def extract_markdown_images(text: str):
	"""Return list of (alt, url) tuples for markdown images in `text`.

	Matches patterns like: ![alt text](https://example.com/img.png)
	"""
	import re

	pattern = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
	results = []
	for m in pattern.finditer(text or ""):
		alt = m.group(1)
		url = m.group(2)
		results.append((alt, url))

	return results


def extract_markdown_links(text: str):
	"""Return list of (anchor, url) tuples for markdown links in `text`.

	Matches patterns like: [anchor text](https://example.com)
	"""
	import re

	pattern = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
	results = []
	for m in pattern.finditer(text or ""):
		anchor = m.group(1)
		url = m.group(2)
		results.append((anchor, url))

	return results

def split_nodes_delimiter(old_nodes, delimiter, text_type):
	"""Split text nodes on a delimiter and return a new list of nodes.

	- `old_nodes`: list of nodes (expected TextNode objects for splitting)
	- `delimiter`: a string delimiter to split on (e.g. "`")
	- `text_type`: the TextType to use for the delimited segments

	Rules:
	- Only split nodes whose TextType is a plain/text type (e.g. PLAIN_TEXT or TEXT).
	- If an old node is not a text/plain node, append it unchanged.
	- If the number of delimiters in a text node is odd, raise ValueError (unmatched delimiter).
	- Returns a new list of TextNode and other nodes.
	"""
	from textnode import TextNode, TextType

	new_nodes = []
	for node in old_nodes:
		# Only attempt to split TextNode objects
		if not isinstance(node, TextNode):
			new_nodes.append(node)
			continue

		tt_name = getattr(node.text_type, "name", "").upper()
		if tt_name not in ("PLAIN_TEXT", "TEXT"):
			# Not a plain text node; leave as-is
			new_nodes.append(node)
			continue

		text = node.text
		if delimiter == "":
			raise ValueError("Delimiter must be a non-empty string")

		count = text.count(delimiter)
		if count == 0:
			new_nodes.append(node)
			continue

		if count % 2 != 0:
			raise ValueError(f"Unmatched delimiter '{delimiter}' in text: {text!r}")

		parts = text.split(delimiter)
		# parts alternates: plain, delimited, plain, delimited, ...
		for idx, part in enumerate(parts):
			if idx % 2 == 0:
				# plain text segment
				new_nodes.append(TextNode(part, TextType.PLAIN_TEXT))
			else:
				# delimited segment -> use provided text_type
				new_nodes.append(TextNode(part, text_type))

	return new_nodes


def split_nodes_link(old_nodes):
	"""Split plain text nodes into link nodes for markdown links.

	Converts text like 'a [link](url) b' into three TextNode objects:
	plain, link (TextType.LINK_TEXT with url), plain.
	"""
	from textnode import TextNode, TextType
	import re

	pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

	new_nodes = []
	for node in old_nodes:
		if not isinstance(node, TextNode):
			new_nodes.append(node)
			continue

		tt_name = getattr(node.text_type, "name", "").upper()
		if tt_name not in ("PLAIN_TEXT", "TEXT"):
			new_nodes.append(node)
			continue

		text = node.text
		# Basic unmatched check: brackets/parentheses counts
		if text.count("[") != text.count("]") or text.count("(") != text.count(")"):
			raise ValueError(f"Unmatched link syntax in text: {text!r}")

		matches = list(pattern.finditer(text))
		if not matches:
			new_nodes.append(node)
			continue

		pos = 0
		for m in matches:
			if m.start() > pos:
				new_nodes.append(TextNode(text[pos : m.start()], TextType.PLAIN_TEXT))
			anchor = m.group(1)
			url = m.group(2)
			new_nodes.append(TextNode(anchor, TextType.LINK_TEXT, url=url))
			pos = m.end()

		if pos < len(text):
			new_nodes.append(TextNode(text[pos:], TextType.PLAIN_TEXT))

	return new_nodes


def split_nodes_image(old_nodes):
	"""Split plain text nodes into image nodes for markdown images.

	Converts text like 'a ![alt](url) b' into three TextNode objects:
	plain, image (TextNode with text=alt and url set), plain.
	"""
	from textnode import TextNode, TextType
	import re

	pattern = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")

	new_nodes = []
	for node in old_nodes:
		if not isinstance(node, TextNode):
			new_nodes.append(node)
			continue

		tt_name = getattr(node.text_type, "name", "").upper()
		if tt_name not in ("PLAIN_TEXT", "TEXT"):
			new_nodes.append(node)
			continue

		text = node.text
		# Basic unmatched check: '![' without matching ')'
		if text.count("![") != text.count(")"):
			# crude but effective for common malformed cases
			if text.count("![") > 0:
				raise ValueError(f"Unmatched image syntax in text: {text!r}")

		matches = list(pattern.finditer(text))
		if not matches:
			new_nodes.append(node)
			continue

		pos = 0
		for m in matches:
			if m.start() > pos:
				new_nodes.append(TextNode(text[pos : m.start()], TextType.PLAIN_TEXT))
			alt = m.group(1)
			url = m.group(2)
			# Use the TextNode with alt text and url in the url field
			new_nodes.append(TextNode(alt, TextType.IMAGE, url=url))
			pos = m.end()

		if pos < len(text):
			new_nodes.append(TextNode(text[pos:], TextType.PLAIN_TEXT))

	return new_nodes