"""
系统配置常量
"""

import os
import configparser

# 项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 数据库配置文件路径（可覆盖）
DATABASE_INI_PATH = os.environ.get('DB_CONFIG', os.path.join(BASE_DIR, 'database.ini'))

# SQL 文件路径
SCHEMA_SQL_PATH = os.path.join(BASE_DIR, 'sql', 'schema.sql')

# 密码安全
PBKDF2_ITERATIONS = 100000
SALT_LENGTH = 32

# 伦理主题分类
THEME_OPTIONS = ['患者隐私', '知情同意', '临终伦理', '科研诚信', '医患关系']

# 案例题型
QUESTION_TYPES = {
    'single_choice': '单选题',
    'multiple_choice': '多选题',
    'open': '开放式文本题'
}

# 任务状态
TASK_STATUS = {
    'draft': '草稿',
    'published': '已发布',
    'active': '进行中',
    'closed': '已关闭'
}


def load_database_config():
    """从 database.ini 加载数据库连接配置"""
    if not os.path.exists(DATABASE_INI_PATH):
        raise FileNotFoundError(
            f"数据库配置文件不存在: {DATABASE_INI_PATH}\n"
            "请复制 database.ini 模板并填写正确的 Oracle 连接信息"
        )

    config = configparser.ConfigParser()
    config.read(DATABASE_INI_PATH, encoding='utf-8')

    engine = config.defaults().get('engine', '')
    if not engine:
        for section_name in ('mysql', 'oracle'):
            if section_name in config:
                engine = config[section_name].get('engine', section_name)
                break
    engine = engine.lower() or os.environ.get('DB_ENGINE', 'sqlite').lower()
    section_name = 'mysql' if engine == 'mysql' and 'mysql' in config else 'oracle'
    if section_name not in config:
        raise ValueError(f"database.ini 中缺少 [{section_name}] 配置节")

    section = config[section_name]

    return {
        'engine': engine,
        'host': os.environ.get('DB_HOST', section.get('host', 'localhost')),
        'port': int(os.environ.get('DB_PORT', section.get('port', '3306' if engine == 'mysql' else '1521'))),
        'database': os.environ.get('DB_NAME', section.get('database', 'survey')),
        'service_name': section.get('service_name', 'XEPDB1'),
        'user': os.environ.get('DB_USER', section.get('user', 'survey_admin')),
        'password': os.environ.get('DB_PASSWORD', section.get('password', '')),
        'min_connections': int(section.get('min_connections', '2')),
        'max_connections': int(section.get('max_connections', '20')),
    }
