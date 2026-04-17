import type {
  CreateDepartmentPayload,
  Department,
  DepartmentListResponse,
  DepartmentMemberListResponse,
  DepartmentTreeResponse,
  UpdateDepartmentPayload,
} from '@/models/department'
import { del, get, post, put } from './base'

export const fetchDepartments = (): Promise<DepartmentListResponse> => {
  return get<DepartmentListResponse>('/departments')
}

export const fetchDepartmentTree = (): Promise<DepartmentTreeResponse> => {
  return get<DepartmentTreeResponse>('/departments/tree')
}

export const createDepartment = (body: CreateDepartmentPayload): Promise<Department> => {
  return post<Department>('/departments', { body })
}

export const getDepartment = (id: string): Promise<Department> => {
  return get<Department>(`/departments/${id}`)
}

export const updateDepartment = (id: string, body: UpdateDepartmentPayload): Promise<Department> => {
  return put<Department>(`/departments/${id}`, { body })
}

export const deleteDepartment = (id: string): Promise<void> => {
  return del<void>(`/departments/${id}`)
}

export const getDepartmentMembers = (id: string): Promise<DepartmentMemberListResponse> => {
  return get<DepartmentMemberListResponse>(`/departments/${id}/members`)
}

export const addDepartmentMember = (id: string, account_id: string): Promise<void> => {
  return post(`/departments/${id}/members`, { body: { account_id } })
}

export const removeDepartmentMember = (id: string, account_id: string): Promise<void> => {
  return del<void>(`/departments/${id}/members/${account_id}`)
}

export const getDepartmentChildren = (id: string): Promise<DepartmentListResponse> => {
  return get<DepartmentListResponse>(`/departments/${id}/children`)
}
