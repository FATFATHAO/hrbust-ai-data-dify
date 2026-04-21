'use client'

import type { Department, DepartmentMember } from '@/models/department'
import { useEffect, useState } from 'react'
import { useParams, useRouter } from '@/next/navigation'
import { addDepartmentMember, getDepartment, getDepartmentMembers, removeDepartmentMember } from '@/service/department'

const DepartmentDetailPage = () => {
  const router = useRouter()
  const params = useParams()
  const departmentId = params.departmentId as string

  const [department, setDepartment] = useState<Department | null>(null)
  const [members, setMembers] = useState<DepartmentMember[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [newMemberId, setNewMemberId] = useState('')
  const [isAdding, setIsAdding] = useState(false)

  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true)
      try {
        const [deptData, membersData] = await Promise.all([
          getDepartment(departmentId),
          getDepartmentMembers(departmentId),
        ])
        setDepartment(deptData)
        setMembers(membersData.data)
      }
      catch (error) {
        console.error('Failed to load department:', error)
      }
      finally {
        setIsLoading(false)
      }
    }
    loadData()
  }, [departmentId])

  const handleAddMember = async () => {
    if (!newMemberId.trim())
      return
    setIsAdding(true)
    try {
      await addDepartmentMember(departmentId, newMemberId.trim())
      const membersData = await getDepartmentMembers(departmentId)
      setMembers(membersData.data)
      setNewMemberId('')
    }
    catch (error) {
      console.error('Failed to add member:', error)
    }
    finally {
      setIsAdding(false)
    }
  }

  const handleRemoveMember = async (member: DepartmentMember) => {
    try {
      await removeDepartmentMember(departmentId, member.account_id)
      setMembers(prev => prev.filter(m => m.account_id !== member.account_id))
    }
    catch (error) {
      console.error('Failed to remove member:', error)
    }
  }

  if (isLoading) {
    return <div className="flex h-full items-center justify-center">加载中...</div>
  }

  if (!department) {
    return <div className="flex h-full items-center justify-center">部门不存在</div>
  }

  return (
    <div className="flex h-full flex-col p-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-text-primary">{department.name}</h1>
          {department.description && (
            <p className="text-text-secondary">{department.description}</p>
          )}
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => router.push('/departments')}
            className="inline-flex cursor-pointer items-center justify-center rounded-lg border-[0.5px] border-components-button-secondary-border bg-components-button-secondary-bg px-3.5 py-1.5 text-[13px] font-medium text-components-button-secondary-text shadow-xs backdrop-blur-[5px] hover:border-components-button-secondary-border-hover hover:bg-components-button-secondary-bg-hover"
          >
            返回
          </button>
          <button
            onClick={() => router.push(`/departments/${departmentId}/settings`)}
            className="inline-flex cursor-pointer items-center justify-center rounded-lg border-[0.5px] border-components-button-secondary-border bg-components-button-secondary-bg px-3.5 py-1.5 text-[13px] font-medium text-components-button-secondary-text shadow-xs backdrop-blur-[5px] hover:border-components-button-secondary-border-hover hover:bg-components-button-secondary-bg-hover"
          >
            设置
          </button>
        </div>
      </div>

      <div className="mb-4 flex items-center gap-2">
        <input
          type="text"
          value={newMemberId}
          onChange={e => setNewMemberId(e.target.value)}
          placeholder="输入用户ID添加成员"
          className="border-components-input-border bg-components-input-bg focus:border-components-input-border-focus h-8 w-64 rounded-lg border px-3 text-sm text-text-primary outline-none focus:ring-1 focus:ring-state-accent-solid"
        />
        <button
          onClick={handleAddMember}
          disabled={isAdding || !newMemberId.trim()}
          className="inline-flex cursor-pointer items-center justify-center rounded-lg border border-components-button-primary-border bg-components-button-primary-bg px-3.5 py-1.5 text-[13px] font-medium text-components-button-primary-text shadow hover:border-components-button-primary-border-hover hover:bg-components-button-primary-bg-hover disabled:cursor-not-allowed disabled:border-components-button-primary-border-disabled disabled:bg-components-button-primary-bg-disabled disabled:text-components-button-primary-text-disabled"
        >
          添加成员
        </button>
      </div>

      <div className="flex-1">
        <h2 className="mb-4 text-lg font-medium text-text-primary">
          部门成员
          {' '}
          (
          {members.length}
          )
        </h2>
        {members.length === 0
          ? (
              <div className="rounded-lg border border-divider-regular p-6 text-center text-text-secondary">
                暂无成员
              </div>
            )
          : (
              <div className="flex flex-col gap-2">
                {members.map(member => (
                  <div key={member.id} className="bg-components_card flex items-center justify-between rounded-lg border border-divider-regular p-3">
                    <div className="flex items-center gap-3">
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary-50 text-sm font-medium text-primary-600">
                        {member.name ? member.name.charAt(0).toUpperCase() : '?'}
                      </div>
                      <div>
                        <div className="font-medium text-text-primary">{member.name || '-'}</div>
                        <div className="text-sm text-text-secondary">{member.email || '-'}</div>
                      </div>
                    </div>
                    <button
                      onClick={() => handleRemoveMember(member)}
                      className="text-text-error hover:bg-state-hover-bg rounded px-2 py-1 text-sm"
                    >
                      移除
                    </button>
                  </div>
                ))}
              </div>
            )}
      </div>
    </div>
  )
}

export default DepartmentDetailPage
