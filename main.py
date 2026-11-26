import json
import os
from time import sleep
from typing import Literal

import uvicorn
from datastar_py.fastapi import (
    DatastarResponse,
    ReadSignals,
    datastar_response,
    read_signals,
)
from datastar_py.fastapi import ServerSentEventGenerator as SSE
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader
from rich import print

from services.db import db
from services.markdown_html_factory import md_html_factory as md_html

# ================= NOTES GERO TO DO, FIX ME and ELSE ===============================================

# TODO: IMPORTANT -> ADD AUTHENTICATION AND AUTHORIZATION to every path!
# TODO: ADD Cache for operations related to DB and others :)
# TODO: In Blog route, the description of the blog post, -> render that correctly as HTML, not MD

# ===================================================================================================


# UTILITIES
# ===================================================================================================
def print_sep(to_print: str | list) -> Literal[0]:
    is_str = isinstance(to_print, str)
    is_list = isinstance(to_print, list)
    if is_str:
        print("=" * 120)
        print(to_print)
        print("=" * 120)
    elif is_list:
        print("=" * 120)
        for e in to_print:
            print(e)
        print("=" * 120)

    return 0


def write_to_log_file(data: str):
    with open("log.log", "a+") as log_file:
        log_file.write(data)
    return {"message": "WROTE to LOG FILE"}


# ===================================================================================================


# --- APP INIT ---
app = FastAPI(title="Gero Zayas")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(
    env=Environment(
        loader=FileSystemLoader(
            [
                "templates",
                "templates/jinja_components",
                "data/blog_posts",
            ]
        )
    )
)

origins = [
    "http://localhost:8000",
    "https://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=500)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = (
        "max-age=63072000; includeSubDomains"
    )
    response.headers["X-Content-Type-Options"] = "nosnif"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-eval' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "img-src 'self' data:; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
    )
    return response


# --- ROUTES ---
@app.get("/")
@app.get("/home")
def home(request: Request):
    context = {"message": "hello world, this is working"}
    return templates.TemplateResponse(
        request=request, name="home.html", context=context
    )


@app.get("/about")
def about(request: Request):
    context = {"message": "hello world, this is about page"}
    return templates.TemplateResponse(
        request=request, name="about.html", context=context
    )


@app.get("/projects")
def projects(request: Request):
    dict_db_projects_entries = db.execute_query(
        db.SELECT_QUERY, table="projects", values={}
    )

    context = {
        "message": "hello world, this is about page",
        "projects": dict_db_projects_entries,
    }
    return templates.TemplateResponse(
        request=request, name="projects.html", context=context
    )


# BLOG ROUTES ------------------------------------------------------------------------------
def return_dict_db_blog_entries():
    dict_db_blog_entries = db.execute_query(
        db.SELECT_QUERY, table="gero_blog", values={}
    )
    return dict_db_blog_entries


def return_blog_entries_tags_set():
    dict_db_blog_entries_tags_set = set()
    # dict_db_blog_entries_tags_set.add("all")
    dict_db_blog_entries_tags = [
        [dict_db_blog_entries_tags_set.add(t) for t in d["tags"].split(",")]
        for d in return_dict_db_blog_entries()
    ]
    print("dict_db_blog_entries_tags", dict_db_blog_entries_tags_set)
    return dict_db_blog_entries_tags_set


# ***A
@app.get("/blog")
async def blog(request: Request, signals: ReadSignals):
    context = {
        "message": "This is blog page",
        "blog_posts": return_dict_db_blog_entries(),
        "tags": return_blog_entries_tags_set(),
    }
    return templates.TemplateResponse(
        request=request, name="blog.html", context=context
    )


# TODO: Poner lista de tags clickables
# TODO: cuando se click en un tag, que el search_term adopte ese valor


def blog_post_stream(
    search_term: str, selected_tag: str = "all", current_page: int = 1
):
    blog_post_card_classes = (
        "items-center flex max-w-l overflow-hidden rounded-lg bg-linear-to-r from-white to-slate-50 transition-all ",
        "duration-300 ease-in-out border border-gray-100 ",
    )
    html = """<div id="blog-posts-cards-area" 
        class="grid grid-cols-1 gap-3">"""

    PAGE_SIZE = 5
    PAGE_START = current_page * PAGE_SIZE - PAGE_SIZE
    PAGE_END = PAGE_START + PAGE_SIZE

    print("TYPE OF SELECTED TAG", type(selected_tag))

    if selected_tag != "all":
        selected_titles = [
            post
            for post in return_dict_db_blog_entries()
            if selected_tag.lower() in post["tags"].lower()
        ]
    else:
        selected_titles = [
            post
            for post in return_dict_db_blog_entries()
            if search_term.lower() in post["title"].lower()
            or search_term.lower() in post["tags"].lower()
        ]

    print("=================")
    print("selected_titles")
    print(selected_titles)
    print("=================")

    for post in selected_titles[PAGE_START:PAGE_END]:
        html += f"""
                <div class="{blog_post_card_classes}">
                    <div class="p-2 pl-5">
                        <a href="blog/{post["id"]}"
                            class="font-bold text-lg text-red-700 transition-all duration-300 ease-in-out hover:underline hover:text-red-900">
                            {post["title"]}
                        </a>
                        <p class="mt-2 text-xs text-gray-600">{post["tags"]}</p>
                        <p class="text-xs text-yellow-600">{post["created_at"]}</p>
                    </div>
                </div>
                """
        # html += "<br>"

    html += """</div>"""
    yield SSE.patch_elements(html)
    yield SSE.patch_signals({"remaining": len(selected_titles) - PAGE_END})


