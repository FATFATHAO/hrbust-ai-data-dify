"""
Department Management API
部门管理 API 路由
"""
import uuid

from flask import request
from flask_restx import Resource
from pydantic import BaseModel, Field
from sqlalchemy import select

from controllers.console import console_ns
from controllers.console.wraps import setup_required
from enterprise_api.models.department import AccountDepartmentJoin, Department
from extensions.ext_database import db
from libs.login import current_account_with_tenant, login_required


class DepartmentCreate(BaseModel):
    """创建部门请求"""
    name: str = Field(..., min_length=1, max_length=255, description="部门名称")
    description: str | None = Field(None, description="部门描述")
    parent_id: str | None = Field(None, description="父部门ID")


class DepartmentUpdate(BaseModel):
    """更新部门请求"""
    name: str | None = Field(None, min_length=1, max_length=255, description="部门名称")
    description: str | None = Field(None, description="部门描述")
    parent_id: str | None = Field(None, description="父部门ID")


class AddMemberRequest(BaseModel):
    """添加成员请求"""
    account_id: str = Field(..., description="用户ID")


class DepartmentResponse(BaseModel):
    """部门响应"""
    id: str
    tenant_id: str
    name: str
    description: str | None
    parent_id: str | None
    created_by: str
    created_at: str | None
    updated_at: str | None
    member_count: int = 0


class DepartmentMemberResponse(BaseModel):
    """部门成员响应"""
    id: str
    account_id: str
    name: str | None
    email: str | None
    avatar: str | None
    role: str | None
    joined_at: str | None


console_ns.model("DepartmentCreate", DepartmentCreate.model_fields)
console_ns.model("DepartmentUpdate", DepartmentUpdate.model_fields)
console_ns.model("AddMemberRequest", AddMemberRequest.model_fields)


def build_department_tree(departments: list[Department], parent_id: str | None = None) -> list[dict]:
    """构建部门树形结构"""
    tree = []
    for dept in departments:
        if dept.parent_id == parent_id:
            member_count = len(dept.members) if dept.members else 0
            children = build_department_tree(departments, dept.id)
            node = {
                "id": dept.id,
                "tenant_id": dept.tenant_id,
                "name": dept.name,
                "description": dept.description,
                "parent_id": dept.parent_id,
                "created_by": dept.created_by,
                "created_at": dept.created_at.isoformat() if dept.created_at else None,
                "updated_at": dept.updated_at.isoformat() if dept.updated_at else None,
                "member_count": member_count,
                "children": children,
            }
            tree.append(node)
    return tree


@console_ns.route("/departments")
class DepartmentListApi(Resource):
    @setup_required
    @login_required
    def get(self):
        """获取部门列表"""
        include_tree = request.args.get("include_tree", "false").lower() == "true"

        current_user, _ = current_account_with_tenant()
        tenant_id = current_user.current_tenant_id

        departments = db.session.scalars(
            select(Department).filter(Department.tenant_id == tenant_id)
        ).all()

        if include_tree:
            data = build_department_tree(departments)
        else:
            data = []
            for dept in departments:
                member_count = len(dept.members) if dept.members else 0
                data.append({
                    "id": dept.id,
                    "tenant_id": dept.tenant_id,
                    "name": dept.name,
                    "description": dept.description,
                    "parent_id": dept.parent_id,
                    "created_by": dept.created_by,
                    "created_at": dept.created_at.isoformat() if dept.created_at else None,
                    "updated_at": dept.updated_at.isoformat() if dept.updated_at else None,
                    "member_count": member_count,
                })

        return {"data": data, "total": len(data)}

    @setup_required
    @login_required
    def post(self):
        """创建部门"""
        current_user, _ = current_account_with_tenant()
        tenant_id = current_user.current_tenant_id

        data = request.get_json()
        department_data = DepartmentCreate.model_validate(data)

        # 验证父部门（如果指定）
        if department_data.parent_id:
            parent = db.session.scalars(
                select(Department).filter(
                    Department.id == department_data.parent_id,
                    Department.tenant_id == tenant_id
                )
            ).first()
            if not parent:
                return {"error": "父部门不存在"}, 400

        # 创建部门
        department = Department(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            name=department_data.name,
            description=department_data.description,
            parent_id=department_data.parent_id,
            created_by=current_user.id,
        )

        db.session.add(department)
        db.session.commit()
        db.session.refresh(department)

        return {
            "id": department.id,
            "tenant_id": department.tenant_id,
            "name": department.name,
            "description": department.description,
            "parent_id": department.parent_id,
            "created_by": department.created_by,
            "created_at": department.created_at.isoformat() if department.created_at else None,
            "updated_at": department.updated_at.isoformat() if department.updated_at else None,
            "member_count": 0,
        }, 201


