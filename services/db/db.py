import logging
import sqlite3
from contextlib import closing
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

INSERT_ROW_QUERY = """
INSERT INTO {table_name} (title, content) VALUES (?, ?)
"""

UPDATE_ROW_QUERY = """
UPDATE {table_name}
SET title = ?, content = ?
WHERE id = ?
"""

DELETE_ROW_QUERY = """
DELETE FROM {table_name}
WHERE id = ?
"""


# =======================================================================================
# UTILS procs
# =======================================================================================
def print_rows_from_db_result(rows_list: list[sqlite3.Row]):
    for i, row in enumerate(rows_list, 1):
        print(f" ROW {i} ".center(40, "="))
        print("ID".ljust(15, "."), row["id"])
        print("TITLE".ljust(15, "."), row["title"])
        print("CONTENT".ljust(15, "."), row["content"])
        print("CREATED AT".ljust(15, "."), row["created_at"])
        print("UPDATED AT".ljust(15, "."), row["updated_at"], end="\n\n")


# =======================================================================================
# Main PROCs
# =======================================================================================
def execute_query(query: str, values: tuple):
    """Returns ROWS of executed query if any"""
    with closing(sqlite3.connect(db_settings["path"])) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        log.info("Cursor creado")
        if values:
            # with conn: -> makes it like conn.commit() if success or ROLLBACK if fail
            with conn:
                cursor.execute(
                    query.format(table_name=db_settings["table_name"]), values
                )
                log.debug("Cursor Ejecutado %s", cursor.rowcount)
                return cursor.rowcount
        else:
            # QUERY JUST FOR READING DATA
            with conn:
                cursor.execute(query.format(table_name=db_settings["table_name"]))
                rows_list = cursor.fetchall()
                log.debug("Cursor Ejecutado %s", cursor.rowcount)
                print_rows_from_db_result(rows_list)
                return rows_list


def insert_row_to_db(data: dict):
    title, content = data["title"], data["content"]
    res = execute_query(
        INSERT_ROW_QUERY.format(table_name=db_settings["table_name"]), (title, content)
    )
    return {"return insert": res}


def update_row_in_db(row_id: int, data: dict):
    title, content = data["title"], data["content"]
    res = execute_query(
        query=UPDATE_ROW_QUERY.format(table_name=db_settings["table_name"]),
        values=(title, content, row_id),
    )
    return {"return update": res}


def delete_row_in_db(row_id: int):
    res = execute_query(query=DELETE_ROW_QUERY, values=(row_id,))
    return {"return delete": res}


# =======================================================================================
# MAIN entry point
# =======================================================================================
def main():
    execute_query(SELECT_QUERY, ())
    print("=" * 80)
    row_id_input = int(input("INSERT ROW ID: "))
    # new_title_input = input("INSERT TITLE: ")
    # new_content_input = input("INSERT CONTENT: ")
    # data = {
    #     "title": new_title_input,
    #     "content": new_content_input,
    # }
    # res_insert = insert_row_to_db(data)
    print("=" * 80)
    # res_update = update_row_in_db(row_id=row_id_input, data=data)
    res_delete = delete_row_in_db(row_id=row_id_input)
    print(res_delete)
    return 0


if __name__ == "__main__":
    main()
