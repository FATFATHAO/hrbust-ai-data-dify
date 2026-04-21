'use client'

import type { ReactNode } from 'react'
import type { AccountRole } from '@/types/permission'
import { usePermission } from './use-permission'

type PermissionGuardProps = {
  /**
   * 允许访问的角色列表
   * 如果为空数组，则所有人都不能访问
   * 如果为 ['admin', 'manager']，则只有 admin 和 manager 可以访问
   */
  roles: AccountRole[]
  /**
   * 子元素
   */
  children: ReactNode
  /**
   * 当没有权限时显示的替代内容
   */
  fallback?: ReactNode
  /**
   * 是否使用更高的权限判断（大于等于）
   * 如果为 true，则当前用户角色>=指定角色时允许访问
   * 如果为 false（默认），则当前用户角色必须完全匹配指定角色
   */
  useHigherOrEqual?: boolean
}

/**
 * PermissionGuard 组件
 * 根据用户角色决定是否渲染子元素
 */
export const PermissionGuard: React.FC<PermissionGuardProps> = ({
  roles,
  children,
  fallback = null,
  useHigherOrEqual = false,
}) => {
  const { accountRole, isRoleHigherOrEqual } = usePermission()

  const hasPermission = useHigherOrEqual
    ? roles.some(role => isRoleHigherOrEqual(role))
    : roles.includes(accountRole)

  if (!hasPermission)
    return fallback

  return <>{children}</>
}

/**
 * RequireAdmin 组件
 * 仅允许管理员及以上角色访问
 */
export const RequireAdmin: React.FC<{ children: ReactNode, fallback?: ReactNode }> = ({
  children,
  fallback = null,
}) => (
  <PermissionGuard roles={['admin', 'manager']} useHigherOrEqual fallback={fallback}>
    {children}
  </PermissionGuard>
)

/**
 * RequireDev 组件
 * 仅允许开发人员及以上角色访问
 */
export const RequireDev: React.FC<{ children: ReactNode, fallback?: ReactNode }> = ({
  children,
  fallback = null,
}) => (
  <PermissionGuard roles={['admin', 'manager', 'dev']} useHigherOrEqual fallback={fallback}>
    {children}
  </PermissionGuard>
)
