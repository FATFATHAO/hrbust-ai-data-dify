'use client'
import type { FC } from 'react'
import type { BatchImportResponse } from '@/types/user'
import * as React from 'react'
import { useState } from 'react'
import { Button } from '@/app/components/base/ui/button'
import { Dialog, DialogCloseButton, DialogContent, DialogTitle } from '@/app/components/base/ui/dialog'
import { toast } from '@/app/components/base/ui/toast'
import { useBatchImportUsers } from '@/service/use-account'
import DownloadTemplate from './download-template'
import FileUploader from './file-uploader'

export type IBatchUserImportModalProps = {
  isShow: boolean
  onCancel: () => void
  onSuccess: () => void
}

const BatchUserImportModal: FC<IBatchUserImportModalProps> = ({
  isShow,
  onCancel,
  onSuccess,
}) => {
  const [currentFile, setCurrentFile] = useState<File | undefined>(undefined)
  const batchImportMutation = useBatchImportUsers()

  const handleFile = (file?: File) => setCurrentFile(file)

  const showResult = (result: BatchImportResponse) => {
    const { success_count, fail_count, created_users, errors } = result

    // 如果有自动生成的密码，显示给用户
    const usersWithGeneratedPassword = created_users.filter(u => u.is_password_generated)

    const title = `导入完成：成功 ${success_count} 个，失败 ${fail_count} 个`
    let description = ''
    if (usersWithGeneratedPassword.length > 0) {
      description += '以下用户的密码已自动生成，请妥善保管：\n'
      usersWithGeneratedPassword.forEach((user) => {
        description += `${user.name} (${user.email}): ${user.generated_password}\n`
      })
    }

    if (fail_count > 0 && errors.length > 0) {
      description += '\n失败详情：\n'
      errors.forEach((err) => {
        description += `第 ${err.row} 行 (${err.email}): ${err.message}\n`
      })
    }

    if (description)
      toast.success(title, { description })
    else
      toast.success(title)
    onSuccess()
    onCancel()
  }

  const handleImport = async () => {
    if (!currentFile)
      return

    try {
      const result = await batchImportMutation.mutateAsync(currentFile)
      showResult(result)
    }
    catch (e) {
      const error = e as Error
      toast.error(error.message || '批量导入失败')
    }
  }

  return (
    <Dialog open={isShow} onOpenChange={open => !open && onCancel()}>
      <DialogContent className="max-w-[640px]! rounded-xl! px-8 py-6">
        <DialogTitle className="system-xl-medium text-text-primary">批量导入用户</DialogTitle>
        <DialogCloseButton onClick={onCancel} />
        <FileUploader
          file={currentFile}
          updateFile={handleFile}
        />
        <DownloadTemplate />
        <div className="mt-[28px] flex justify-end pt-6">
          <Button className="mr-2 system-sm-medium text-text-tertiary" onClick={onCancel}>
            取消
          </Button>
          <Button
            variant="primary"
            onClick={handleImport}
            disabled={!currentFile}
            loading={batchImportMutation.isPending}
          >
            开始导入
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
export default React.memo(BatchUserImportModal)
