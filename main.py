import os
import sqlite3

import uvicorn
from datastar_py import ServerSentEventGenerator as SSE
from datastar_py.fastapi import datastar_response, read_signals
from fastapi import Body, FastAPI, Request
from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from icecream import ic
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
            ]
        )
    )
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


blog_posts_list = {
    "one": {"title": "The TITLE of one", "content": "The CONTENTS of one"},
    "two": {"title": "The TITLE of two", "content": "The CONTENTS of two"},
    "three": {"title": "The TITLE of three", "content": "The CONTENTS of three"},
}


@app.get("/blog")
def blog(request: Request):
    dict_db_blog_entries = db.execute_query(db.SELECT_QUERY, ())
    context = {"message": "This is blog page", "blog_posts": dict_db_blog_entries}

    return templates.TemplateResponse(
        request=request, name="blog.html", context=context
    )


@app.get("/blog/{blog_id}")
def blog_post(blog_id: str, request: Request):
    selected_blog = blog_posts_list[blog_id]
    print("selected_blog:", selected_blog)
    context = {"message": "hello world, this is blog page", "blog_post": selected_blog}
    return templates.TemplateResponse(
        request=request, name="blog_post.html", context=context
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
        port=int(os.getenv("PORT", 8000)),
        reload=True,
    )
