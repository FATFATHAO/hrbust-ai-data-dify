'use client'

import type { Department } from '@/models/department'
import type { UserInfo } from '@/types/user'
import { useQuery } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import { Button } from '@/app/components/base/ui/button'
import { Dialog, DialogContent } from '@/app/components/base/ui/dialog'
import BatchUserImportModal from '@/app/components/batch-user-import-modal'
import { useAppContext } from '@/context/app-context'
import { fetchDepartments } from '@/service/department'
import { useResetUserPassword, useUpdateUserDepartments, useUpdateUserInfo, useUserList } from '@/service/use-account'
import { getRoleLabel } from '@/types/user'

// Component to display all departments with checkboxes
const DepartmentCheckboxList = ({ selectedDepts, onToggle }: { selectedDepts: string[], onToggle: (id: string) => void }) => {
  const { data: allDeptsResp, isLoading } = useQuery({
    queryKey: ['all-departments-for-selection'],
    queryFn: fetchDepartments,
  })

  if (isLoading) {
    return <p className="py-4 text-center text-sm text-text-secondary">加载中...</p>
  }

  const departments = allDeptsResp?.data || []

  if (departments.length === 0) {
    return <p className="py-4 text-center text-sm text-text-secondary">暂无可用部门</p>
  }

  return (
    <div className="max-h-60 space-y-2 overflow-y-auto">
      {departments.map((dept: Department) => (
        <label key={dept.id} className="hover:bg-state-hover-bg flex cursor-pointer items-center gap-3 rounded-lg p-2">
          <input
            type="checkbox"
            checked={selectedDepts.includes(dept.id)}
            onChange={() => onToggle(dept.id)}
            className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-600"
          />
          <span className="text-sm text-text-primary">{dept.name}</span>
        </label>
      ))}
    </div>
  )
}

