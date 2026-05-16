import * as React from 'react'
import { cn } from '@/lib/utils'

export interface ProgressProps
  extends React.HTMLAttributes<HTMLDivElement> {
  value: number
}

export const Progress = React.forwardRef<HTMLDivElement, ProgressProps>(
  ({ value, className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        'relative h-4 w-full overflow-hidden rounded-full bg-slate-800',
        className
      )}
      {...props}
    >
      <div
        className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 transition-all duration-300"
        style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
      />
    </div>
  )
)
Progress.displayName = 'Progress'
