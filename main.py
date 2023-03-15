import hashlib
import os
import shutil
import sqlite3
from pathlib import Path

from settings import paths, file_pattern, do_original2hash


def setup_paths():
    if not os.path.exists(paths['original_dir']):
        raise FileNotFoundError(f"{paths['original_dir']} does not exist.")
    paths['base'] = os.path.dirname(os.path.realpath(__file__))
    for k in ['base', 'original_dir', 'hash_dir']:
        paths[k] = Path(paths[k])
    paths['db'] = Path(paths['base'] / 'db.sqlite')
    paths['original_excludes'] = [paths['original_dir'] / p for p in paths['original_excludes']]
    Path(paths['hash_dir']).mkdir(parents=True, exist_ok=True)


def setup_database():
    global conn, c, tbl
    tbl = 'file'
    conn = sqlite3.connect(paths['db'])
    conn.row_factory = sqlite3.Row
    c = conn.cursor()


def create_table():
    sql = f"""
        create table if not exists {tbl}
    (
        id             integer                            not null
            constraint id_pk
                primary key autoincrement,
        run            integer                            not null,
        date           datetime default current_timestamp not null,
        file_path      TEXT                               not null,
        file_path_hash TEXT                               not null,
        constraint     file_path_unique
            unique     (run, file_path),
        constraint     file_path_hash_unique
            unique     (run, file_path_hash)
    );
        """
    c.execute(sql)



def original2hash():
    create_table()
    sql = f"SELECT MAX(run) FROM {tbl};"
    c.execute(sql)
    max_run = c.fetchone()[0] or 0
    sql = f"""
        INSERT INTO {tbl}(run, file_path, file_path_hash)
        VALUES(?, ?, ?)
        """
    for file_path in paths['original_dir'].rglob(file_pattern):
        for original_exclude in paths['original_excludes']:
            if original_exclude in file_path.parents:
                break
        else:
            file_path_hash = hashlib.md5(str(file_path).encode('utf-8')).hexdigest()
            c.execute(sql, (max_run + 1, str(file_path), file_path_hash))
            conn.commit()
            new_file_path = paths['hash_dir'] / f'{file_path_hash}.php'
            shutil.copyfile(file_path, new_file_path)
            print(f"{file_path} -> {new_file_path}")


def hash2original():
    sql = f"SELECT * FROM {tbl} WHERE run = (SELECT MAX(run) FROM {tbl})"
    c.execute(sql)
    files = c.fetchall()
    for file in files:
        old_file_path = paths['hash_dir'] / f'{file["file_path_hash"]}.php'
        shutil.copyfile(old_file_path, file['file_path'])
        print(f"{old_file_path} -> {file['file_path']}")


def main():
    setup_paths()
    setup_database()
    if do_original2hash:
        original2hash()
    else:
        hash2original()


if __name__ == '__main__':
    main()
