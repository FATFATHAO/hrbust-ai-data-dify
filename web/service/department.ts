/**
 * Department Service
 * 部门管理 API 服务
 * 部门端点在 Flask API 中，路径为 /console/api/departments
 */
import type {
  CreateDepartmentPayload,
  Department,
  DepartmentListResponse,
  DepartmentMemberListResponse,
  DepartmentTreeResponse,
  UpdateDepartmentPayload,
} from '@/models/department'
import Cookies from 'js-cookie'
import { CSRF_COOKIE_NAME, CSRF_HEADER_NAME } from '@/config'

const departmentFetch = async (
  url: string,
  options: RequestInit = {},
): Promise<Response> => {
  const csrfToken = Cookies.get(CSRF_COOKIE_NAME()) || ''

  return fetch(url, {
    ...options,
    credentials: 'include',
    headers: {
      [CSRF_HEADER_NAME]: csrfToken,
      'Content-Type': 'application/json',
      ...options.headers,
    },
  })
}

export const fetchDepartments = async (): Promise<DepartmentListResponse> => {
  const response = await departmentFetch('/console/api/departments')
  if (!response.ok) {
    const errorText = await response.text()
    console.error('Fetch departments failed:', errorText)
    throw new Error(`Failed to fetch departments: ${response.status} - ${errorText}`)
  }
  return response.json()
}

export const fetchDepartmentTree = async (): Promise<DepartmentTreeResponse> => {
  const response = await departmentFetch('/console/api/departments?include_tree=true')
  if (!response.ok) {
    throw new Error(`Failed to fetch department tree: ${response.status}`)
  }
  return response.json()
}

export const createDepartment = async (body: CreateDepartmentPayload): Promise<Department> => {
  const response = await departmentFetch('/console/api/departments', {
    method: 'POST',
    body: JSON.stringify(body),
  })
  if (!response.ok) {
    const errorText = await response.text()
    console.error('Create department failed:', errorText)
    throw new Error(`Failed to create department: ${response.status} - ${errorText}`)
  }
  return response.json()
}

export const getDepartment = async (id: string): Promise<Department> => {
  const response = await departmentFetch(`/console/api/departments/${id}`)
  if (!response.ok) {
    throw new Error(`Failed to get department: ${response.status}`)
  }
  return response.json()
}

export const updateDepartment = async (id: string, body: UpdateDepartmentPayload): Promise<Department> => {
  const response = await departmentFetch(`/console/api/departments/${id}`, {
    method: 'PUT',
    body: JSON.stringify(body),
  })
  if (!response.ok) {
    throw new Error(`Failed to update department: ${response.status}`)
  }
  return response.json()
}

export const deleteDepartment = async (id: string): Promise<void> => {
  const response = await departmentFetch(`/console/api/departments/${id}`, {
    method: 'DELETE',
  })
  if (!response.ok) {
    throw new Error(`Failed to delete department: ${response.status}`)
  }
}

export const getDepartmentMembers = async (id: string): Promise<DepartmentMemberListResponse> => {
  const response = await departmentFetch(`/console/api/departments/${id}/members`)
  if (!response.ok) {
    throw new Error(`Failed to get department members: ${response.status}`)
  }
  return response.json()
}

export const addDepartmentMember = async (id: string, account_id: string): Promise<void> => {
  const response = await departmentFetch(`/console/api/departments/${id}/members`, {
    method: 'POST',
    body: JSON.stringify({ account_id }),
  })
  if (!response.ok) {
    throw new Error(`Failed to add department member: ${response.status}`)
  }
}

export const removeDepartmentMember = async (id: string, account_id: string): Promise<void> => {
  const response = await departmentFetch(`/console/api/departments/${id}/members/${account_id}`, {
    method: 'DELETE',
  })
  if (!response.ok) {
    throw new Error(`Failed to remove department member: ${response.status}`)
  }
}

export const getDepartmentChildren = async (id: string): Promise<DepartmentListResponse> => {
  const response = await departmentFetch(`/console/api/departments/${id}/children`)
  if (!response.ok) {
    throw new Error(`Failed to get department children: ${response.status}`)
  }
  return response.json()
}
