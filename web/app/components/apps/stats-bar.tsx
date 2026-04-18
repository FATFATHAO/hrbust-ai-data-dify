'use client'

import { cn } from '@langgenius/dify-ui/cn'

type StatItem = {
  label: string
  value: string | number
  icon: React.ReactNode
}

type StatsBarProps = {
  stats?: StatItem[]
}

const defaultStats: StatItem[] = [
  {
    label: '应用',
    value: '12',
    icon: <span className="i-heroicons-cube h-6 w-6" />,
  },
  {
    label: '用户',
    value: '3.2k',
    icon: <span className="i-heroicons-users h-6 w-6" />,
  },
  {
    label: '上线率',
    value: '98%',
    icon: <span className="i-heroicons-arrow-trending-up h-6 w-6" />,
  },
  {
    label: '部门',
    value: '45',
    icon: <span className="i-heroicons-building-office h-6 w-6" />,
  },
]

export default function StatsBar({ stats = defaultStats }: StatsBarProps) {
  return (
    <section className="mx-auto max-w-5xl px-6">
      <div className="flex items-center justify-around rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl">
        {stats.map(stat => (
          <div
            key={stat.label}
            className={cn(
              'flex flex-col items-center gap-2',
              'transition-all duration-200',
              'hover:scale-105',
            )}
          >
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-500/20 text-indigo-400">
              {stat.icon}
            </div>
            <div className="text-2xl font-bold text-white">{stat.value}</div>
            <div className="text-sm text-zinc-400">{stat.label}</div>
          </div>
        ))}
      </div>
    </section>
  )
}
