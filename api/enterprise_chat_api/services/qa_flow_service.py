"""
QA Flow Service
问答流业务逻辑 - DSL 加载、App 创建、流程调用
"""

import logging
import os
from typing import Optional

import yaml
from sqlalchemy.orm import Session

from enterprise_chat_api.config import get_dsl_file_path
from enterprise_chat_api.schemas.department_qa_flow import QAFlowCreate, QAFlowUpdate
from enterprise_chat_api.models.department_qa_flow import DepartmentQAFlow
from enterprise_chat_api.models.personal_qa_flow import PersonalQAFlow
from enterprise_api.models.department import Department
from services.app_dsl_service import AppDslService
from models import Account

logger = logging.getLogger(__name__)


class QAFlowService:
    """问答流服务"""

    def __init__(self, db: Session):
        self._db = db

    def _read_dsl_file(self, file_path: str) -> str:
        """读取 DSL YAML 文件"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"DSL file not found: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def _get_default_dsl_path(self) -> str:
        """获取默认 DSL 文件路径"""
        return get_dsl_file_path()

    def create_department_qa_flow(
        self,
        department: Department,
        flow_data: QAFlowCreate,
        created_by: str,
    ) -> DepartmentQAFlow:
        """创建部门问答流"""
        # 1. 读取 DSL 文件
        dsl_content = self._read_dsl_file(self._get_default_dsl_path())

        # 2. 获取创建者账户
        account = self._db.query(Account).filter(Account.id == created_by).first()
        if not account:
            raise ValueError(f"Account not found: {created_by}")

        # 设置 tenant context（临时，不持久化）
        account.current_tenant_id = department.tenant_id

        # 3. 使用 AppDslService 导入
        app_dsl_service = AppDslService(self._db)
        import_result = app_dsl_service.import_app(
            account=account,
            import_mode="yaml-content",
            yaml_content=dsl_content,
            name=flow_data.name,
            description=flow_data.description,
        )

        if import_result.status.value not in ("completed", "completed-with-warnings"):
            raise ValueError(f"Failed to import app: {import_result.error}")

        # 4. 创建问答流记录
        flow = DepartmentQAFlow(
            id=import_result.app_id or str(department.id),
            tenant_id=department.tenant_id,
            department_id=department.id,
            created_by=created_by,
            name=flow_data.name,
            description=flow_data.description,
            dsl_file_path=self._get_default_dsl_path(),
            app_id=import_result.app_id,
            workflow_id=None,  # 从 import_result 获取
            dataset_ids=flow_data.dataset_ids or [],
            status="active",
        )

        self._db.add(flow)
        self._db.commit()
        self._db.refresh(flow)

        return flow

    def create_personal_qa_flow(
        self,
        flow_data: QAFlowCreate,
        account_id: str,
        tenant_id: str,
    ) -> PersonalQAFlow:
        """创建个人问答流"""
        # 1. 读取 DSL 文件
        dsl_content = self._read_dsl_file(self._get_default_dsl_path())

        # 2. 获取账户
        account = self._db.query(Account).filter(Account.id == account_id).first()
        if not account:
            raise ValueError(f"Account not found: {account_id}")

        # 设置 tenant context（临时，不持久化）
        account.current_tenant_id = tenant_id

        # 3. 使用 AppDslService 导入
        app_dsl_service = AppDslService(self._db)
        import_result = app_dsl_service.import_app(
            account=account,
            import_mode="yaml-content",
            yaml_content=dsl_content,
            name=flow_data.name,
            description=flow_data.description,
        )

        if import_result.status.value not in ("completed", "completed-with-warnings"):
            raise ValueError(f"Failed to import app: {import_result.error}")

        # 4. 创建问答流记录
        flow = PersonalQAFlow(
            id=import_result.app_id or str(account_id),
            tenant_id=tenant_id,
            account_id=account_id,
            name=flow_data.name,
            description=flow_data.description,
            dsl_file_path=self._get_default_dsl_path(),
            app_id=import_result.app_id,
            workflow_id=None,
            dataset_ids=flow_data.dataset_ids or [],
            status="active",
        )

        self._db.add(flow)
        self._db.commit()
        self._db.refresh(flow)

        return flow

    def update_department_qa_flow(
        self,
        flow: DepartmentQAFlow,
        flow_data: QAFlowUpdate,
    ) -> DepartmentQAFlow:
        """更新部门问答流"""
        if flow_data.name is not None:
            flow.name = flow_data.name
        if flow_data.description is not None:
            flow.description = flow_data.description
        if flow_data.dataset_ids is not None:
            flow.dataset_ids = flow_data.dataset_ids
        if flow_data.status is not None:
            flow.status = flow_data.status

        self._db.commit()
        self._db.refresh(flow)
        return flow

    def update_personal_qa_flow(
        self,
        flow: PersonalQAFlow,
        flow_data: QAFlowUpdate,
    ) -> PersonalQAFlow:
        """更新个人问答流"""
        if flow_data.name is not None:
            flow.name = flow_data.name
        if flow_data.description is not None:
            flow.description = flow_data.description
        if flow_data.dataset_ids is not None:
            flow.dataset_ids = flow_data.dataset_ids
        if flow_data.status is not None:
            flow.status = flow_data.status

        self._db.commit()
        self._db.refresh(flow)
        return flow

    def delete_department_qa_flow(self, flow: DepartmentQAFlow) -> None:
        """删除部门问答流"""
        self._db.delete(flow)
        self._db.commit()

    def delete_personal_qa_flow(self, flow: PersonalQAFlow) -> None:
        """删除个人问答流"""
        self._db.delete(flow)
        self._db.commit()
