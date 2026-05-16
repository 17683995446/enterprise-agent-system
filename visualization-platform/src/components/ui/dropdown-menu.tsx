import * as React from 'react'
import { MoreHorizontal } from 'lucide-react'
import { cn } from '@/lib/utils'

export interface DropdownMenuProps {
  children: React.ReactNode
}

export const DropdownMenu = ({ children }: DropdownMenuProps) => (
  <div className="relative">{children}</div>
)

export const DropdownMenuTrigger = ({ children, ...props }: any) => (
  <div {...props}>{children}</div>
)

export const DropdownMenuContent = ({ children, align = 'end', sideOffset = 4, ...props }: any) => {
  const [open, setOpen] = React.useState(false)
  
  return (
    <>
      <div onClick={() => setOpen(!open)}>
        {React.Children.map(children, (child) => {
          if (React.isValidElement(child) && (child.type as any)?.displayName === 'DropdownMenuTrigger') {
            return child
          }
          return null
        })}
      </div>
      {open && (
        <>
          <div 
            className="fixed inset-0 z-40" 
            onClick={() => setOpen(false)} 
          />
          <div 
            className={cn(
              'absolute z-50 mt-2 w-56 rounded-md border border-slate-700 bg-slate-900 shadow-lg',
              align === 'end' ? 'right-0' : 'left-0'
            )}
            style={{ marginTop: sideOffset }}
            {...props}
          >
            <div className="py-1">
              {React.Children.map(children, (child) => {
                if (React.isValidElement(child) && (child.type as any)?.displayName !== 'DropdownMenuTrigger') {
                  return React.cloneElement(child as any, { onSelect: () => setOpen(false) })
                }
                return null
              })}
            </div>
          </div>
        </>
      )}
    </>
  )
}

export const DropdownMenuItem = ({ children, onClick, onSelect, ...props }: any) => (
  <button
    type="button"
    onClick={(e) => {
      onClick?.(e)
      onSelect?.()
    }}
    className="flex w-full items-center gap-2 px-3 py-2 text-sm text-slate-300 hover:bg-slate-800 text-left"
    {...props}
  >
    {children}
  </button>
)