@console_ns.route("/departments/<department_id>")
class DepartmentApi(Resource):
    @setup_required
    @login_required
    def get(self, department_id: str):
        """获取部门详情"""
        current_user, _ = current_account_with_tenant()
        tenant_id = current_user.current_tenant_id

        department = db.session.scalars(
            select(Department).filter(
                Department.id == department_id,
                Department.tenant_id == tenant_id
            )
        ).first()

        if not department:
            return {"error": "部门不存在"}, 404

        member_count = len(department.members) if department.members else 0

        return {
            "id": department.id,
            "tenant_id": department.tenant_id,
            "name": department.name,
            "description": department.description,
            "parent_id": department.parent_id,
            "created_by": department.created_by,
            "created_at": department.created_at.isoformat() if department.created_at else None,
            "updated_at": department.updated_at.isoformat() if department.updated_at else None,
            "member_count": member_count,
        }

    @setup_required
    @login_required
    def put(self, department_id: str):
        """更新部门"""
        current_user, _ = current_account_with_tenant()
        tenant_id = current_user.current_tenant_id

        department = db.session.scalars(
            select(Department).filter(
                Department.id == department_id,
                Department.tenant_id == tenant_id
            )
        ).first()

        if not department:
            return {"error": "部门不存在"}, 404

        data = request.get_json()
        update_data = DepartmentUpdate.model_validate(data)

        # 更新字段
        if update_data.name is not None:
            department.name = update_data.name
        if update_data.description is not None:
            department.description = update_data.description
        if update_data.parent_id is not None:
            # 防止循环引用
            if update_data.parent_id == department_id:
                return {"error": "不能将部门设置为自己的父部门"}, 400
            # 验证新父部门
            parent = db.session.scalars(
                select(Department).filter(
                    Department.id == update_data.parent_id,
                    Department.tenant_id == tenant_id
                )
            ).first()
            if not parent:
                return {"error": "父部门不存在"}, 400
            department.parent_id = update_data.parent_id

        db.session.commit()
        db.session.refresh(department)

        member_count = len(department.members) if department.members else 0

        return {
            "id": department.id,
            "tenant_id": department.tenant_id,
            "name": department.name,
            "description": department.description,
            "parent_id": department.parent_id,
            "created_by": department.created_by,
            "created_at": department.created_at.isoformat() if department.created_at else None,
            "updated_at": department.updated_at.isoformat() if department.updated_at else None,
            "member_count": member_count,
        }

    @setup_required
    @login_required
    def delete(self, department_id: str):
        """删除部门"""
        current_user, _ = current_account_with_tenant()
        tenant_id = current_user.current_tenant_id

        department = db.session.scalars(
            select(Department).filter(
                Department.id == department_id,
                Department.tenant_id == tenant_id
            )
        ).first()

        if not department:
            return {"error": "部门不存在"}, 404

        # 检查是否有子部门
        children_count = db.session.scalars(
            select(Department).filter(
                Department.parent_id == department_id,
                Department.tenant_id == tenant_id
            )
        ).count()
        if children_count > 0:
            return {"error": "无法删除有子部门的部门"}, 400

        # 检查是否有成员
        member_count = db.session.scalars(
            select(AccountDepartmentJoin).filter(
                AccountDepartmentJoin.department_id == department_id
            )
        ).count()
        if member_count > 0:
            return {"error": "无法删除有成员的部门"}, 400

        db.session.delete(department)
        db.session.commit()

        return "", 204


@console_ns.route("/departments/<department_id>/members")
class DepartmentMemberListApi(Resource):
    @setup_required
    @login_required
    def get(self, department_id: str):
        """获取部门成员列表"""
        current_user, _ = current_account_with_tenant()
        tenant_id = current_user.current_tenant_id

        # 验证部门存在
        department = db.session.scalars(
            select(Department).filter(
                Department.id == department_id,
                Department.tenant_id == tenant_id
            )
        ).first()

        if not department:
            return {"error": "部门不存在"}, 404

        # 查询成员
        from models.account import Account
        members = db.session.scalars(
            select(AccountDepartmentJoin).filter(
                AccountDepartmentJoin.department_id == department_id
            )
        ).all()

        result = []
        for m in members:
            # 查找用户信息
            account = db.session.scalars(
                select(Account).filter(Account.id == m.account_id)
            ).first()
            result.append({
                "id": m.id,
                "account_id": m.account_id,
                "name": account.name if account else None,
                "email": account.email if account else None,
                "avatar": account.avatar if account else None,
                "role": m.role,
                "joined_at": m.created_at.isoformat() if m.created_at else None,
            })

        return {"data": result, "total": len(result)}

    @setup_required
    @login_required
    def post(self, department_id: str):
        """添加部门成员"""
        current_user, _ = current_account_with_tenant()
        tenant_id = current_user.current_tenant_id

        # 验证部门存在
        department = db.session.scalars(
            select(Department).filter(
                Department.id == department_id,
                Department.tenant_id == tenant_id
            )
        ).first()

        if not department:
            return {"error": "部门不存在"}, 404

        data = request.get_json()
        member_data = AddMemberRequest.model_validate(data)

        # 检查是否已是成员
        existing = db.session.scalars(
            select(AccountDepartmentJoin).filter(
                AccountDepartmentJoin.department_id == department_id,
                AccountDepartmentJoin.account_id == member_data.account_id
            )
        ).first()

        if existing:
            return {"error": "用户已是该部门成员"}, 400

        # 创建关联
        join_record = AccountDepartmentJoin(
            id=str(uuid.uuid4()),
            account_id=member_data.account_id,
            department_id=department_id,
            tenant_id=tenant_id,
        )

        db.session.add(join_record)
        db.session.commit()

        return {"message": "成员添加成功"}, 201


@console_ns.route("/departments/<department_id>/members/<account_id>")
class DepartmentMemberApi(Resource):
    @setup_required
    @login_required
    def delete(self, department_id: str, account_id: str):
        """移除部门成员"""
        current_user, _ = current_account_with_tenant()
        tenant_id = current_user.current_tenant_id

        # 验证部门存在
        department = db.session.scalars(
            select(Department).filter(
                Department.id == department_id,
                Department.tenant_id == tenant_id
            )
        ).first()

        if not department:
            return {"error": "部门不存在"}, 404

        # 查找成员
        member = db.session.scalars(
            select(AccountDepartmentJoin).filter(
                AccountDepartmentJoin.department_id == department_id,
                AccountDepartmentJoin.account_id == account_id
            )
        ).first()

        if not member:
            return {"error": "成员不在该部门中"}, 404

        db.session.delete(member)
        db.session.commit()

        return "", 204
