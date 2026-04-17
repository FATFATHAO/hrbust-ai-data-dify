export type Department = {
  id: string
  name: string
  description?: string
  parent_id?: string
  children?: Department[]
  member_count?: number
  created_at: string
  created_by?: string
}

export type DepartmentListResponse = {
  data: Department[]
  total: number
}

export type DepartmentTreeResponse = {
  data: Department[]
}

export type CreateDepartmentPayload = {
  name: string
  parent_id?: string
  description?: string
}

export type UpdateDepartmentPayload = {
  name?: string
  parent_id?: string
  description?: string
}

export type DepartmentMember = {
  id: string
  name: string
  email: string
  avatar?: string
  status?: string
  role?: string
  department_id?: string
}

export type DepartmentMemberListResponse = {
  data: DepartmentMember[]
  total: number
}
