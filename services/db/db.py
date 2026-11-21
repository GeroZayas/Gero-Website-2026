import logging
import sqlite3
from contextlib import closing
from functools import lru_cache
from pathlib import Path
from types import MappingProxyType

from rich import print

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

READ_ROW = "SELECT * FROM {table_name} WHERE id = ?"

INSERT_ROW_QUERY = """
INSERT INTO {table_name} (title, content, tags, lang) VALUES (?, ?, ?, ?)
"""

UPDATE_ROW_QUERY = """
UPDATE {table_name}
SET title = ?, content = ?, tags = ?, lang = ?, 
WHERE id = ?
"""

DELETE_ROW_QUERY = """
DELETE FROM {table_name}
WHERE id = ?
"""


# =======================================================================================
# UTILS procs
# =======================================================================================
@lru_cache(maxsize=128)
def print_rows_from_db_result(rows_list: list[sqlite3.Row]):
    for i, row in enumerate(rows_list, 1):
        print(f" ROW {i} ".center(40, "="))
        print("ID".ljust(15, "."), row["id"])
        print("TITLE".ljust(15, "."), row["title"])
        print("CONTENT".ljust(15, "."), row["content"])
        print("TAGS".ljust(15, "."), row["tags"])
        print("LANG".ljust(15, "."), row["lang"])
        print("CREATED AT".ljust(15, "."), row["created_at"])
        print("UPDATED AT".ljust(15, "."), row["updated_at"], end="\n\n")


# =======================================================================================
# Main PROCs
# =======================================================================================
@lru_cache(maxsize=128)
def execute_query(query: str, values: tuple, read_one=False):
    """Returns ROWS of executed query if any"""
    with closing(sqlite3.connect(db_settings["path"])) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        log.info("Cursor creado")
        if values and read_one == False:
            # with conn: -> makes it like conn.commit() if success or ROLLBACK if fail
            with conn:
                cursor.execute(
                    query.format(table_name=db_settings["table_name"]), values
                )
                log.debug("Cursor Ejecutado %s", cursor.rowcount)
                return cursor.rowcount
        elif read_one == True:
            with conn:
                cursor.execute(
                    query.format(table_name=db_settings["table_name"]), values
                )
                rows_list = cursor.fetchall()
                # print(rows_list)
                # print_rows_from_db_result(rows_list)
                log.debug("Cursor Ejecutado %s", cursor.rowcount)
                return rows_list

        else:
            # QUERY JUST FOR READING ALL DATA
            with conn:
                cursor.execute(query.format(table_name=db_settings["table_name"]))
                rows_list = cursor.fetchall()
                log.debug("Cursor Ejecutado %s", cursor.rowcount)
                # print_rows_from_db_result(rows_list)
                return rows_list


def insert_row_to_db(data: dict):
    title, content, tags, lang = (
        data["title"],
        data["content"],
        data["tags"],
        data["lang"],
    )
    res = execute_query(
        INSERT_ROW_QUERY.format(table_name=db_settings["table_name"]),
        (title, content, tags, lang),
    )
    execute_query.cache_clear()
    return {"return insert": res}


def update_row_in_db(row_id: int, data: dict):
    title, content = data["title"], data["content"]
    res = execute_query(
        query=UPDATE_ROW_QUERY.format(table_name=db_settings["table_name"]),
        values=(title, content, row_id),
    )
    execute_query.cache_clear()
    return {"return update": res}


def delete_row_in_db(row_id: int):
    res = execute_query(query=DELETE_ROW_QUERY, values=(row_id,))
    execute_query.cache_clear()
    return {"return delete": res}


# =======================================================================================
# MAIN entry point
# =======================================================================================
def main():
    execute_query(SELECT_QUERY, ())
    print("=" * 80)
    user_choice = input("i - insert, u - update, d - delete, q - exit: ")
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
        res_insert = insert_row_to_db(data)
        print(res_insert)
    elif user_choice == "u":
        row_id_input = int(input("INSERT ROW ID: "))
        new_title_input = input("INSERT TITLE: ")
        new_content_input = input("INSERT CONTENT: ")
        data = {
            "title": new_title_input,
            "content": new_content_input,
        }
        res_update = update_row_in_db(row_id=row_id_input, data=data)
        print(res_update)

    elif user_choice == "d":
        row_id_input = int(input("INSERT ROW ID: "))
        res_delete = delete_row_in_db(row_id=row_id_input)
        print(res_delete)

    elif user_choice == "q":
        print("BYE BYE")
        exit()

    else:
        print("COMMAND NOT AVAILABLE")

    print("=" * 80)
    return 0


if __name__ == "__main__":
    main()
