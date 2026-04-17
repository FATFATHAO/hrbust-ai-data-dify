# Dify Enterprise API

FastAPI 实现的 Dify 企业版 API，提供部门管理和知识库分库功能。

## 快速开始

### 1. 安装依赖

```bash
cd api/enterprise_api
uv sync
```

### 2. 配置环境变量

```bash
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/dify"
export REDIS_URL="redis://localhost:6379/0"
export SECRET_KEY="your-secret-key"
```

### 3. 运行服务

```bash
# 开发模式
uv run uvicorn main:app --host 0.0.0.0 --port 5002 --reload

# 生产模式
uv run gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:5002
```

## API 文档

启动服务后访问：
- Swagger UI: http://localhost:5002/docs
- ReDoc: http://localhost:5002/redoc

## API 路由

### 部门管理 `/enterprise/api/departments`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/enterprise/api/departments` | 获取部门列表 |
| POST | `/enterprise/api/departments` | 创建部门 |
| GET | `/enterprise/api/departments/{id}` | 获取部门详情 |
| PUT | `/enterprise/api/departments/{id}` | 更新部门 |
| DELETE | `/enterprise/api/departments/{id}` | 删除部门 |
| GET | `/enterprise/api/departments/{id}/members` | 获取部门成员 |
| POST | `/enterprise/api/departments/{id}/members` | 添加成员 |
| DELETE | `/enterprise/api/departments/{id}/members/{account_id}` | 移除成员 |

## 数据库迁移

使用 Dify 的 Alembic 迁移系统：

```bash
cd api

# 创建迁移
uv run alembic revision --autogenerate -m "Add departments tables"

# 执行迁移
uv run alembic upgrade head
```

## Docker 部署

在 `docker-compose.yml` 中添加：

```yaml
services:
  enterprise_api:
    build:
      context: ./api
      dockerfile: Dockerfile.enterprise
    ports:
      - "5002:5002"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db_postgres:5432/dify
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db_postgres
      - redis
```

## 目录结构

```
enterprise_api/
├── __init__.py
├── main.py              # FastAPI 应用入口
├── config.py            # 配置
├── database.py         # 数据库连接
├── deps.py             # 依赖注入（认证）
├── models/              # SQLAlchemy 模型
│   └── department.py
├── schemas/             # Pydantic 模型
│   └── department.py
├── routers/             # API 路由
│   ├── __init__.py
│   └── department.py
└── services/           # 业务逻辑
```
