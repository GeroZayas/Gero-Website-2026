from os import DirEntry, name

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
import os

app = FastAPI(title="Gero Zayas")
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/")
@app.get("/home")
def home(request: Request):
    context = {"message": "hello world, this is working"}
    return templates.TemplateResponse(
        request=request, name="home.html", context=context
    )


@app.get("/")
@app.get("/about")
def about(request: Request):
    context = {"message": "hello world, this is about page"}
    return templates.TemplateResponse(
        request=request, name="about.html", context=context
    )


@app.get("/")
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


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
    )
