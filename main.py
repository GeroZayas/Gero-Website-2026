import json
import os

import uvicorn
from datastar_py import ServerSentEventGenerator as SSE
from datastar_py.fastapi import ReadSignals, datastar_response, read_signals
from fastapi import Body, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader
from rich import print

from services.db import db

# TODO: IMPORTANT -> ADD AUTHENTICATION AND AUTHORIZATION to every path!

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
    projects = [
        "project 1",
        "project 2",
        "project 3",
    ]
    context = {"message": "hello world, this is about page", "projects": projects}
    return templates.TemplateResponse(
        request=request, name="projects.html", context=context
    )


# BLOG ROUTES ------------------------------------------------------------------------------


@app.get("/blog")
def blog(request: Request):
    dict_db_blog_entries = db.execute_query(db.SELECT_QUERY, ())
    context = {"message": "This is blog page", "blog_posts": dict_db_blog_entries}

    return templates.TemplateResponse(
        request=request, name="blog.html", context=context
    )


@app.get("/blog/{blog_id}")
def blog_post(blog_id: str, request: Request):
    selected_blog = blog_id
    print("selected_blog:", selected_blog)
    db.execute_query(db.READ_ROW, (blog_id,))

    context = {"message": "hello world, this is blog page", "blog_post": selected_blog}
    return templates.TemplateResponse(
        request=request, name="blog_post.html", context=context
    )


@app.get("/blog-post-creator")
async def blog_post_creator(request: Request):
    context = {"message": "hello world, this is blog page", "blog_post": ""}
    return templates.TemplateResponse(
        request=request, name="blog_post_creator.html", context=context
    )


@app.post("/blog-post-creator-submit-content")
async def blog_post_creator_print_signals(signals: ReadSignals):
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
    res_insert = db.insert_row_to_db(data=new_blog_post_data)
    print(res_insert)
    print("*" * 100)


# end of BLOG ROUTES ------------------------------------------------------------------------------


@app.get("/resources")
def resources(request: Request):
    context = {"message": "hello world, this is resources", "resources": {}}
    return templates.TemplateResponse(
        request=request, name="resources.html", context=context
    )


@app.get("/list-db-blog-entries")
def list_db_blog_entries(request: Request):
    res = db.execute_query(db.SELECT_QUERY, ())
    return {"res": res}


# --- EXECUTING  ---

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )
