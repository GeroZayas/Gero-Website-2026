import markdown
from rich import print


def render_markdown_html(source):
    """CONVERTS MD Doc to HTML"""
    md = markdown.Markdown(
        extensions=[
            "extra",
            "toc",
            "codehilite",
        ],
        extension_configs={
            "codehilite": {
                "guess_lang": False,
                "use_pygments": True,
            },
        },
    )

    return md.convert(source)


def main():
    src = ""

    with open("data/blog_posts/test.md", "r") as file:
        src = file.read()

    html = render_markdown_html(source=src)
    with open("test.html", "w") as file:
        file.write(html)
        print(f"WROTE {len(html)} into file.")


if __name__ == "__main__":
    main()
