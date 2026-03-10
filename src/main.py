def main():
	from pathlib import Path
	import sys

	# Ensure `src` (this file's directory) is on sys.path so we can import local modules
	sys.path.insert(0, str(Path(__file__).resolve().parent))

	from textnode import TextNode, TextType
	# import markdown/site helpers
	from htmlnode import markdown_to_html_node, extract_title
	import os

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

	# generate a page from content/index.md -> public/index.html using template.html
	def generate_page(from_path, template_path, dest_path):
		print(f"Generating page from {from_path} to {dest_path} using {template_path}")
		# read markdown
		with open(from_path, "r", encoding="utf-8") as f:
			md = f.read()

		# read template
		with open(template_path, "r", encoding="utf-8") as f:
			tpl = f.read()

		# convert markdown to HTML string
		html_node = markdown_to_html_node(md)
		content_html = html_node.to_html()

		# extract title
		title = extract_title(md)

		# replace placeholders (handle common casing variants)
		out = tpl.replace("{{ Title }}", title).replace("{{ Content }}", content_html)
		out = out.replace("{{ title }}", title).replace("{{ content }}", content_html)

		# ensure destination directory exists
		dirname = os.path.dirname(dest_path)
		if dirname:
			os.makedirs(dirname, exist_ok=True)

		# write output
		with open(dest_path, "w", encoding="utf-8") as f:
			f.write(out)

	# Attempt to generate the main page
	try:
		generate_page("content/index.md", "template.html", "public/index.html")
		print("Generated public/index.html")
	except Exception as e:
		print(f"Failed to generate page: {e}")


if __name__ == "__main__":
	main()
