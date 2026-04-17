'use client'

import type { Department } from '@/models/department'
import { useCallback, useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useRouter } from '@/next/navigation'
import { createDepartment, deleteDepartment, fetchDepartments, updateDepartment } from '@/service/department'

const DepartmentsPage = () => {
  const { t } = useTranslation()
  const router = useRouter()
  const [departments, setDepartments] = useState<Department[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingDepartment, setEditingDepartment] = useState<Department | null>(null)
  const [newName, setNewName] = useState('')
  const [newDescription, setNewDescription] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [deletingDept, setDeletingDept] = useState<Department | null>(null)

  const loadDepartments = useCallback(async () => {
    setIsLoading(true)
    try {
      const response = await fetchDepartments()
      setDepartments(response.data)
    }
    catch (error) {
      console.error('Failed to load departments:', error)
    }
    finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    loadDepartments()
  }, [loadDepartments])

  const handleCreate = () => {
    setEditingDepartment(null)
    setNewName('')
    setNewDescription('')
    setShowForm(true)
  }

  const handleEdit = (department: Department) => {
    setEditingDepartment(department)
    setNewName(department.name)
    setNewDescription(department.description || '')
    setShowForm(true)
  }

  const handleDelete = async () => {
    if (!deletingDept)
      return
    try {
      await deleteDepartment(deletingDept.id)
      setDeletingDept(null)
      loadDepartments()
    }
    catch (error) {
      console.error('Failed to delete department:', error)
    }
  }

  const handleFormSubmit = async () => {
    if (!newName.trim())
      return
    setIsSubmitting(true)
    try {
      if (editingDepartment) {
        await updateDepartment(editingDepartment.id, { name: newName, description: newDescription })
      }
      else {
        await createDepartment({ name: newName, description: newDescription })
      }
      setShowForm(false)
      loadDepartments()
    }
    catch (error) {
      console.error('Failed to save department:', error)
    }
    finally {
      setIsSubmitting(false)
    }
  }

  const handleDepartmentClick = (department: Department) => {
    router.push(`/departments/${department.id}`)
  }

  const handleEditClick = (e: React.MouseEvent, department: Department) => {
    e.stopPropagation()
    handleEdit(department)
  }

  const handleDeleteClick = (e: React.MouseEvent, department: Department) => {
    e.stopPropagation()
    setDeletingDept(department)
  }

  return (
    <div className="flex h-full flex-col p-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-text-primary">
            {t('departments.title')}
          </h1>
          <p className="text-text-secondary">
            {t('departments.description')}
          </p>
        </div>
        <button
          onClick={handleCreate}
          className="inline-flex cursor-pointer items-center justify-center rounded-lg border border-components-button-primary-border bg-components-button-primary-bg px-3.5 py-1.5 text-[13px] font-medium whitespace-nowrap text-components-button-primary-text shadow hover:border-components-button-primary-border-hover hover:bg-components-button-primary-bg-hover disabled:cursor-not-allowed disabled:border-components-button-primary-border-disabled disabled:bg-components-button-primary-bg-disabled disabled:text-components-button-primary-text-disabled"
        >
          {t('departments.create')}
        </button>
      </div>

      {showForm && (
        <div className="bg-components-card mb-6 rounded-lg border border-divider-regular p-4">
          <div className="mb-4 space-y-3">
            <div>
              <label className="mb-1 block text-sm font-medium text-text-secondary">
                {t('departments.name')}
              </label>
              <input
                type="text"
                value={newName}
                onChange={e => setNewName(e.target.value)}
                className="border-components-input-border bg-components-input-bg focus:border-components-input-border-focus h-8 w-full rounded-lg border px-3 text-sm text-text-primary outline-none focus:ring-1 focus:ring-state-accent-solid"
                placeholder={t('departments.namePlaceholder')}
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-text-secondary">
                {t('departments.description')}
              </label>
              <textarea
                value={newDescription}
                onChange={e => setNewDescription(e.target.value)}
                className="border-components-input-border bg-components-input-bg focus:border-components-input-border-focus w-full rounded-lg border px-3 py-2 text-sm text-text-primary outline-none focus:ring-1 focus:ring-state-accent-solid"
                rows={2}
                placeholder={t('departments.descriptionPlaceholder')}
              />
            </div>
          </div>
          <div className="flex justify-end gap-2">
            <button
              onClick={() => setShowForm(false)}
              className="inline-flex cursor-pointer items-center justify-center rounded-lg border-[0.5px] border-components-button-secondary-border bg-components-button-secondary-bg px-3.5 py-1.5 text-[13px] font-medium text-components-button-secondary-text shadow-xs backdrop-blur-[5px] hover:border-components-button-secondary-border-hover hover:bg-components-button-secondary-bg-hover"
            >
              {t('common.cancel')}
            </button>
            <button
              onClick={handleFormSubmit}
              disabled={isSubmitting || !newName.trim()}
              className="inline-flex cursor-pointer items-center justify-center rounded-lg border border-components-button-primary-border bg-components-button-primary-bg px-3.5 py-1.5 text-[13px] font-medium text-components-button-primary-text shadow hover:border-components-button-primary-border-hover hover:bg-components-button-primary-bg-hover disabled:cursor-not-allowed disabled:border-components-button-primary-border-disabled disabled:bg-components-button-primary-bg-disabled disabled:text-components-button-primary-text-disabled"
            >
              {isSubmitting ? t('common.saving') : t('common.save')}
            </button>
          </div>
        </div>
      )}

      {isLoading
        ? (
            <div className="flex-1 text-center text-text-secondary">{t('common.loading')}</div>
          )
        : departments.length === 0
          ? (
              <div className="flex-1 rounded-lg border border-divider-regular p-8 text-center text-text-secondary">
                {t('departments.empty')}
              </div>
            )
          : (
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
                {departments.map(department => (
                  <div
                    key={department.id}
                    className="group bg-components-card hover:border-line-default-hover relative flex cursor-pointer flex-col gap-2 rounded-lg border border-divider-regular p-4 transition-all hover:shadow-xs"
                    onClick={() => handleDepartmentClick(department)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-2">
                        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#E8F9F6] text-[#0E9A6F]">
                          <span className="text-lg font-semibold">{department.name.charAt(0).toUpperCase()}</span>
                        </div>
                        <div>
                          <h3 className="font-medium text-text-primary">{department.name}</h3>
                          {department.description && (
                            <p className="text-sm text-text-secondary">{department.description}</p>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="mt-2 flex items-center gap-4 text-sm text-text-tertiary">
                      {department.member_count !== undefined && (
                        <span>
                          {department.member_count}
                          {' '}
                          {t('departments.members')}
                        </span>
                      )}
                    </div>
                    <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100">
                      <div className="bg-components-card flex gap-1 rounded-md p-1 shadow-md">
                        <button
                          onClick={e => handleEditClick(e, department)}
                          className="hover:bg-state-hover-bg rounded px-2 py-1 text-xs"
                        >
                          {t('common.edit')}
                        </button>
                        <button
                          onClick={e => handleDeleteClick(e, department)}
                          className="text-text-error hover:bg-state-hover-bg rounded px-2 py-1 text-xs"
                        >
                          {t('common.delete')}
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

      {deletingDept && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-components-card rounded-lg p-6 shadow-lg">
            <p className="mb-4 text-text-primary">
              {t('departments.deleteConfirmContent', { name: deletingDept.name })}
            </p>
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setDeletingDept(null)}
                className="rounded-lg border border-components-button-secondary-border bg-components-button-secondary-bg px-3.5 py-1.5 text-sm font-medium text-components-button-secondary-text hover:bg-components-button-secondary-bg-hover"
              >
                {t('common.cancel')}
              </button>
              <button
                onClick={handleDelete}
                className="rounded-lg border border-components-button-primary-border bg-components-button-primary-bg px-3.5 py-1.5 text-sm font-medium text-components-button-primary-text hover:bg-components-button-primary-bg-hover"
              >
                {t('common.delete')}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default DepartmentsPage
