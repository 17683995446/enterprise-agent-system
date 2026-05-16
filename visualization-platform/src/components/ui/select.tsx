import * as React from 'react'
import { ChevronDown } from 'lucide-react'
import { cn } from '@/lib/utils'

export interface SelectProps {
  value?: string
  onValueChange?: (value: string) => void
  children: React.ReactNode
  placeholder?: string
}

export const Select = ({ value, onValueChange, children, placeholder }: SelectProps) => {
  const [open, setOpen] = React.useState(false)
  const [selectedValue, setSelectedValue] = React.useState(value)
  
  const handleSelect = (val: string) => {
    setSelectedValue(val)
    onValueChange?.(val)
    setOpen(false)
  }
  
  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="flex h-10 w-full items-center justify-between rounded-md border border-slate-700 bg-slate-800/50 px-3 py-2 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-cyan-500"
      >
        <span>{selectedValue || placeholder}</span>
        <ChevronDown className="w-4 h-4 text-slate-400" />
      </button>
      
      {open && (
        <>
          <div 
            className="fixed inset-0 z-40" 
            onClick={() => setOpen(false)} 
          />
          <div className="absolute top-full left-0 right-0 z-50 mt-1 rounded-md border border-slate-700 bg-slate-900 shadow-lg">
            {React.Children.map(children, (child) => {
              if (React.isValidElement(child)) {
                return React.cloneElement(child as any, { 
                  onSelect: handleSelect, 
                  selectedValue 
                })
              }
              return child
            })}
          </div>
        </>
      )}
    </div>
  )
}

export const SelectTrigger = ({ children, className, ...props }: any) => (
  <div className={cn('relative', className)} {...props}>
    {children}
  </div>
)

export const SelectValue = ({ placeholder }: any) => (
  <span>{placeholder}</span>
)

export const SelectContent = ({ children, ...props }: any) => (
  <div {...props}>{children}</div>
)

export const SelectItem = ({ value, children, onSelect, selectedValue, ...props }: any) => (
  <button
    type="button"
    onClick={() => onSelect?.(value)}
    className={cn(
      'flex w-full items-center justify-between px-3 py-2 text-sm text-left',
      selectedValue === value ? 'bg-cyan-500/10 text-cyan-400' : 'text-slate-300 hover:bg-slate-800'
    )}
    {...props}
  >
    {children}
  </button>
)
