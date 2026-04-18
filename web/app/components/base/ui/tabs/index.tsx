'use client'

import type { ReactNode } from 'react'
import { Tabs as BaseTabs } from '@base-ui/react/tabs'
import { cn } from '@langgenius/dify-ui/cn'

export const Tabs = BaseTabs.Root
export const TabsList = BaseTabs.List
export const TabsTab = BaseTabs.Tab
export const TabsPanel = BaseTabs.Panel

type TabsTriggerProps = {
  value: string
  children: ReactNode
  className?: string
  disabled?: boolean
}

export function TabsTrigger({ value, children, className, disabled, ...props }: TabsTriggerProps) {
  return (
    <BaseTabs.Tab
      value={value}
      disabled={disabled}
      className={cn(
        'cursor-pointer rounded-lg px-4 py-2 text-sm font-medium transition-colors',
        'text-text-secondary hover:text-text-primary',
        'data-[selected]:bg-components-button-secondary-bg data-[selected]:text-text-primary',
        'data-[disabled]:cursor-not-allowed data-[disabled]:opacity-50',
        className,
      )}
      {...props}
    >
      {children}
    </BaseTabs.Tab>
  )
}

type TabsContentProps = {
  value: string
  children: ReactNode
  className?: string
}

export function TabsContent({ value, children, className }: TabsContentProps) {
  return (
    <BaseTabs.Panel
      value={value}
      className={cn('mt-4 outline-none', className)}
    >
      {children}
    </BaseTabs.Panel>
  )
}
