"""
This small program generates all the blog posts as html files and saves them into data/blog_posts
So they can be included in Jinja templates
"""

from pathlib import Path

from rich import print

from services.db import db
from services.markdown_html_factory import md_html_factory as md

title = "title"
the_id = "id"
tags = "tags"
content = "content"
lang = "lang"

rows = db.execute_query(db.SELECT_QUERY, ())


def save_blog_post_to_html_file(id: str, data: str):
    blog_posts_path = Path("data/blog_posts")
    print(blog_posts_path)
    with open(f"{blog_posts_path}/{id}.html", "w") as file:
        file.write(
            "{% raw %}\n"
        )  # we add this so we have no problem rendering it with jinja
        file.write(data)
        file.write("\n{% endraw %}")


for row in rows:
    html = md.render_markdown_html(source=row[content])
    save_blog_post_to_html_file(row[the_id], html)
    print("*" * 100)
