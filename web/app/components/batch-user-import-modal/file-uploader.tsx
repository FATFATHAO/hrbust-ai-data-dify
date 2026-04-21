'use client'
import type { FC } from 'react'
import { cn } from '@langgenius/dify-ui/cn'
import * as React from 'react'
import { useCallback, useEffect, useRef, useState } from 'react'
import { Button } from '@/app/components/base/ui/button'
import { toast } from '@/app/components/base/ui/toast'

export type Props = {
  file: File | undefined
  updateFile: (file?: File) => void
}

const FileUploader: FC<Props> = ({
  file,
  updateFile,
}) => {
  const [dragging, setDragging] = useState(false)
  const dropRef = useRef<HTMLDivElement>(null)
  const dragRef = useRef<HTMLDivElement>(null)
  const fileUploaderRef = useRef<HTMLInputElement>(null)

  const handleDragEnter = useCallback((e: DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.target !== dragRef.current)
      setDragging(true)
  }, [])

  const handleDragOver = useCallback((e: DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
  }, [])

  const handleDragLeave = useCallback((e: DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.target === dragRef.current)
      setDragging(false)
  }, [])

  const handleDrop = useCallback((e: DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragging(false)
    if (!e.dataTransfer)
      return
    const files = Array.from(e.dataTransfer.files)
    if (files.length > 1) {
      toast.error('一次只能上传一个文件')
      return
    }
    const uploadedFile = files[0]
    if (!uploadedFile) {
      toast.error('文件无效')
      return
    }
    const validExtensions = ['.csv', '.xlsx', '.xls']
    const fileExtension = uploadedFile.name.substring(uploadedFile.name.lastIndexOf('.')).toLowerCase()
    if (!validExtensions.includes(fileExtension)) {
      toast.error('只支持 CSV 或 Excel 文件')
      return
    }
    updateFile(uploadedFile)
  }, [updateFile])

  const selectHandle = () => {
    if (fileUploaderRef.current)
      fileUploaderRef.current.click()
  }
  const removeFile = () => {
    if (fileUploaderRef.current)
      fileUploaderRef.current.value = ''
    updateFile()
  }
  const fileChangeHandle = (e: React.ChangeEvent<HTMLInputElement>) => {
    const currentFile = e.target.files?.[0]
    if (currentFile) {
      const validExtensions = ['.csv', '.xlsx', '.xls']
      const fileExtension = currentFile.name.substring(currentFile.name.lastIndexOf('.')).toLowerCase()
      if (!validExtensions.includes(fileExtension)) {
        toast.error('只支持 CSV 或 Excel 文件')
        return
      }
      updateFile(currentFile)
    }
  }

  useEffect(() => {
    const drop = dropRef.current
    drop?.addEventListener('dragenter', handleDragEnter)
    drop?.addEventListener('dragover', handleDragOver)
    drop?.addEventListener('dragleave', handleDragLeave)
    drop?.addEventListener('drop', handleDrop)
    return () => {
      drop?.removeEventListener('dragenter', handleDragEnter)
      drop?.removeEventListener('dragover', handleDragOver)
      drop?.removeEventListener('dragleave', handleDragLeave)
      drop?.removeEventListener('drop', handleDrop)
    }
  }, [handleDragEnter, handleDragOver, handleDragLeave, handleDrop])

  const getFileExtension = (filename: string) => {
    const lastDot = filename.lastIndexOf('.')
    return lastDot > 0 ? filename.substring(lastDot).toLowerCase() : ''
  }

  return (
    <div className="mt-6">
      <input
        ref={fileUploaderRef}
        style={{ display: 'none' }}
        type="file"
        id="fileUploader"
        accept=".csv,.xlsx,.xls"
        onChange={fileChangeHandle}
      />
      <div ref={dropRef}>
        {!file && (
          <div className={cn('flex h-20 items-center rounded-xl border border-dashed border-components-dropzone-border bg-components-dropzone-bg system-sm-regular', dragging && 'border border-components-dropzone-border-accent bg-components-dropzone-bg-accent')}>
            <div className="flex w-full items-center justify-center space-x-2">
              <span className="i-custom-public-files-csv shrink-0" />
              <div className="text-text-tertiary">
                拖拽 CSV 或 Excel 文件到此处，或
                <span className="cursor-pointer text-text-accent" onClick={selectHandle}>点击选择文件</span>
              </div>
            </div>
            {dragging && <div ref={dragRef} className="absolute top-0 left-0 h-full w-full" />}
          </div>
        )}
        {file && (
          <div className={cn('group flex h-20 items-center rounded-xl border border-components-panel-border bg-components-panel-bg px-6 text-sm font-normal', 'hover:border-components-panel-bg-blur hover:bg-components-panel-bg-blur')}>
            <span className={cn('shrink-0', getFileExtension(file.name) === '.csv' ? 'i-custom-public-files-csv' : 'i-custom-public-files-xlsx')} />
            <div className="ml-2 flex w-0 grow">
              <span className="max-w-[calc(100%-30px)] overflow-hidden text-ellipsis whitespace-nowrap text-text-primary">{file.name.replace(/\.[^.]+$/, '')}</span>
              <span className="shrink-0 text-text-tertiary">{getFileExtension(file.name)}</span>
            </div>
            <div className="hidden items-center group-hover:flex">
              <Button variant="secondary" onClick={selectHandle}>更换文件</Button>
              <div className="mx-2 h-4 w-px bg-divider-regular" />
              <div className="cursor-pointer p-2" onClick={removeFile} data-testid="remove-file-button">
                <span className="i-ri-delete-bin-line h-4 w-4 text-text-tertiary" />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default React.memo(FileUploader)
