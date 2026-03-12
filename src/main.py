import os
import sys
from pathlib import Path

# Ensure `src` (this file's directory) is on sys.path so we can import local modules.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from copy_static import copy_static_to_public
from htmlnode import extract_title, markdown_to_html_node


def generate_page(from_path, template_path, dest_path, basepath):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    with open(from_path, "r", encoding="utf-8") as f:
        markdown = f.read()

    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    content_html = markdown_to_html_node(markdown).to_html()
    title = extract_title(markdown)

    page_html = template.replace("{{ Title }}", title).replace("{{ Content }}", content_html)
    page_html = page_html.replace("{{ title }}", title).replace("{{ content }}", content_html)
    page_html = page_html.replace('href="/', f'href="{basepath}')
    page_html = page_html.replace('src="/', f'src="{basepath}')

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(page_html)


def generate_pages_recursive(content_dir, template_path, dest_dir, basepath):
    """Generate one HTML page for every markdown file under content_dir."""
    for root, _, files in os.walk(content_dir):
        for filename in files:
            if not filename.endswith(".md"):
                continue

            from_path = os.path.join(root, filename)
            rel_path = os.path.relpath(from_path, content_dir)
            html_rel_path = os.path.splitext(rel_path)[0] + ".html"
            dest_path = os.path.join(dest_dir, html_rel_path)
            generate_page(from_path, template_path, dest_path, basepath)


def main():
    basepath = sys.argv[1] if len(sys.argv) > 1 else "/"
    if not basepath.startswith("/"):
        basepath = f"/{basepath}"
    if not basepath.endswith("/"):
        basepath = f"{basepath}/"

    print("Copying static files to docs/...")
    copy_static_to_public(dst_dir="docs")
    print("Finished copying static files to docs/.")

    generate_pages_recursive("content", "template.html", "docs", basepath)
    print("Finished generating pages.")


if __name__ == "__main__":
    main()
