'use client'

import { cn } from '@langgenius/dify-ui/cn'
import { useShallow } from 'zustand/react/shallow'
import { useSidebarStore } from './sidebar-store'

type MainContentProps = {
  children: React.ReactNode
  className?: string
}

const MainContent: React.FC<MainContentProps> = ({ children, className }) => {
  const { sidebarExpand } = useSidebarStore(useShallow(state => ({
    sidebarExpand: state.sidebarExpand,
  })))

  const expanded = sidebarExpand === 'expand'

  return (
    <main
      className={cn(
        'flex min-h-screen flex-col transition-all duration-300',
        expanded ? 'ml-[240px]' : 'ml-14',
        className,
      )}
    >
      {children}
    </main>
  )
}

export default MainContent
