'use client'

import type { Department } from '@/models/department'
import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useParams, useRouter } from '@/next/navigation'
import { getDepartment, updateDepartment } from '@/service/department'

const DepartmentSettingsPage = () => {
  const { t } = useTranslation()
  const router = useRouter()
  const params = useParams()
  const departmentId = params.departmentId as string

  const [department, setDepartment] = useState<Department | null>(null)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    const loadDepartment = async () => {
      setIsLoading(true)
      try {
        const data = await getDepartment(departmentId)
        setDepartment(data)
        setName(data.name)
        setDescription(data.description || '')
      }
      catch (error) {
        console.error('Failed to load department:', error)
      }
      finally {
        setIsLoading(false)
      }
    }
    loadDepartment()
  }, [departmentId])

  const handleSubmit = async () => {
    if (!name.trim())
      return
    setIsSubmitting(true)
    try {
      await updateDepartment(departmentId, { name, description })
      router.push(`/departments/${departmentId}`)
    }
    catch (error) {
      console.error('Failed to update department:', error)
    }
    finally {
      setIsSubmitting(false)
    }
  }

  if (isLoading) {
    return <div className="flex h-full items-center justify-center">{t('common.loading')}</div>
  }

  if (!department) {
    return <div className="flex h-full items-center justify-center">{t('departments.notFound')}</div>
  }

  return (
    <div className="flex h-full flex-col p-8">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-text-primary">
          {t('departments.settings')}
        </h1>
        <p className="text-text-secondary">
          {t('departments.settingsDescription')}
        </p>
      </div>

      <div className="w-full max-w-lg space-y-4">
        <div>
          <label className="mb-1 block text-sm font-medium text-text-secondary">
            {t('departments.name')}
            {' '}
            <span className="text-text-error">*</span>
          </label>
          <input
            type="text"
            value={name}
            onChange={e => setName(e.target.value)}
            className="border-components-input-border bg-components-input-bg focus:border-components-input-border-focus h-8 w-full rounded-lg border px-3 text-sm text-text-primary outline-none focus:ring-1 focus:ring-state-accent-solid"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-text-secondary">
            {t('departments.description')}
          </label>
          <textarea
            value={description}
            onChange={e => setDescription(e.target.value)}
            className="border-components-input-border bg-components-input-bg focus:border-components-input-border-focus w-full rounded-lg border px-3 py-2 text-sm text-text-primary outline-none focus:ring-1 focus:ring-state-accent-solid"
            rows={3}
          />
        </div>

        <div className="flex justify-end gap-2 pt-4">
          <button
            onClick={() => router.back()}
            className="inline-flex cursor-pointer items-center justify-center rounded-lg border-[0.5px] border-components-button-secondary-border bg-components-button-secondary-bg px-3.5 py-1.5 text-[13px] font-medium text-components-button-secondary-text shadow-xs backdrop-blur-[5px] hover:border-components-button-secondary-border-hover hover:bg-components-button-secondary-bg-hover"
          >
            {t('common.cancel')}
          </button>
          <button
            onClick={handleSubmit}
            disabled={isSubmitting || !name.trim()}
            className="inline-flex cursor-pointer items-center justify-center rounded-lg border border-components-button-primary-border bg-components-button-primary-bg px-3.5 py-1.5 text-[13px] font-medium text-components-button-primary-text shadow hover:border-components-button-primary-border-hover hover:bg-components-button-primary-bg-hover disabled:cursor-not-allowed disabled:border-components-button-primary-border-disabled disabled:bg-components-button-primary-bg-disabled disabled:text-components-button-primary-text-disabled"
          >
            {isSubmitting ? t('common.saving') : t('common.save')}
          </button>
        </div>
      </div>
    </div>
  )
}

export default DepartmentSettingsPage
