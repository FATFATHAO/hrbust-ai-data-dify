'use client'

import { cn } from '@langgenius/dify-ui/cn'

type HeroSectionProps = {
  onCreateApp?: () => void
}

export default function HeroSection({ onCreateApp }: HeroSectionProps) {
  return (
    <section className="relative w-full overflow-hidden">
      {/* Background gradient */}
      <div className="gradient-hero animate-gradient absolute inset-0" />

      {/* Mesh overlay */}
      <div className="gradient-mesh absolute inset-0" />

      {/* Content */}
      <div className="relative z-10 mx-auto max-w-5xl px-6 py-16">
        <div className="mx-auto max-w-3xl rounded-2xl border border-white/10 bg-white/5 p-8 text-center backdrop-blur-xl transition-all duration-200 hover:scale-[1.02] hover:border-indigo-500/50 hover:bg-white/10 hover:shadow-2xl">
          {/* Title */}
          <h1 className="mb-4 text-4xl font-bold tracking-tight text-white md:text-5xl">
            <span className="bg-gradient-to-r from-indigo-400 via-violet-400 to-purple-400 bg-clip-text text-transparent">
              构建 AI 应用的未来
            </span>
          </h1>

          {/* Subtitle */}
          <p className="mb-8 text-lg text-zinc-400">
            创建智能对话应用、工作流和 Agent，将您的想法变为现实
          </p>

          {/* Action buttons */}
          <div className="flex flex-wrap items-center justify-center gap-4">
            <button
              type="button"
              onClick={onCreateApp}
              className={cn(
                'inline-flex items-center gap-2 rounded-xl px-6 py-3',
                'bg-indigo-600 text-white',
                'transition-all duration-200',
                'hover:scale-105 hover:bg-indigo-500',
                'active:scale-95',
                'shadow-[4px_4px_0px_rgba(255,255,255,0.1)]',
              )}
            >
              <span className="i-heroicons-plus h-5 w-5" />
              <span className="font-medium">
                创建应用
              </span>
            </button>

            <button
              type="button"
              className={cn(
                'inline-flex items-center gap-2 rounded-xl px-6 py-3',
                'border border-white/20 bg-white/5 text-white backdrop-blur-xl',
                'transition-all duration-200',
                'hover:scale-105 hover:bg-white/10',
                'active:scale-95',
              )}
            >
              <span className="i-heroicons-sparkles h-5 w-5" />
              <span className="font-medium">
                浏览模板
              </span>
            </button>

            <button
              type="button"
              className={cn(
                'inline-flex items-center gap-2 rounded-xl px-6 py-3',
                'border border-white/20 bg-white/5 text-white backdrop-blur-xl',
                'transition-all duration-200',
                'hover:scale-105 hover:bg-white/10',
                'active:scale-95',
              )}
            >
              <span className="i-heroicons-document-text h-5 w-5" />
              <span className="font-medium">
                查看文档
              </span>
            </button>
          </div>
        </div>
      </div>
    </section>
  )
}
