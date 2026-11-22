import logging
import sqlite3
from contextlib import closing, contextmanager
from functools import lru_cache
from pathlib import Path
from types import MappingProxyType

from rich import print
from rich.console import Console
from rich.panel import Panel

fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
logging.basicConfig(level=logging.DEBUG, format=fmt)
log = logging.getLogger(__name__)


db_settings = MappingProxyType(
    {
        "path": Path(__file__).parent / "gero_zayas_website_db.db",
        "table_name": "gero_blog",
    }
)
# db_settings['table_name']

log.info("scratch buffer iniciado")

# =======================================================================================
# QUERIES
# =======================================================================================
SELECT_QUERY = "SELECT * FROM {table_name}"

READ_ROW = "SELECT * FROM {table_name} WHERE id = :id"

# BLOG QUERRIES /////////////////////////////////////////////////////////////////////////
INSERT_ROW_BLOG_TABLE_QUERY = """
INSERT INTO gero_blog (title, content, tags, lang) VALUES (:title, :content, :tags, :lang)
"""

UPDATE_ROW_BLOG_TABLE_QUERY = """
UPDATE gero_blog
SET title = :title, content = :content, tags = :tags, lang = :lang 
WHERE id = :id
"""

DELETE_ROW_BLOG_TABLE_QUERY = """
DELETE FROM gero_blog
WHERE id = :id
"""

# PROJECT QUERRIES //////////////////////////////////////////////////////////////////////
CREATE_TABLE_PROJECTS_QUERY = """
CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    tags TEXT,
    link TEXT,
    description TEXT
);
"""

INSERT_NEW_PROJECT_TABLE_PROJECTS_QUERY = """
INSERT INTO projects (name, tags, link, description)
VALUES (:name, :tags, :link, :description);
"""

UPDATE_ROW_TABLE_PROJECTS_QUERY = """
UPDATE projects
SET name= :name, tags = :tags, link = :link, description = :description
WHERE id = :id
"""

DELETE_ROW_TABLE_PROJECTS_QUERY = """
DELETE FROM projects
WHERE id = :id
"""


# =======================================================================================
# UTILS procs
# =======================================================================================
def print_rows_from_blog_table_db_result(rows_list: list[sqlite3.Row]):
    for i, row in enumerate(rows_list, 1):
        print(f"ROW {i} ".center(40, "="))
        print("ID".ljust(15, "."), row["id"])
        print("TITLE".ljust(15, "."), row["title"])
        # print("CONTENT".ljust(15, "."), row["content"])
        print("TAGS".ljust(15, "."), row["tags"])
        print("LANG".ljust(15, "."), row["lang"])
        print("CREATED AT".ljust(15, "."), row["created_at"])
        print("UPDATED AT".ljust(15, "."), row["updated_at"], end="\n\n")


def print_rows_from_db_result(rows_list: list[sqlite3.Row], table_name: str = ""):
    row = rows_list[0]
    keys = row.keys()
    for row in rows_list:
        for k in keys:
            if k == "content":
                continue
            print(f"-> {k} ".ljust(20, "-"), row[k])
        print("=" * 120)


@contextmanager
def handle_db_operational_errors():
    try:
        yield
    except Exception as e:
        print(Panel(f"[ERROR] {e}", style="red"))


# =======================================================================================
# Main PROCs
# =======================================================================================
# @lru_cache(maxsize=128)
def execute_query(query: str, values: dict, table: str, read_one=False):
    """Returns ROWS of executed query if any"""
    with closing(sqlite3.connect(db_settings["path"])) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        log.info("Cursor creado")
        if values and read_one == False:
            # with conn: -> makes it like conn.commit() if success or ROLLBACK if fail
            with conn, handle_db_operational_errors():
                cursor.execute(query.format(table_name=table), values)
                log.debug("Cursor Ejecutado %s", cursor.rowcount)
                return cursor.rowcount
        elif read_one == True:
            with conn, handle_db_operational_errors():
                cursor.execute(query.format(table_name=table), values)
                rows_list = cursor.fetchall()
                print(rows_list)
                print_rows_from_db_result(rows_list)
                log.debug("Cursor Ejecutado %s", cursor.rowcount)
                return rows_list

        # ELSE READ ALL
        else:
            # QUERY JUST FOR READING ALL DATA
            with conn, handle_db_operational_errors():
                cursor.execute(query.format(table_name=table))
                rows_list = cursor.fetchall()
                log.debug("Cursor Ejecutado %s", cursor.rowcount)
                print_rows_from_db_result(rows_list)
                return rows_list


def insert_row_to_blog_db(data: dict):
    res = execute_query(
        INSERT_ROW_BLOG_TABLE_QUERY,
        table="gero_blog",
        values=data,
    )

    return {"return insert": res}


def update_row_in_blog_db(data: dict):
    res = execute_query(
        query=UPDATE_ROW_BLOG_TABLE_QUERY,
        table="gero_blog",
        values=data,
    )

    return {"return update": res}


def delete_row_in_blog_db(row_id: int):
    res = execute_query(
        query=DELETE_ROW_BLOG_TABLE_QUERY, table="gero_blog", values={"id": row_id}
    )

    return {"return delete": res}


# PROJECTS TABLES
def create_projects_table():
    res = execute_query(CREATE_TABLE_PROJECTS_QUERY, values=(), table="projects")
    print(
        "EXECUTING -> execute_query(CREATE_TABLE_PROJECTS_QUERY, values=(), table='projects')"
    )
    return {"res": res}


