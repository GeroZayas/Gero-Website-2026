from dataclasses import dataclass


# --- DATA MODELS ---
@dataclass
class BlogPostElement:
    title: str
    id: int
    slug: str
    body: str
    tags: list[str]


@dataclass
class ProjectElement:
    title: str
    link: str
    id: int
    slug: str
    body: str
    tags: list[str]
