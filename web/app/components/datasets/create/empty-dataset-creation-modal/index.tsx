'use client'
import type { Department } from '@/models/department'
import { cn } from '@langgenius/dify-ui/cn'
import * as React from 'react'
import { useCallback, useEffect, useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { trackEvent } from '@/app/components/base/amplitude'
import Input from '@/app/components/base/input'
// eslint-disable-next-line no-restricted-imports
import Modal from '@/app/components/base/modal'
import { Button } from '@/app/components/base/ui/button'
import { toast } from '@/app/components/base/ui/toast'
import { useRouter } from '@/next/navigation'
import { createEmptyDataset } from '@/service/datasets'
import { fetchDepartments } from '@/service/department'
import { useInvalidDatasetList } from '@/service/knowledge/use-dataset'
import s from './index.module.css'

type KnowledgeType = 'personal' | 'department'

type IProps = {
  show: boolean
  onHide: () => void
}
const EmptyDatasetCreationModal = ({ show = false, onHide }: IProps) => {
  const [inputValue, setInputValue] = useState('')
  const [knowledgeType, setKnowledgeType] = useState<KnowledgeType>('personal')
  const [departments, setDepartments] = useState<Department[]>([])
  const [selectedDepartmentId, setSelectedDepartmentId] = useState<string>('')
  const [isLoadingDepts, setIsLoadingDepts] = useState(false)
  const { t } = useTranslation()
  const router = useRouter()
  const invalidDatasetList = useInvalidDatasetList()
  const isLoadingRef = useRef(false)

  const loadDepartments = useCallback(async () => {
    if (knowledgeType !== 'department')
      return
    isLoadingRef.current = true
    setIsLoadingDepts(true)
    try {
      const res = await fetchDepartments()
      setDepartments(res.data)
    }
    catch {
      setDepartments([])
    }
    finally {
      isLoadingRef.current = false
      setIsLoadingDepts(false)
    }
  }, [knowledgeType])

  useEffect(() => {
    if (show && knowledgeType === 'department') {
      loadDepartments()
    }
  }, [show, knowledgeType, loadDepartments])

  const submit = async () => {
    if (!inputValue) {
      toast.error(t('stepOne.modal.nameNotEmpty', { ns: 'datasetCreation' }))
      return
    }
    if (inputValue.length > 40) {
      toast.error(t('stepOne.modal.nameLengthInvalid', { ns: 'datasetCreation' }))
      return
    }
    if (knowledgeType === 'department' && !selectedDepartmentId) {
      toast.error(t('stepOne.modal.departmentRequired', { ns: 'datasetCreation' }))
      return
    }
    try {
      const dataset = await createEmptyDataset({
        name: inputValue,
        is_personal: knowledgeType === 'personal',
        department_id: knowledgeType === 'department' ? selectedDepartmentId : undefined,
      })
      invalidDatasetList()
      trackEvent('create_empty_datasets', {
        name: inputValue,
        dataset_id: dataset.id,
        knowledge_type: knowledgeType,
      })
      onHide()
      router.push(`/datasets/${dataset.id}/documents`)
    }
    catch {
      toast.error(t('stepOne.modal.failed', { ns: 'datasetCreation' }))
    }
  }
  return (
    <Modal isShow={show} onClose={onHide} className={cn(s.modal, '!max-w-[520px]', 'px-8')}>
      <div className={s.modalHeader}>
        <div className={s.title}>{t('stepOne.modal.title', { ns: 'datasetCreation' })}</div>
        <span className={s.close} onClick={onHide} />
      </div>
      <div className={s.tip}>{t('stepOne.modal.tip', { ns: 'datasetCreation' })}</div>
      <div className={s.form}>
        <div className={s.label}>{t('stepOne.modal.input', { ns: 'datasetCreation' })}</div>
        <Input value={inputValue} placeholder={t('stepOne.modal.placeholder', { ns: 'datasetCreation' }) || ''} onChange={e => setInputValue(e.target.value)} />
      </div>
      <div className="mb-4">
        <div className={s.label}>{t('stepOne.modal.knowledgeType', { ns: 'datasetCreation' })}</div>
        <div className="flex gap-4">
          <label className="flex cursor-pointer items-center gap-2">
            <input
              type="radio"
              name="knowledgeType"
              value="personal"
              checked={knowledgeType === 'personal'}
              onChange={() => {
                setKnowledgeType('personal')
                setSelectedDepartmentId('')
              }}
              className="text-components-radio-active h-4 w-4 border-components-radio-border"
            />
            <span className="system-sm-regular text-text-secondary">{t('stepOne.modal.knowledgeTypePersonal', { ns: 'datasetCreation' })}</span>
          </label>
          <label className="flex cursor-pointer items-center gap-2">
            <input
              type="radio"
              name="knowledgeType"
              value="department"
              checked={knowledgeType === 'department'}
              onChange={() => setKnowledgeType('department')}
              className="text-components-radio-active h-4 w-4 border-components-radio-border"
            />
            <span className="system-sm-regular text-text-secondary">{t('stepOne.modal.knowledgeTypeDepartment', { ns: 'datasetCreation' })}</span>
          </label>
        </div>
      </div>
      {knowledgeType === 'department' && (
        <div className="mb-4">
          <div className={s.label}>{t('stepOne.modal.selectDepartment', { ns: 'datasetCreation' })}</div>
          {isLoadingDepts
            ? (
                <div className="border-components-input-border bg-components-input-bg flex h-8 w-full items-center rounded-lg border px-3 py-2 text-sm text-text-secondary">
                  {t('common.loading')}
                </div>
              )
            : (
                <select
                  value={selectedDepartmentId}
                  onChange={e => setSelectedDepartmentId(e.target.value)}
                  className="border-components-input-border bg-components-input-bg focus:border-components-input-border-focus h-8 w-full rounded-lg border px-3 text-sm text-text-primary outline-none focus:ring-1 focus:ring-state-accent-solid"
                >
                  <option value="">{t('stepOne.modal.selectDepartmentPlaceholder', { ns: 'datasetCreation' })}</option>
                  {departments.map(dept => (
                    <option key={dept.id} value={dept.id}>{dept.name}</option>
                  ))}
                </select>
              )}
        </div>
      )}
      <div className="flex flex-row-reverse">
        <Button className="ml-2 w-24" variant="primary" onClick={submit}>{t('stepOne.modal.confirmButton', { ns: 'datasetCreation' })}</Button>
        <Button className="w-24" onClick={onHide}>{t('stepOne.modal.cancelButton', { ns: 'datasetCreation' })}</Button>
      </div>
    </Modal>
  )
}
export default EmptyDatasetCreationModal
