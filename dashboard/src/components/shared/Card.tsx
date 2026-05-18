import type { ReactNode } from 'react'

interface CardProps {
  children: ReactNode
  className?: string
}

export default function Card({ children, className = '' }: CardProps) {
  return (
    <div className={`bg-navy-800 border border-navy-700 rounded-xl p-5 ${className}`}>
      {children}
    </div>
  )
}
