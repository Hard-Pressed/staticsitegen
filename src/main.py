def main():
	from pathlib import Path
	import sys

	# Ensure `src` (this file's directory) is on sys.path so we can import local modules
	sys.path.insert(0, str(Path(__file__).resolve().parent))

	from textnode import TextNode, TextType

	# Create a TextNode with dummy values
	node = TextNode("dummy text", text_type=TextType.BOLD_TEXT, url=None)
	print(node)


if __name__ == "__main__":
	main()
