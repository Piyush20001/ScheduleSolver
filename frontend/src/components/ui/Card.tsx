interface CardProps {
  children: React.ReactNode
  className?: string
  padding?: 'none' | 'sm' | 'md' | 'lg'
}

const paddingMap = {
  none: '',
  sm: 'p-3',
  md: 'p-5',
  lg: 'p-8',
}

export function Card({ children, className = '', padding = 'md' }: CardProps) {
  return (
    <div
      className={`bg-slate-800/50 border border-slate-700/50 rounded-xl ${paddingMap[padding]} ${className}`}
    >
      {children}
    </div>
  )
}
