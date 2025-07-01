export function ScrollArea({ children, className }) {
  return <div className={`overflow-y-auto ${className}`}>{children}</div>
}
