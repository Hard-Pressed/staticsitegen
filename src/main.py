def main():
	from pathlib import Path
	import sys

	# Ensure `src` (this file's directory) is on sys.path so we can import local modules
	sys.path.insert(0, str(Path(__file__).resolve().parent))

	from textnode import TextNode, TextType

	# Create a TextNode with dummy values
	node = TextNode("dummy text", text_type=TextType.BOLD_TEXT, url=None)
	print(node)

	# Copy static site assets into `public/`
	try:
		from copy_static import copy_static_to_public
		print("Copying static files to public/...")
		copy_static_to_public()
		print("Finished copying static files to public/.")
	except Exception as e:
		print(f"Failed to copy static files: {e}")


if __name__ == "__main__":
	main()
