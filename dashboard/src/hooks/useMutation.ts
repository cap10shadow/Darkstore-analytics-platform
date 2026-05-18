import { useState, useCallback } from 'react'

interface UseMutationResult<T, A extends unknown[]> {
  data: T | null
  loading: boolean
  error: string | null
  execute: (...args: A) => Promise<T | undefined>
}

export function useMutation<T, A extends unknown[]>(
  mutator: (...args: A) => Promise<T>
): UseMutationResult<T, A> {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const execute = useCallback(async (...args: A) => {
    setLoading(true)
    setError(null)
    try {
      const result = await mutator(...args)
      setData(result)
      return result
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }, [mutator])

  return { data, loading, error, execute }
}
