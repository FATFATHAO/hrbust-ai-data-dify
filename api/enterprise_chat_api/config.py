"""
Enterprise Chat API 配置
"""

import os
from functools import lru_cache


@lru_cache(maxsize=1)
def get_dsl_file_base_path() -> str:
    """获取 DSL 文件基础路径"""
    return os.environ.get(
        "QA_FLOW_DSL_BASE_PATH",
        "/home/soyor1n/HrbustGateway"
    )


def get_dsl_file_path(file_name: str = "智能问答助手.yml") -> str:
    """获取完整的 DSL 文件路径"""
    return os.path.join(get_dsl_file_base_path(), file_name)