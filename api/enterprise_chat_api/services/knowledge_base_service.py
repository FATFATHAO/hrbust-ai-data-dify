"""
Knowledge Base Service
知识库权限和服务
"""


from sqlalchemy.orm import Session

from enterprise_api.models.department import AccountDepartmentJoin, DatasetDepartmentBinding
from models.dataset import Dataset, DatasetPermission


class KnowledgeBaseService:
    """知识库服务 - 获取用户可用的知识库"""

    def __init__(self, db: Session):
        self._db = db

    def get_accessible_datasets_for_user(self, user_id: str, tenant_id: str) -> list[Dataset]:
        """
        获取用户可访问的所有知识库

        复用 DatasetPermission 逻辑:
        1. 个人直接授权的知识库
        2. 通过部门绑定的知识库
        """
        dataset_ids = set()

        # 1. 个人直接授权的知识库
        personal_perms = self._db.query(DatasetPermission).filter(
            DatasetPermission.account_id == user_id,
            DatasetPermission.tenant_id == tenant_id,
            DatasetPermission.has_permission == True,
        ).all()
        dataset_ids.update(p.dataset_id for p in personal_perms)

        # 2. 通过部门绑定的知识库
        user_depts = self._db.query(AccountDepartmentJoin.department_id).filter(
            AccountDepartmentJoin.account_id == user_id,
        ).all()
        dept_ids = [d.department_id for d in user_depts]

        if dept_ids:
            dept_bindings = self._db.query(DatasetDepartmentBinding).filter(
                DatasetDepartmentBinding.department_id.in_(dept_ids),
                DatasetDepartmentBinding.tenant_id == tenant_id,
            ).all()
            dataset_ids.update(b.dataset_id for b in dept_bindings)

        if not dataset_ids:
            return []

        datasets = self._db.query(Dataset).filter(Dataset.id.in_(dataset_ids)).all()
        return datasets

    def get_department_datasets(self, department_id: str, tenant_id: str) -> list[Dataset]:
        """获取部门绑定的知识库"""
        bindings = self._db.query(DatasetDepartmentBinding).filter(
            DatasetDepartmentBinding.department_id == department_id,
            DatasetDepartmentBinding.tenant_id == tenant_id,
        ).all()

        if not bindings:
            return []

        dataset_ids = [b.dataset_id for b in bindings]
        datasets = self._db.query(Dataset).filter(Dataset.id.in_(dataset_ids)).all()
        return datasets

    def validate_dataset_ids(
        self,
        dataset_ids: list[str],
        user_id: str,
        tenant_id: str,
    ) -> list[str]:
        """
        验证知识库 ID 列表，返回有效的知识库 ID
        用户只能关联自己有权限的知识库
        """
        accessible_ids = {ds.id for ds in self.get_accessible_datasets_for_user(user_id, tenant_id)}
        return [ds_id for ds_id in dataset_ids if ds_id in accessible_ids]