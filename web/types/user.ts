/**
 * User Types
 * 用户管理相关的类型定义
 */

import type { AccountRole } from '@/types/permission'

/**
 * 用户信息
 */
export type UserInfo = {
  account_id: string
  name: string | null
  email: string | null
  avatar: string | null
  account_role: AccountRole
  status: string
  last_login_ip: string | null
  created_at: string | null
  updated_at: string | null
  departments: string[]
}

/**
 * 用户列表响应
 */
export type UserListResponse = {
  data: UserInfo[]
  total: number
}

/**
 * 部门信息
 */
export type DepartmentInfo = {
  id: string
  name: string
}

/**
 * 用户部门列表响应
 */
export type UserDepartmentsResponse = {
  data: DepartmentInfo[]
  total: number
}

/**
 * 用户角色选项（用于下拉选择）
 */
export const USER_ROLE_OPTIONS: { value: AccountRole, label: string }[] = [
  { value: 'admin', label: '超级管理员' },
  { value: 'manager', label: '普通管理员' },
  { value: 'dev', label: '开发人员' },
  { value: 'user', label: '普通用户' },
]

/**
 * 获取用户角色显示名称
 */
export const getRoleLabel = (role: AccountRole): string => {
  const option = USER_ROLE_OPTIONS.find(opt => opt.value === role)
  return option?.label ?? role
}

/**
 * 获取当前角色可选择的角色选项
 * admin 可见: dev, manager, user
 * manager 可见: manager, user
 */
export const getVisibleRoleOptions = (currentRole: AccountRole): { value: AccountRole, label: string }[] => {
  if (currentRole === 'admin') {
    return [
      { value: 'dev', label: '开发人员' },
      { value: 'manager', label: '普通管理员' },
      { value: 'user', label: '普通用户' },
    ]
  }
  if (currentRole === 'manager') {
    return [
      { value: 'manager', label: '普通管理员' },
      { value: 'user', label: '普通用户' },
    ]
  }
  return []
}

/**
 * 批量导入用户记录
 */
export type BatchImportUserRecord = {
  name: string
  email: string
  password?: string
  role?: AccountRole
  department?: string
}

/**
 * 批量导入错误信息
 */
export type BatchImportError = {
  row: number
  email: string
  message: string
}

/**
 * 批量导入创建的用户信息
 */
export type BatchImportCreatedUser = {
  email: string
  name: string
  is_password_generated: boolean
  generated_password?: string
}

/**
 * 批量导入响应
 */
export type BatchImportResponse = {
  success_count: number
  fail_count: number
  total: number
  errors: BatchImportError[]
  created_users: BatchImportCreatedUser[]
}
