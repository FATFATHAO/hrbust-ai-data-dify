'use client'

import { useTranslation } from 'react-i18next'

type StatCardProps = {
  title: string
  value: string
  icon: string
}

const StatCard = ({ title, value, icon }: StatCardProps) => {
  return (
    <div className="rounded-xl border border-components-card-border bg-components-card-bg p-6 shadow-sm">
      <div className="flex items-center gap-4">
        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500/20 to-violet-500/20">
          <span className={`h-6 w-6 ${icon} text-indigo-400`} />
        </div>
        <div>
          <p className="text-sm text-text-tertiary">{title}</p>
          <p className="text-2xl font-bold text-text-primary">{value}</p>
        </div>
      </div>
    </div>
  )
}

const DashboardPage = () => {
  const { t } = useTranslation()

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold text-text-primary">
        {t('dashboard.title', { defaultValue: '数据总览' })}
      </h1>
      <p className="mt-2 text-text-secondary">
        {t('dashboard.description', { defaultValue: '在此查看您的应用数据统计和分析' })}
      </p>

      {/* Placeholder content - to be migrated from the original data components */}
      <div className="mt-8 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title={t('dashboard.apps', { defaultValue: '应用数' })}
          value="12"
          icon="i-heroicons-cube"
        />
        <StatCard
          title={t('dashboard.users', { defaultValue: '用户数' })}
          value="3.2k"
          icon="i-heroicons-users"
        />
        <StatCard
          title={t('dashboard.activeRate', { defaultValue: '活跃率' })}
          value="98%"
          icon="i-heroicons-arrow-trending-up"
        />
        <StatCard
          title={t('dashboard.departments', { defaultValue: '部门数' })}
          value="45"
          icon="i-heroicons-building-office"
        />
      </div>
    </div>
  )
}

export default DashboardPage