const UsersPage = () => {
  const { accountRole } = useAppContext()
  const [mounted, setMounted] = useState(false)
  useEffect(() => {
    // eslint-disable-next-line react/set-state-in-effect
    setMounted(true)
  }, [])
  const { data: userListResp, isLoading, refetch } = useUserList()

  // Batch import modal state
  const [showBatchImportModal, setShowBatchImportModal] = useState(false)
  const { data: allDeptsResp } = useQuery({
    queryKey: ['all-departments-for-users'],
    queryFn: fetchDepartments,
  })
  const updateInfoMutation = useUpdateUserInfo()
  const resetPasswordMutation = useResetUserPassword()

  const [editingUser, setEditingUser] = useState<UserInfo | null>(null)
  const [editName, setEditName] = useState('')
  const [editStatus, setEditStatus] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [actionType, setActionType] = useState<'name' | 'status' | 'password' | 'departments' | null>(null)

  // Department editing state
  const [showDeptDialog, setShowDeptDialog] = useState(false)
  const updateDeptsMutation = useUpdateUserDepartments()
  const [selectedDepts, setSelectedDepts] = useState<string[]>([])

  const users = userListResp?.data ?? []

  // Create department ID to name lookup
  const deptIdToName = (deptId: string) => {
    const dept = allDeptsResp?.data?.find((d: Department) => d.id === deptId)
    return dept?.name || deptId
  }

  const getDeptNamesFromIds = (deptIds: string[]) => {
    if (!deptIds || deptIds.length === 0)
      return '-'
    return deptIds.map(id => deptIdToName(id)).join(', ')
  }

  const handleEditClick = (user: UserInfo, type: 'name' | 'status' | 'password' | 'departments') => {
    setEditingUser(user)
    setActionType(type)
    if (type === 'name') {
      setEditName(user.name || '')
    }
    else if (type === 'status') {
      setEditStatus(user.status)
    }
    else if (type === 'departments') {
      setSelectedDepts(user.departments || [])
      setShowDeptDialog(true)
    }
  }

  const handleCancelEdit = () => {
    setEditingUser(null)
    setActionType(null)
    setEditName('')
    setEditStatus('')
    setShowDeptDialog(false)
  }

  const handleSaveName = async () => {
    if (!editingUser)
      return

    setIsSubmitting(true)
    try {
      await updateInfoMutation.mutateAsync({
        accountId: editingUser.account_id,
        data: { name: editName },
      })
      handleCancelEdit()
      refetch()
    }
    catch (error) {
      console.error('Failed to update user name:', error)
    }
    finally {
      setIsSubmitting(false)
    }
  }

  const handleSaveStatus = async () => {
    if (!editingUser)
      return

    setIsSubmitting(true)
    try {
      await updateInfoMutation.mutateAsync({
        accountId: editingUser.account_id,
        data: { status: editStatus },
      })
      handleCancelEdit()
      refetch()
    }
    catch (error) {
      console.error('Failed to update user status:', error)
    }
    finally {
      setIsSubmitting(false)
    }
  }

  const handleResetPassword = async () => {
    if (!editingUser)
      return

    setIsSubmitting(true)
    try {
      await resetPasswordMutation.mutateAsync(editingUser.account_id)
      handleCancelEdit()
    }
    catch (error) {
      console.error('Failed to reset password:', error)
    }
    finally {
      setIsSubmitting(false)
    }
  }

  const handleSaveDepartments = async () => {
    if (!editingUser)
      return

    setIsSubmitting(true)
    try {
      await updateDeptsMutation.mutateAsync({
        accountId: editingUser.account_id,
        departmentIds: selectedDepts,
      })
      setShowDeptDialog(false)
      handleCancelEdit()
      refetch()
    }
    catch (error) {
      console.error('Failed to update departments:', error)
    }
    finally {
      setIsSubmitting(false)
    }
  }

  const toggleDeptSelection = (deptId: string) => {
    setSelectedDepts(prev =>
      prev.includes(deptId)
        ? prev.filter(id => id !== deptId)
        : [...prev, deptId],
    )
  }

  const formatDate = (dateStr: string | null) => {
    if (!dateStr)
      return '-'
    try {
      const date = new Date(dateStr)
      return date.toLocaleString('zh-CN')
    }
    catch {
      return dateStr
    }
  }

  return (
    <div className="flex h-full flex-col p-8">
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-text-primary">
            用户管理
          </h1>
          <p className="text-text-secondary">
            管理系统中的用户账户
          </p>
        </div>
        {mounted && accountRole === 'admin' && (
          <div className="flex gap-2">
            <Button variant="secondary" onClick={() => setShowBatchImportModal(true)}>
              批量导入
            </Button>
          </div>
        )}
      </div>

      {/* Edit Panel - Name */}
      {(editingUser && actionType === 'name') && (
        <div className="bg-components-card mb-6 rounded-lg border border-divider-regular p-6">
          <div className="mb-4">
            <h3 className="mb-4 text-lg font-medium text-text-primary">
              编辑用户姓名
            </h3>
            <div className="mb-4 flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#E8F9F6] text-[#0E9A6F]">
                <span className="text-sm font-semibold">
                  {(editingUser.name || editingUser.email || '?').charAt(0).toUpperCase()}
                </span>
              </div>
              <div>
                <div className="font-medium text-text-primary">{editingUser.name || '-'}</div>
                <div className="text-sm text-text-secondary">{editingUser.email}</div>
              </div>
            </div>
            <label className="mb-2 block text-sm font-medium text-text-secondary">
              姓名
            </label>
            <input
              type="text"
              value={editName}
              onChange={e => setEditName(e.target.value)}
              className="border-components-input-border bg-components-input-bg focus:border-components-input-border-focus h-9 w-full rounded-lg border px-3 text-sm text-text-primary outline-none focus:ring-1 focus:ring-state-accent-solid"
            />
          </div>
          <div className="flex justify-end gap-2">
            <button
              onClick={handleCancelEdit}
              className="h-8 rounded-lg border border-components-button-secondary-border bg-components-button-secondary-bg px-4 text-sm font-medium text-components-button-secondary-text hover:border-components-button-secondary-border-hover hover:bg-components-button-secondary-bg-hover"
            >
              取消
            </button>
            <button
              onClick={handleSaveName}
              disabled={isSubmitting}
              className="h-8 rounded-lg border border-components-button-primary-border bg-components-button-primary-bg px-4 text-sm font-medium text-components-button-primary-text hover:border-components-button-primary-border-hover hover:bg-components-button-primary-bg-hover disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isSubmitting ? '保存中...' : '保存'}
            </button>
          </div>
        </div>
      )}

      {/* Edit Panel - Status */}
      {(editingUser && actionType === 'status') && (
        <div className="bg-components-card mb-6 rounded-lg border border-divider-regular p-6">
          <h3 className="mb-4 text-lg font-medium text-text-primary">
            编辑用户状态
          </h3>
          <div className="mb-4 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#E8F9F6] text-[#0E9A6F]">
              <span className="text-sm font-semibold">
                {(editingUser.name || editingUser.email || '?').charAt(0).toUpperCase()}
              </span>
            </div>
            <div>
              <div className="font-medium text-text-primary">{editingUser.name || '-'}</div>
              <div className="text-sm text-text-secondary">{editingUser.email}</div>
            </div>
          </div>
          <label className="mb-2 block text-sm font-medium text-text-secondary">
            状态
          </label>
          <select
            value={editStatus}
            onChange={e => setEditStatus(e.target.value)}
            className="border-components-input-border bg-components-input-bg focus:border-components-input-border-focus h-9 w-full rounded-lg border px-3 text-sm text-text-primary outline-none focus:ring-1 focus:ring-state-accent-solid"
          >
            <option value="active">启用</option>
            <option value="banned">禁用</option>
            <option value="closed">关闭</option>
          </select>
          <div className="mt-4 flex justify-end gap-2">
            <button
              onClick={handleCancelEdit}
              className="h-8 rounded-lg border border-components-button-secondary-border bg-components-button-secondary-bg px-4 text-sm font-medium text-components-button-secondary-text hover:border-components-button-secondary-border-hover hover:bg-components-button-secondary-bg-hover"
            >
              取消
            </button>
            <button
              onClick={handleSaveStatus}
              disabled={isSubmitting}
              className="h-8 rounded-lg border border-components-button-primary-border bg-components-button-primary-bg px-4 text-sm font-medium text-components-button-primary-text hover:border-components-button-primary-border-hover hover:bg-components-button-primary-bg-hover disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isSubmitting ? '保存中...' : '保存'}
            </button>
          </div>
        </div>
      )}

      {/* Edit Panel - Password */}
      {(editingUser && actionType === 'password') && (
        <div className="bg-components-card mb-6 rounded-lg border border-divider-regular p-6">
          <h3 className="mb-4 text-lg font-medium text-text-primary">
            重置密码
          </h3>
          <div className="mb-4 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#E8F9F6] text-[#0E9A6F]">
              <span className="text-sm font-semibold">
                {(editingUser.name || editingUser.email || '?').charAt(0).toUpperCase()}
              </span>
            </div>
            <div>
              <div className="font-medium text-text-primary">{editingUser.name || '-'}</div>
              <div className="text-sm text-text-secondary">{editingUser.email}</div>
            </div>
          </div>
          <p className="mb-4 text-text-secondary">
            确定要重置此用户的密码吗？密码将被重置为随机值，管理员需要手动通知用户。
          </p>
          <div className="flex justify-end gap-2">
            <button
              onClick={handleCancelEdit}
              className="h-8 rounded-lg border border-components-button-secondary-border bg-components-button-secondary-bg px-4 text-sm font-medium text-components-button-secondary-text hover:border-components-button-secondary-border-hover hover:bg-components-button-secondary-bg-hover"
            >
              取消
            </button>
            <button
              onClick={handleResetPassword}
              disabled={isSubmitting}
              className="h-8 rounded-lg border border-components-button-primary-border bg-components-button-primary-bg px-4 text-sm font-medium text-components-button-primary-text hover:border-components-button-primary-border-hover hover:bg-components-button-primary-bg-hover disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isSubmitting ? '重置中...' : '确认重置'}
            </button>
          </div>
        </div>
      )}

      {/* Department Selection Dialog */}
      <Dialog
        open={showDeptDialog && !!editingUser}
        onOpenChange={(open) => {
          if (!open)
            handleCancelEdit()
        }}
      >
        <DialogContent className="w-[480px]">
          <h3 className="mb-4 text-lg font-medium text-text-primary">
            设置部门 -
            {' '}
            {editingUser?.name || editingUser?.email}
          </h3>
          <p className="mb-4 text-sm text-text-secondary">选择用户所属的部门：</p>
          <DepartmentCheckboxList selectedDepts={selectedDepts} onToggle={toggleDeptSelection} />
          <div className="mt-4 flex justify-end gap-2">
            <button
              onClick={() => handleCancelEdit()}
              className="h-8 rounded-lg border border-components-button-secondary-border bg-components-button-secondary-bg px-4 text-sm font-medium text-components-button-secondary-text hover:border-components-button-secondary-border-hover hover:bg-components-button-secondary-bg-hover"
            >
              取消
            </button>
            <button
              onClick={handleSaveDepartments}
              disabled={isSubmitting}
              className="h-8 rounded-lg border border-components-button-primary-border bg-components-button-primary-bg px-4 text-sm font-medium text-components-button-primary-text hover:border-components-button-primary-border-hover hover:bg-components-button-primary-bg-hover disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isSubmitting ? '保存中...' : '保存'}
            </button>
          </div>
        </DialogContent>
      </Dialog>

      {/* User List Table */}
      {isLoading
        ? (
            <div className="flex flex-1 items-center justify-center">
              <div className="text-text-secondary">加载中...</div>
            </div>
          )
        : users.length === 0
          ? (
              <div className="flex flex-1 items-center justify-center rounded-lg border border-divider-regular">
                <div className="text-text-secondary">暂无用户</div>
              </div>
            )
          : (
              <div className="bg-components-card flex-1 overflow-hidden rounded-lg border border-divider-regular">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="border-b border-divider-regular bg-background-default-subtle">
                      <tr>
                        <th className="px-4 py-3 text-left text-sm font-medium text-text-secondary">用户</th>
                        <th className="px-4 py-3 text-left text-sm font-medium text-text-secondary">角色</th>
                        <th className="px-4 py-3 text-left text-sm font-medium text-text-secondary">状态</th>
                        <th className="px-4 py-3 text-left text-sm font-medium text-text-secondary">部门</th>
                        <th className="px-4 py-3 text-left text-sm font-medium text-text-secondary">最后登录IP</th>
                        <th className="px-4 py-3 text-left text-sm font-medium text-text-secondary">创建时间</th>
                        <th className="px-4 py-3 text-left text-sm font-medium text-text-secondary">操作</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-divider-subtle">
                      {users.map(user => (
                        <tr key={user.account_id} className="hover:bg-state-hover-bg">
                          <td className="px-4 py-3">
                            <div className="flex items-center gap-3">
                              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-[#E8F9F6] text-[#0E9A6F]">
                                <span className="text-sm font-semibold">
                                  {(user.name || user.email || '?').charAt(0).toUpperCase()}
                                </span>
                              </div>
                              <div>
                                <div className="text-sm font-medium text-text-primary">{user.name || '-'}</div>
                                <div className="text-xs text-text-secondary">{user.email || '-'}</div>
                              </div>
                            </div>
                          </td>
                          <td className="px-4 py-3">
                            <span className="bg-state-accent-solid-bg inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium text-state-accent-solid">
                              {getRoleLabel(user.account_role)}
                            </span>
                          </td>
                          <td className="px-4 py-3">
                            <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
                              user.status === 'active'
                                ? 'bg-green-50 text-green-600'
                                : user.status === 'banned'
                                  ? 'bg-red-50 text-red-600'
                                  : 'bg-gray-50 text-gray-600'
                            }`}
                            >
                              {user.status === 'active' ? '启用' : user.status === 'banned' ? '禁用' : '关闭'}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-sm text-text-secondary">
                            {getDeptNamesFromIds(user.departments)}
                          </td>
                          <td className="px-4 py-3 text-sm text-text-secondary">{user.last_login_ip || '-'}</td>
                          <td className="px-4 py-3 text-sm text-text-secondary">{formatDate(user.created_at)}</td>
                          <td className="px-4 py-3">
                            <div className="flex items-center gap-1">
                              <button
                                onClick={() => handleEditClick(user, 'name')}
                                className="hover:bg-state-hover-bg rounded-md px-2 py-1 text-xs text-text-secondary hover:text-text-primary"
                              >
                                姓名
                              </button>
                              <button
                                onClick={() => handleEditClick(user, 'status')}
                                className="hover:bg-state-hover-bg rounded-md px-2 py-1 text-xs text-text-secondary hover:text-text-primary"
                              >
                                状态
                              </button>
                              {mounted && accountRole === 'admin' && (
                                <button
                                  onClick={() => handleEditClick(user, 'password')}
                                  className="hover:bg-state-hover-bg rounded-md px-2 py-1 text-xs text-text-secondary hover:text-text-primary"
                                >
                                  重置密码
                                </button>
                              )}
                              <button
                                onClick={() => handleEditClick(user, 'departments')}
                                className="hover:bg-state-hover-bg rounded-md px-2 py-1 text-xs text-text-secondary hover:text-text-primary"
                              >
                                部门
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

      {/* Batch Import Modal */}
      <BatchUserImportModal
        isShow={showBatchImportModal}
        onCancel={() => setShowBatchImportModal(false)}
        onSuccess={() => {
          setShowBatchImportModal(false)
          refetch()
        }}
      />
    </div>
  )
}

export default UsersPage
