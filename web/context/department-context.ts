'use client'

import type { QueryObserverResult, RefetchOptions } from '@tanstack/react-query'
import type { CreateDepartmentPayload, Department, DepartmentMember, UpdateDepartmentPayload } from '@/models/department'
import { noop } from 'es-toolkit/function'
import { createContext, useContext, useContextSelector } from 'use-context-selector'

type DepartmentContextValue = {
  departments: Department[]
  userDepartments: Department[]
  currentDepartment: Department | null
  isLoading: boolean
  refetchDepartments: (options?: RefetchOptions | undefined) => Promise<QueryObserverResult<Department[], Error>>
  fetchDepartmentTree: () => Promise<Department[]>
  createDepartment: (payload: CreateDepartmentPayload) => Promise<Department>
  updateDepartment: (id: string, payload: UpdateDepartmentPayload) => Promise<Department>
  deleteDepartment: (id: string) => Promise<void>
  setCurrentDepartment: (department: Department | null) => void
  getDepartmentMembers: (id: string) => Promise<DepartmentMember[]>
  addDepartmentMember: (departmentId: string, accountId: string) => Promise<void>
  removeDepartmentMember: (departmentId: string, accountId: string) => Promise<void>
}

type NoopFn = (...args: never[]) => unknown

const typedNoop = noop as NoopFn

export const DepartmentContext = createContext<DepartmentContextValue>({
  departments: [],
  userDepartments: [],
  currentDepartment: null,
  isLoading: false,
  refetchDepartments: typedNoop,
  fetchDepartmentTree: typedNoop,
  createDepartment: typedNoop,
  updateDepartment: typedNoop,
  deleteDepartment: typedNoop,
  setCurrentDepartment: typedNoop,
  getDepartmentMembers: typedNoop,
  addDepartmentMember: typedNoop,
  removeDepartmentMember: typedNoop,
})

export const useDepartmentContext = () => useContext(DepartmentContext)

export const useDepartmentContextWithSelector = <T>(selector: (value: DepartmentContextValue) => T): T => {
  return useContextSelector(DepartmentContext, selector)
}

export default DepartmentContext
