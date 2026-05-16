import * as React from 'react'
import { X } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from './button'

export interface DialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  children: React.ReactNode
}

export const Dialog = ({ open, onOpenChange, children }: DialogProps) => {
  React.useEffect(() => {
    if (open) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => {
      document.body.style.overflow = ''
    }
  }, [open])
  
  if (!open) return null
  
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div 
        className="fixed inset-0 bg-black/50 backdrop-blur-sm"
        onClick={() => onOpenChange(false)}
      />
      {children}
    </div>
  )
}

export const DialogTrigger = ({ asChild, children, ...props }: any) => {
  if (asChild && React.isValidElement(children)) {
    return React.cloneElement(children, props)
  }
  return <Button {...props}>{children}</Button>
}

export const DialogContent = ({ className, children, ...props }: any) => (
  <div 
    className={cn(
      'relative z-50 w-full max-w-lg bg-slate-900 border border-slate-700 rounded-xl shadow-2xl p-6',
      className
    )}
    {...props}
  >
    {children}
  </div>
)

export const DialogHeader = ({ className, ...props }: any) => (
  <div className={cn('flex flex-col space-y-1.5 mb-4', className)} {...props} />
)

export const DialogTitle = ({ className, ...props }: any) => (
  <h2 className={cn('text-lg font-semibold text-slate-200', className)} {...props} />
)
