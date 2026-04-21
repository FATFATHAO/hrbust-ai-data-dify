import type { AccountRole } from '@/types/permission'
import { useQuery } from '@tanstack/react-query'
import Cookies from 'js-cookie'
import { CSRF_COOKIE_NAME, CSRF_HEADER_NAME } from '@/config'

export type AccountRoleResponse = {
  account_id: string
  role: AccountRole
}

/**
 * Fetch account role from native Flask API
 * Cookie is automatically sent to same-origin API route
 */
const fetchAccountRole = async (): Promise<AccountRoleResponse> => {
  // Use native Flask API endpoint - same-origin request, cookie sent automatically
  const url = '/console/api/account/role'

  // Get CSRF token from cookie and include in header
  const csrfToken = Cookies.get(CSRF_COOKIE_NAME()) || ''

  const response = await fetch(url, {
    method: 'GET',
    credentials: 'include', // Include cookies for same-origin requests
    headers: {
      [CSRF_HEADER_NAME]: csrfToken,
    },
  })

  if (!response.ok) {
    throw new Error(`Failed to fetch account role: ${response.status}`)
  }

  return response.json()
}

/**
 * Hook to get current user's account role
 * @param userId - Current user's ID. When it changes (user switches), query automatically refetches
 */
export const useAccountRole = (userId?: string) => {
  return useQuery<AccountRoleResponse>({
    // Include userId in queryKey so query refetches when user changes
    queryKey: ['account-role', userId],
    queryFn: fetchAccountRole,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    retry: false,
  })
}