def insert_row_to_projects_table_db(data: dict):
    #  (name, tags, link, description)
    res = execute_query(
        INSERT_NEW_PROJECT_TABLE_PROJECTS_QUERY,
        table="projects",
        values=data,
    )
    # execute_query.cache_clear()
    return {"return insert": res}


def update_row_in_projects_table_db(data: dict):
    res = execute_query(
        query=UPDATE_ROW_TABLE_PROJECTS_QUERY,
        table="projects",
        values=data,
    )
    return {"return update": res}


def delete_row_in_projects_table_db(row_id: int):
    res = execute_query(
        query=DELETE_ROW_TABLE_PROJECTS_QUERY, table="gero_blog", values={"id": row_id}
    )

    return {"return delete": res}


def show_user_options():
    print(
        Panel(
            "Choose action:\n\tct - create table,\n\tr - read all entries,\n\tr1 - read one,\n\ti - insert,\n\tu - update,\n\td - delete,\n\tq - exit: ",
            title="Choose action",
            border_style="yellow",
        )
    )


# TABLES PROCEDURES ///////////////////////////////////////////////////////////////////////////////
def table_blog():
    running = True
    while running:
        show_user_options()

        user_choice = input(">>> ")
        print("=" * 80)

        if user_choice == "i":
            new_title_input = input("INSERT TITLE: ")
            new_content_input = input("INSERT CONTENT: ")
            new_tags_input = input("INSERT TAGS (separated by commas): ")
            new_lang_input = input("INSERT LANG: ")
            data = {
                "title": new_title_input,
                "content": new_content_input,
                "tags": new_tags_input,
                "lang": new_lang_input,
            }
            res_insert = insert_row_to_blog_db(data)
            print(res_insert)
        elif user_choice == "r":
            execute_query(SELECT_QUERY, table="gero_blog", values={})
            print("=" * 80)
        elif user_choice == "r1":
            row_id_input = input("INSERT ROW ID: ")
            execute_query(
                READ_ROW, table="gero_blog", values={"id": row_id_input}, read_one=True
            )
            print("=" * 80)
        elif user_choice == "u":
            row_id_input = int(input("INSERT ROW ID: "))
            new_title_input = input("INSERT TITLE: ")
            new_content_input = input("INSERT CONTENT: ")
            new_tags_input = input("INSERT TAGS: ")
            new_lang_input = input("INSERT LANG: ")
            data = {
                "title": new_title_input,
                "content": new_content_input,
                "tags": new_tags_input,
                "lang": new_lang_input,
                "id": row_id_input,
            }
            res_update = update_row_in_blog_db(data=data)
            print(res_update)

        elif user_choice == "d":
            row_id_input = int(input("INSERT ROW ID: "))
            res_delete = delete_row_in_blog_db(row_id=row_id_input)
            print(res_delete)

        elif user_choice == "q":
            print("BYE BYE")
            running = False

        else:
            print("COMMAND NOT AVAILABLE")

        print("=" * 80)


def table_project():
    running = True
    while running:
        show_user_options()
        user_choice = input(">>> ")
        if user_choice == "ct":
            create_projects_table()
        elif user_choice == "q":
            print("BYE BYE")
            running = False

        elif user_choice == "i":
            new_name_input = input("INSERT NAME: ")
            new_tags_input = input("INSERT TAGS (separated by commas): ")
            new_link_input = input("INSERT LINK: ")
            new_description_input = input("INSERT DESCRIPTION: ")
            data = {
                "name": new_name_input,
                "tags": new_link_input,
                "link": new_tags_input,
                "description": new_description_input,
            }
            res_insert = insert_row_to_projects_table_db(data)
            print(res_insert)
        elif user_choice == "r":
            execute_query(SELECT_QUERY, table="projects", values={})
            print("=" * 80)

        elif user_choice == "r1":
            row_id_input = input("INSERT ROW ID: ")
            execute_query(
                READ_ROW, table="projects", values={"id": row_id_input}, read_one=True
            )
            print("=" * 80)

        elif user_choice == "u":
            row_id_input = input("INSERT ROW ID to UPDATE: ")
            new_name_input = input("INSERT NAME: ")
            new_tags_input = input("INSERT TAGS (separated by commas): ")
            new_link_input = input("INSERT LINK: ")
            new_description_input = input("INSERT DESCRIPTION: ")
            data = {
                "name": new_name_input,
                "tags": new_link_input,
                "link": new_tags_input,
                "description": new_description_input,
                "id": row_id_input,
            }
            res_update = update_row_in_projects_table_db(data=data)
            print(res_update)

        elif user_choice == "d":
            row_id_input = int(input("INSERT ROW ID: "))
            res_delete = delete_row_in_projects_table_db(row_id=row_id_input)
            print(res_delete)

    print("=" * 80)
    return


# =======================================================================================
# MAIN entry point
# =======================================================================================
def main():
    console = Console()

    console.print("[bold green]Welcome, Gero, to the DB Utility![/bold green]")
    print(
        Panel(
            "Choose table: 'b' -> blog , 'p' -> projects:",
            title="Choose table",
            border_style="green",
        )
    )
    table_choice = input(">>> ").lower()
    if table_choice == "p":
        table_project()
    elif table_choice == "b":
        table_blog()


if __name__ == "__main__":
    main()
    # test()
