'use client'

import type * as React from 'react'
import { cn } from '@langgenius/dify-ui/cn'
import { useHover } from 'ahooks'
import { useCallback, useEffect, useMemo, useRef } from 'react'
import { useTranslation } from 'react-i18next'
import { useShallow } from 'zustand/react/shallow'
import DataDevelopmentLogo from '@/app/components/base/logo/data-development-logo'
import AccountDropdown from '@/app/components/header/account-dropdown'
import Link from '@/next/link'
import { ROLE_NAV_CONFIG } from '@/types/permission'
import { usePermission } from '../permission/use-permission'
import { useSidebarStore } from './sidebar-store'

type NavItem = {
  label: string
  icon: string
  href: string
  activeIcon?: string
}

const NAV_ITEMS: NavItem[] = [
  // {
  //   label: '数据总览',
  //   icon: 'i-heroicons-chart-bar',
  //   activeIcon: 'i-heroicons-chart-bar-solid',
  //   href: '/dashboard',
  // },
  {
    label: '工作室',
    icon: 'i-heroicons-sparkles',
    activeIcon: 'i-heroicons-sparkles',
    href: '/apps',
  },
  {
    label: '知识库',
    icon: 'i-heroicons-book-open',
    activeIcon: 'i-heroicons-book-open',
    href: '/datasets',
  },
  {
    label: '工具',
    icon: 'i-heroicons-wrench-screwdriver',
    activeIcon: 'i-heroicons-wrench-screwdriver',
    href: '/tools',
  },
  {
    label: '插件',
    icon: 'i-heroicons-puzzle-piece',
    activeIcon: 'i-heroicons-puzzle-piece',
    href: '/plugins',
  },
]

type SidebarProps = {
  className?: string
}

const Sidebar: React.FC<SidebarProps> = ({ className }) => {
  const sidebarRef = useRef<HTMLDivElement>(null)
  const isHovering = useHover(sidebarRef)
  const { sidebarExpand, setSidebarExpand } = useSidebarStore(useShallow(state => ({
    sidebarExpand: state.sidebarExpand,
    setSidebarExpand: state.setSidebarExpand,
  })))
  const { accountRole } = usePermission()

  const expanded = sidebarExpand === 'expand'

  // 根据用户角色过滤导航项
  const visibleNavItems = useMemo(() => {
    const allowedPaths = ROLE_NAV_CONFIG[accountRole] || ROLE_NAV_CONFIG.user
    return NAV_ITEMS.filter(item => allowedPaths.some(path => item.href.startsWith(path)))
  }, [accountRole])

  // Load saved state
  useEffect(() => {
    const saved = localStorage.getItem('global-sidebar-expand')
    if (saved === 'expand' || saved === 'collapse') {
      setSidebarExpand(saved)
    }
  }, [setSidebarExpand])

  // Save state on change
  useEffect(() => {
    localStorage.setItem('global-sidebar-expand', sidebarExpand)
  }, [sidebarExpand])

  const handleToggle = useCallback(() => {
    setSidebarExpand(sidebarExpand === 'expand' ? 'collapse' : 'expand')
  }, [sidebarExpand, setSidebarExpand])

  // Keyboard shortcut: Ctrl+B
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.key === 'b') {
        e.preventDefault()
        handleToggle()
      }
    }
    window.addEventListener('keydown', handleKeyPress)
    return () => window.removeEventListener('keydown', handleKeyPress)
  }, [handleToggle])

  return (
    <div
      ref={sidebarRef}
      className={cn(
        'fixed top-0 left-0 z-40 flex h-screen shrink-0 flex-col border-r border-divider-burn bg-background-default-subtle transition-all duration-300',
        expanded ? 'w-[240px]' : 'w-14',
        className,
      )}
    >
      {/* Logo */}
      <div className={cn('flex h-[56px] shrink-0 items-center border-b border-divider-burn', expanded ? 'px-4' : 'justify-center px-2')}>
        {expanded
          ? (
              <div className="flex items-center gap-2">
                <DataDevelopmentLogo size="medium" />
              </div>
            )
          : (
              <DataDevelopmentLogo size="small" />
            )}
      </div>

      {/* Nav Items */}
      <nav className={cn('flex flex-1 flex-col gap-y-1 py-3', expanded ? 'px-3' : 'px-2')}>
        {visibleNavItems.map(item => (
          <NavItem
            key={item.href}
            item={item}
            expanded={expanded}
          />
        ))}
      </nav>

      {/* Bottom Section */}
      <div className="border-t border-divider-burn">
        {/* User Account Dropdown */}
        <div className={cn('flex items-center', expanded ? 'px-3' : 'justify-center px-2')}>
          <AccountDropdown />
        </div>

        {/* Toggle Button - Show on hover when collapsed */}
        {!expanded && isHovering && (
          <button
            type="button"
            onClick={handleToggle}
            className="absolute top-[68px] -right-3 z-50 flex h-6 w-6 items-center justify-center rounded-full border border-divider-burn bg-background-default shadow-sm hover:bg-state-base-hover"
          >
            <span className="i-heroicons-chevron-right h-3 w-3 text-text-tertiary" />
          </button>
        )}

        {expanded && (
          <button
            type="button"
            onClick={handleToggle}
            className="m-3 flex items-center gap-2 rounded-lg px-3 py-2 text-text-tertiary hover:bg-state-base-hover hover:text-text-secondary"
          >
            <span className="i-heroicons-chevron-left h-4 w-4" />
            <span className="text-sm">收起</span>
          </button>
        )}
      </div>
    </div>
  )
}

type NavItemProps = {
  item: NavItem
  expanded: boolean
}

const NavItem: React.FC<NavItemProps> = ({ item, expanded }) => {
  const { t } = useTranslation()
  // For now, we'll use a simple implementation
  // The active state will be determined by the current pathname

  return (
    <Link
      href={item.href}
      className={cn(
        'group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-200',
        'text-text-tertiary hover:bg-state-base-hover hover:text-text-secondary',
        // Active state would need pathname check - simplified for now
      )}
      title={!expanded ? t(item.label) : undefined}
    >
      <span className={cn('h-5 w-5 shrink-0', item.icon)} />
      {expanded && <span className="truncate">{t(item.label)}</span>}
    </Link>
  )
}

export default Sidebar
