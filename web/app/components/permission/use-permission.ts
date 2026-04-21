'use client'

import type { AccountRole } from '@/types/permission'
import { useAppContext } from '@/context/app-context'
import { isDeveloperOnlyRole, isDevRole, isPrivilegedRole, ROLE_NAV_CONFIG, ROLE_PRIORITY } from '@/types/permission'

/**
 * usePermission Hook
 * 提供权限判断功能
 */
export const usePermission = () => {
  // 从 AppContext 获取当前用户的 account role
  // 这个值是通过 API 从 enterprise API 获取的
  const { accountRole } = useAppContext()

  /**
   * 判断当前用户是否有权限访问指定角色
   */
  const canAccess = (roles: AccountRole[]): boolean => {
    return roles.includes(accountRole)
  }

  /**
   * 判断当前用户是否有权限访问指定菜单路径
   */
  const canAccessNav = (href: string): boolean => {
    const allowedPaths = ROLE_NAV_CONFIG[accountRole]
    return allowedPaths.some(path => href.startsWith(path))
  }

  /**
   * 判断当前用户是否为管理员及以上
   */
  const isPrivileged = (): boolean => {
    return isPrivilegedRole(accountRole)
  }

  /**
   * 判断当前用户是否为开发人员及以上
   */
  const isDeveloper = (): boolean => {
    return isDevRole(accountRole)
  }

  /**
   * 判断当前用户是否为开发人员（admin 或 dev，不包括 manager）
   */
  const isDeveloperOnly = (): boolean => {
    return isDeveloperOnlyRole(accountRole)
  }

  /**
   * 判断当前角色是否高于指定角色
   */
  const isRoleHigherThan = (role: AccountRole): boolean => {
    return ROLE_PRIORITY[accountRole] > ROLE_PRIORITY[role]
  }

  /**
   * 判断当前角色是否大于等于指定角色
   */
  const isRoleHigherOrEqual = (role: AccountRole): boolean => {
    return ROLE_PRIORITY[accountRole] >= ROLE_PRIORITY[role]
  }

  return {
    accountRole,
    canAccess,
    canAccessNav,
    isPrivileged,
    isDeveloper,
    isDeveloperOnly,
    isRoleHigherThan,
    isRoleHigherOrEqual,
  }
}
