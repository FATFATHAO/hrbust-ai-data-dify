import type { ReactNode } from 'react'
import { cn } from '@langgenius/dify-ui/cn'

type CardProps = {
  children: ReactNode
  className?: string
}

export function Card({ children, className }: CardProps) {
  return (
    <div
      className={cn(
        'rounded-xl border border-components-card-border bg-components-card-bg shadow-sm',
        className,
      )}
    >
      {children}
    </div>
  )
}

type CardHeaderProps = {
  children: ReactNode
  className?: string
}

export function CardHeader({ children, className }: CardHeaderProps) {
  return (
    <div className={cn('flex flex-col space-y-1.5 p-6', className)}>
      {children}
    </div>
  )
}

type CardTitleProps = {
  children: ReactNode
  className?: string
}

export function CardTitle({ children, className }: CardTitleProps) {
  return (
    <h3 className={cn('text-xl leading-none font-semibold tracking-tight text-text-primary', className)}>
      {children}
    </h3>
  )
}

type CardDescriptionProps = {
  children: ReactNode
  className?: string
}

export function CardDescription({ children, className }: CardDescriptionProps) {
  return (
    <p className={cn('text-sm text-text-secondary', className)}>
      {children}
    </p>
  )
}

type CardContentProps = {
  children: ReactNode
  className?: string
}

export function CardContent({ children, className }: CardContentProps) {
  return (
    <div className={cn('p-6 pt-0', className)}>
      {children}
    </div>
  )
}

type CardFooterProps = {
  children: ReactNode
  className?: string
}

export function CardFooter({ children, className }: CardFooterProps) {
  return (
    <div className={cn('flex items-center p-6 pt-0', className)}>
      {children}
    </div>
  )
}
