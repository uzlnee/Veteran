export function Button({ children, onClick, variant = 'default', size = 'md' }) {
  const styles = {
    default: 'bg-blue-600 text-white hover:bg-blue-700',
    outline: 'border border-gray-300 text-gray-800 hover:bg-gray-100',
  }

  const sizes = {
    sm: 'text-sm px-3 py-1.5',
    md: 'text-base px-4 py-2',
  }

  return (
    <button
      onClick={onClick}
      className={`${styles[variant]} ${sizes[size]} rounded-lg transition`}
    >
      {children}
    </button>
  )
}
