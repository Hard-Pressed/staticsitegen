from enum import Enum
from typing import Optional


class BlockType(Enum):
	PARAGRAPH = "paragraph"
	HEADING = "heading"
	CODE = "code"
	QUOTE = "quote"
	UNORDERED_LIST = "unordered_list"
	ORDERED_LIST = "ordered_list"


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


def markdown_to_blocks(markdown: Optional[str]):
	"""Split a markdown document into top-level blocks.

	Splits on double-newlines, strips whitespace, and removes empty blocks.
	"""
	if markdown is None:
		return []

	blocks = [b.strip() for b in markdown.split("\n\n")]
	return [b for b in blocks if b]


def extract_title(markdown: str):
	"""Return the text of the first h1 heading in a markdown document.

	An h1 heading is a line that begins with exactly one '#'. The leading '#'
	and surrounding whitespace are removed from the returned title.
	"""
	for line in markdown.splitlines():
		stripped = line.strip()
		if stripped.startswith("#") and not stripped.startswith("##"):
			title = stripped[1:].strip()
			if title:
				return title

	raise ValueError("Markdown document does not contain an h1 header")

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
		# Validate that any '![' occurrences are well-formed: must have ']' then '(' then ')'
		idx = text.find('![')
		while idx != -1:
			close_br = text.find(']', idx + 2)
			if close_br == -1:
				raise ValueError(f"Unmatched image syntax in text: {text!r}")
			# next char after ']' should be '('
			if close_br + 1 >= len(text) or text[close_br + 1] != '(':
				raise ValueError(f"Unmatched image syntax in text: {text!r}")
			close_paren = text.find(')', close_br + 2)
			if close_paren == -1:
				raise ValueError(f"Unmatched image syntax in text: {text!r}")
			idx = text.find('![', close_paren + 1)

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


def text_to_textnodes(text: str):
	"""Convert raw markdown-like text into a list of TextNode objects.

	The function applies several splitting passes to handle images, links,
	code spans, bold, and italic markers. It returns a list of TextNode
	instances using the TextType enum from `textnode`.
	"""
	from textnode import TextNode, TextType

	# start with a single plain text node
	nodes = [TextNode(text, TextType.PLAIN_TEXT)]

	# split images: ![alt](url)
	nodes = split_nodes_image(nodes)

	# split links: [text](url)
	nodes = split_nodes_link(nodes)

	# split code spans: `code`
	nodes = split_nodes_delimiter(nodes, "`", TextType.CODE_TEXT)

	# split bold: **bold**
	nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD_TEXT)

	# split italic: _italic_
	nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC_TEXT)

	return nodes


def text_to_children(text: str):
	"""Convert an inline markdown text string into a list of HTMLNode children.

	Uses `text_to_textnodes` to split inline elements, then converts each
	TextNode into an HTMLNode via `text_node_to_html_node`.
	"""
	from textnode import TextNode

	tnodes = text_to_textnodes(text)
	children = []
	for tn in tnodes:
		# convert each TextNode to an HTML LeafNode
		children.append(text_node_to_html_node(tn))
	return children


def determine_block_type(block: str):
	"""Return (BlockType, info) for a given block string.

	`info` may contain auxiliary data like heading level.
	"""
	stripped = block.lstrip()
	# code fence
	if stripped.startswith('```'):
		return BlockType.CODE, {}

	# heading: count leading # characters
	if stripped.startswith('#'):
		# count number of # at start
		i = 0
		while i < len(stripped) and stripped[i] == '#':
			i += 1
		# skip a single space if present
		return BlockType.HEADING, {"level": max(1, i)}

	# blockquote
	if stripped.startswith('>'):
		return BlockType.QUOTE, {}

	# unordered list (lines starting with - or *)
	lines = block.splitlines()
	if all(line.lstrip().startswith(('-', '*')) for line in lines if line.strip()):
		return BlockType.UNORDERED_LIST, {}

	# ordered list: lines starting with digit + '.'
	import re

	if all(re.match(r"^\s*\d+\.", line) for line in lines if line.strip()):
		return BlockType.ORDERED_LIST, {}

	return BlockType.PARAGRAPH, {}


def markdown_to_html_node(markdown: str):
	"""Convert a full markdown document into a single ParentNode ('div').

	Each top-level block becomes a child HTML node with appropriate tag and
	children representing inline content.
	"""
	blocks = markdown_to_blocks(markdown)
	children = []
	for block in blocks:
		btype, info = determine_block_type(block)

		if btype == BlockType.HEADING:
			# remove leading #'s and optional space
			stripped = block.lstrip()
			i = 0
			while i < len(stripped) and stripped[i] == '#':
				i += 1
			content = stripped[i:].lstrip()
			level = info.get("level", 1)
			tag = f"h{min(level,6)}"
			node_children = text_to_children(content)
			children.append(ParentNode(tag, node_children))
			continue

		if btype == BlockType.PARAGRAPH:
			node_children = text_to_children(block)
			children.append(ParentNode("p", node_children))
			continue

		if btype == BlockType.CODE:
			# code fence: extract content between fences
			lines = block.splitlines()
			# remove first and last fence lines if present
			if lines and lines[0].startswith('```'):
				# find closing fence
				end = None
				for idx in range(1, len(lines)):
					if lines[idx].startswith('```'):
						end = idx
						break
				if end is None:
					# no closing fence; take everything after the first line
					code_text = "\n".join(lines[1:])
				else:
					code_text = "\n".join(lines[1:end])
			else:
				code_text = block
			# create code TextNode and convert without inline parsing
			from textnode import TextNode, TextType

			code_tn = TextNode(code_text, TextType.CODE_TEXT)
			code_node = text_node_to_html_node(code_tn)
			# wrap in pre for block formatting
			children.append(ParentNode("pre", [code_node]))
			continue

		if btype == BlockType.QUOTE:
			# remove leading > and space
			lines = [l.lstrip()[1:].lstrip() if l.lstrip().startswith('>') else l for l in block.splitlines()]
			content = "\n".join(lines)
			node_children = text_to_children(content)
			children.append(ParentNode("blockquote", node_children))
			continue

		if btype == BlockType.UNORDERED_LIST:
			# each non-empty line becomes li
			items = []
			for line in block.splitlines():
				s = line.lstrip()
				if not s:
					continue
				if s.startswith(('-', '*')):
					item_text = s[1:].lstrip()
				else:
					item_text = s
				items.append(ParentNode("li", text_to_children(item_text)))
			children.append(ParentNode("ul", items))
			continue

		if btype == BlockType.ORDERED_LIST:
			items = []
			import re

			for line in block.splitlines():
				if not line.strip():
					continue
				m = re.match(r"^\s*\d+\.\s*(.*)$", line)
				item_text = m.group(1) if m else line.strip()
				items.append(ParentNode("li", text_to_children(item_text)))
			children.append(ParentNode("ol", items))
			continue

	return ParentNode("div", children)