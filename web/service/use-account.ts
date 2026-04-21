/**
 * User Account Management Service
 * 用户管理 API 服务
 */
import type { AccountRole } from '@/types/permission'
import type { UserDepartmentsResponse, UserListResponse } from '@/types/user'
import { useMutation, useQuery } from '@tanstack/react-query'
import Cookies from 'js-cookie'
import { CSRF_COOKIE_NAME, CSRF_HEADER_NAME } from '@/config'

/**
 * 获取用户列表（从 Flask API）
 * 使用直接 fetch 调用 /console/api/accounts
 */
const fetchUserList = async (): Promise<UserListResponse> => {
  const url = '/console/api/accounts'
  const csrfToken = Cookies.get(CSRF_COOKIE_NAME()) || ''

  const response = await fetch(url, {
    method: 'GET',
    credentials: 'include',
    headers: {
      [CSRF_HEADER_NAME]: csrfToken,
    },
  })

  if (!response.ok) {
    throw new Error(`Failed to fetch user list: ${response.status}`)
  }

  return response.json()
}

/**
 * Hook to get user list
 */
export const useUserList = () => {
  return useQuery<UserListResponse>({
    queryKey: ['user-list'],
    queryFn: fetchUserList,
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
    retry: false,
  })
}

/**
 * 更新用户角色
 */
const updateUserRole = async (accountId: string, role: AccountRole): Promise<void> => {
  const url = `/console/api/accounts/${accountId}/role`
  const csrfToken = Cookies.get(CSRF_COOKIE_NAME()) || ''

  const response = await fetch(url, {
    method: 'PATCH',
    credentials: 'include',
    headers: {
      [CSRF_HEADER_NAME]: csrfToken,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ role }),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(error.error || `Failed to update user role: ${response.status}`)
  }
}

/**
 * Hook to update user role
 */
export const useUpdateUserRole = () => {
  return useMutation<void, Error, { accountId: string, role: AccountRole }>({
    mutationFn: ({ accountId, role }) => updateUserRole(accountId, role),
  })
}

/**
 * 更新用户信息（名字、状态）
 */
const updateUserInfo = async (accountId: string, data: { name?: string, status?: string }): Promise<void> => {
  const url = `/console/api/accounts/${accountId}/info`
  const csrfToken = Cookies.get(CSRF_COOKIE_NAME()) || ''

  const response = await fetch(url, {
    method: 'PATCH',
    credentials: 'include',
    headers: {
      [CSRF_HEADER_NAME]: csrfToken,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(error.error || `Failed to update user info: ${response.status}`)
  }
}

/**
 * Hook to update user info
 */
export const useUpdateUserInfo = () => {
  return useMutation<void, Error, { accountId: string, data: { name?: string, status?: string } }>({
    mutationFn: ({ accountId, data }) => updateUserInfo(accountId, data),
  })
}

/**
 * 重置用户密码
 */
const resetUserPassword = async (accountId: string): Promise<void> => {
  const url = `/console/api/accounts/${accountId}/reset-password`
  const csrfToken = Cookies.get(CSRF_COOKIE_NAME()) || ''

  const response = await fetch(url, {
    method: 'POST',
    credentials: 'include',
    headers: {
      [CSRF_HEADER_NAME]: csrfToken,
    },
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(error.error || `Failed to reset user password: ${response.status}`)
  }
}

/**
 * Hook to reset user password
 */
export const useResetUserPassword = () => {
  return useMutation<void, Error, string>({
    mutationFn: accountId => resetUserPassword(accountId),
  })
}

/**
 * 获取用户部门列表
 */
const fetchUserDepartments = async (accountId: string): Promise<UserDepartmentsResponse> => {
  const url = `/console/api/accounts/${accountId}/departments`
  const csrfToken = Cookies.get(CSRF_COOKIE_NAME()) || ''

  const response = await fetch(url, {
    method: 'GET',
    credentials: 'include',
    headers: {
      [CSRF_HEADER_NAME]: csrfToken,
    },
  })

  if (!response.ok) {
    throw new Error(`Failed to fetch user departments: ${response.status}`)
  }

  return response.json()
}

/**
 * Hook to get user departments
 */
export const useUserDepartments = (accountId: string) => {
  return useQuery<UserDepartmentsResponse>({
    queryKey: ['user-departments', accountId],
    queryFn: () => fetchUserDepartments(accountId),
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
    retry: false,
    enabled: !!accountId,
  })
}

/**
 * 更新用户部门
 */
const updateUserDepartments = async (accountId: string, departmentIds: string[]): Promise<void> => {
  const url = `/console/api/accounts/${accountId}/departments`
  const csrfToken = Cookies.get(CSRF_COOKIE_NAME()) || ''

  const response = await fetch(url, {
    method: 'PUT',
    credentials: 'include',
    headers: {
      [CSRF_HEADER_NAME]: csrfToken,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ department_ids: departmentIds }),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(error.error || `Failed to update user departments: ${response.status}`)
  }
}

/**
 * Hook to update user departments
 */
export const useUpdateUserDepartments = () => {
  return useMutation<void, Error, { accountId: string, departmentIds: string[] }>({
    mutationFn: ({ accountId, departmentIds }) => updateUserDepartments(accountId, departmentIds),
  })
}