@app.get("/blog-post-card-render", response_class=StreamingResponse)
async def blog_post_card_render(request: Request, signals: ReadSignals):
    print("==== SIGNALS ====", signals)
    return DatastarResponse(
        blog_post_stream(
            signals["searchTerm"], signals["selected-tag"], signals["current-page"]
        )
    )


@app.get("/blog/{blog_id}")
def blog_post(blog_id: str, request: Request):
    blog_post = {
        "id": blog_id,
    }
    context = {
        "message": "hello world, this is blog page",
        "blog_post": blog_post,
    }
    return templates.TemplateResponse(
        request=request, name="blog_post.html", context=context
    )


@app.get("/blog-post-creator")
async def blog_post_creator(request: Request):
    context = {"message": "hello world, this is blog page", "blog_post": ""}
    return templates.TemplateResponse(
        request=request, name="blog_post_creator.html", context=context
    )


@datastar_response
@app.post("/blog-post-creator-submit-content")
async def blog_post_creator_insert_new_post(signals: ReadSignals):
    print("*" * 100)
    title = (signals.get("blogPostCreatorTitle")).strip()  # type: ignore
    content = (signals.get("blogPostCreatorContent")).strip()  # type: ignore
    tags = [e.strip() for e in (signals.get("blogPostCreatorTags")).split(",")]  # type: ignore
    lang = signals.get("blogPostCreatorLang").strip()  # type: ignore

    print(title)
    print(content)
    print(tags)
    print(lang)
    new_blog_post_data = {
        "title": title,
        "content": content,
        "tags": ",".join(tags),
        "lang": lang.upper(),
    }

    print_sep(tags)

    res_insert = db.insert_row_to_blog_db(data=new_blog_post_data)

    log_message = """
    CALLING:
    `db.insert_row_to_db(data=new_blog_post_data)`
    Opening DB and WRITING to it.
    """
    write_to_log_file(log_message)

    print(res_insert)
    # TODO: add a patch signals piece of logic to see confirmation in the frontend
    print("*" * 100)


# EXAMPLE FROM DOCS:
# ------------------
# @app.get('/do-you-read-me')
# @datastar_response
# async def open_doors(request):
#     yield SSE.patch_signals({"hal": "Affirmative, Dave. I read you."})
#     await asyncio.sleep(1)
#     yield SSE.patch_signals({"hal": "..."})


@app.post("/blog-post-creator-delete-post/{blog_id}")
async def blog_post_creator_delete(blog_id: int, request: Request):
    res_delete = db.delete_row_in_blog_db(row_id=blog_id)
    print(res_delete)
    # TODO: add a patch signals piece of logic to see confirmation in the frontend
    return {"status": "OK", "action_completed": f"deleted blog id: {blog_id}"}


# end of BLOG ROUTES ------------------------------------------------------------------------------


@app.get("/project-creator")
async def project_creator(request: Request):
    context = {"message": "hello world, this is the project page", "project": ""}
    return templates.TemplateResponse(
        request=request, name="project_creator.html", context=context
    )


@datastar_response
@app.post("/project-creator-submit-content")
async def project_creator_insert_new_project(signals: ReadSignals):
    print("*" * 100)
    name = (signals.get("projectCreatorName")).strip()  # type: ignore
    description = (signals.get("projectCreatorDescription")).strip()  # type: ignore
    tags = [e.strip() for e in (signals.get("projectCreatorTags")).split(",")]  # type: ignore
    link = signals.get("projectCreatorLink").strip()  # type: ignore

    new_project_data = {
        "name": name,
        "description": description,
        "tags": ",".join(tags),
        "link": link,
    }

    print_sep(tags)

    res_insert = db.insert_row_to_projects_table_db(data=new_project_data)

    log_message = """
    CALLING:
    `db.insert_row_to_db(data=new_project_data)`
    Opening DB and WRITING to it.
    """
    write_to_log_file(log_message)

    print(res_insert)
    # TODO: add a patch signals piece of logic to see confirmation in the frontend
    print("*" * 100)


@app.get("/resources")
def resources(request: Request):
    context = {"message": "hello world, this is resources", "resources": {}}
    return templates.TemplateResponse(
        request=request, name="resources.html", context=context
    )


@app.get("/list-db-blog-entries")
def list_db_blog_entries(request: Request):
    res = db.execute_query(db.SELECT_QUERY, table="gero_blog", values=())
    return {"res": res}


# --- EXECUTING  ---

if __name__ == "__main__":
    PORT = "8000"
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", PORT)),
        reload=True,
    )
