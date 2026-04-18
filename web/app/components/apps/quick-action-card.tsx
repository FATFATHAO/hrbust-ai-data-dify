'use client'

import { cn } from '@langgenius/dify-ui/cn'

type QuickAction = {
  id: string
  label: string
  icon: React.ReactNode
  onClick?: () => void
}

type QuickActionCardProps = {
  actions?: QuickAction[]
}

const defaultActions: QuickAction[] = [
  {
    id: 'create',
    label: '创建应用',
    icon: <span className="i-heroicons-plus h-8 w-8" />,
  },
  {
    id: 'browse',
    label: '浏览模板',
    icon: <span className="i-heroicons-folder-open h-8 w-8" />,
  },
  {
    id: 'dataset',
    label: '知识库',
    icon: <span className="i-heroicons-cog-6-tooth h-8 w-8" />,
  },
  {
    id: 'analytics',
    label: '数据分析',
    icon: <span className="i-heroicons-chart-bar h-8 w-8" />,
  },
]

export default function QuickActionCard({ actions = defaultActions }: QuickActionCardProps) {
  return (
    <section className="mx-auto max-w-5xl px-6">
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        {actions.map(action => (
          <button
            key={action.id}
            type="button"
            onClick={action.onClick}
            className={cn(
              'group relative flex flex-col items-center gap-3 rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl',
              'shadow-[4px_4px_0px_rgba(255,255,255,0.1)]',
              'transition-all duration-200',
              'hover:-translate-y-0.5 hover:scale-105 hover:bg-white/10 hover:shadow-[6px_6px_0px_rgba(255,255,255,0.15)]',
              'hover:border-indigo-500/50',
            )}
          >
            {/* Icon */}
            <div className="flex h-16 w-16 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500/20 to-violet-500/20 text-indigo-400 transition-colors group-hover:from-indigo-500/30 group-hover:to-violet-500/30">
              {action.icon}
            </div>

            {/* Label */}
            <span className="text-sm font-medium text-zinc-300 transition-colors group-hover:text-white">
              {action.label}
            </span>

            {/* Hover glow effect */}
            <div className="pointer-events-none absolute inset-0 rounded-2xl opacity-0 transition-opacity duration-200 group-hover:opacity-100">
              <div className="absolute inset-0 rounded-2xl border border-indigo-500/30 shadow-[0_0_20px_rgba(99,102,241,0.15)]" />
            </div>
          </button>
        ))}
      </div>
    </section>
  )
}
