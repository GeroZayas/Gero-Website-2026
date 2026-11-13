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
from rich import print

# --- APP INIT ---


app = FastAPI(title="Gero Zayas")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


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
    context = {"message": "This is blog page", "blog_posts": blog_posts_list}
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


# --- EXECUTING  ---

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True,
    )
