"""将项目旧 SQLite 数据迁移到当前 database.ini 配置的 MySQL。"""

import argparse
import os
import sqlite3

from app.db import get_connection, get_engine


TABLES = [
    'users',
    'cases',
    'case_questions',
    'tasks',
    'task_cases',
    'responses',
    'response_details',
    'feedback_tasks',
    'feedback_questions',
    'feedback_question_options',
    'feedback_task_mappings',
    'feedback_responses',
]


def migrate(source_path: str) -> None:
    if get_engine() != 'mysql':
        raise RuntimeError('当前 database.ini 未配置 engine = mysql')
    if not os.path.exists(source_path):
        raise FileNotFoundError(f'找不到 SQLite 数据库: {source_path}')

    source = sqlite3.connect(source_path)
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            counts = {}
            for table in TABLES:
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                counts[table] = cursor.fetchone()[0]
            if any(counts.values()):
                raise RuntimeError('MySQL 目标表已有数据，已停止迁移，请先备份并清理目标库')

            for table in TABLES:
                source_cursor = source.execute(f'SELECT * FROM {table}')
                source_columns = [item[0] for item in source_cursor.description]
                rows = source_cursor.fetchall()
                if not rows:
                    continue

                cursor.execute(f'SHOW COLUMNS FROM {table}')
                target_columns = {row[0] for row in cursor.fetchall()}
                columns = [column for column in source_columns if column in target_columns]
                indexes = [source_columns.index(column) for column in columns]
                placeholders = ', '.join(['?'] * len(columns))
                column_sql = ', '.join(columns)
                insert_sql = f'INSERT INTO {table} ({column_sql}) VALUES ({placeholders})'
                cursor.executemany(insert_sql, [tuple(row[index] for index in indexes) for row in rows])
                print(f'{table}: {len(rows)}')

            conn.commit()
            print('SQLite -> MySQL migration completed.')
    finally:
        source.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Migrate survey.db data to MySQL')
    parser.add_argument('--source', default='survey.db', help='SQLite database path')
    args = parser.parse_args()
    migrate(args.source)
