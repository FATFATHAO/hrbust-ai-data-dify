/**
 * Permission Types
 * 用户身份和权限相关的类型定义
 */

/**
 * 用户身份枚举
 * - admin: 超级管理员
 * - manager: 普通管理员
 * - dev: 开发人员
 * - user: 普通用户
 */
export type AccountRole = 'admin' | 'manager' | 'dev' | 'user'

/**
 * 菜单项配置
 */
export type NavItem = {
  label: string
  icon: string
  href: string
  activeIcon?: string
}

/**
 * 角色菜单权限配置
 * 定义每个角色可以访问的菜单路径
 */
export const ROLE_NAV_CONFIG: Record<AccountRole, string[]> = {
  admin: ['/dashboard', '/apps', '/datasets', '/tools', '/plugins', '/departments'],
  manager: ['/dashboard', '/apps', '/datasets', '/tools'],
  dev: ['/dashboard', '/apps', '/datasets', '/tools', '/plugins'],
  user: ['/dashboard', '/apps', '/datasets'],
}

/**
 * 权限等级
 * 用于比较角色权限高低
 */
export const ROLE_PRIORITY: Record<AccountRole, number> = {
  admin: 4,
  manager: 3,
  dev: 2,
  user: 1,
}

/**
 * 判断角色是否有特权（管理员及以上）
 */
export const isPrivilegedRole = (role: AccountRole): boolean => {
  return role === 'admin' || role === 'manager'
}

/**
 * 判断角色是否为开发人员及以上
 */
export const isDevRole = (role: AccountRole): boolean => {
  return role === 'admin' || role === 'manager' || role === 'dev'
}

/**
 * 判断角色是否为开发人员及以上（admin 或 dev，不包括 manager）
 */
export const isDeveloperOnlyRole = (role: AccountRole): boolean => {
  return role === 'admin' || role === 'dev'
}

/**
 * 判断当前角色是否有权限访问指定菜单
 */
export const canAccessNav = (role: AccountRole, href: string): boolean => {
  const allowedPaths = ROLE_NAV_CONFIG[role]
  return allowedPaths.some(path => href.startsWith(path))
}
