import type { ReactNode } from 'react'
import { cn } from '@langgenius/dify-ui/cn'

type LabelProps = {
  children: ReactNode
  htmlFor?: string
  className?: string
}

export function Label({ children, htmlFor, className }: LabelProps) {
  return (
    <label
      htmlFor={htmlFor}
      className={cn(
        'system-md-semibold text-text-secondary',
        className,
      )}
    >
      {children}
    </label>
  )
}
