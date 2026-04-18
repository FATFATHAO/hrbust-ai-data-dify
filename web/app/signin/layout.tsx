// [HRBUST MODIFIED] Layout for unified auth page - renders children directly
'use client'

import { useGlobalPublicStore } from '@/context/global-public-context'
import useDocumentTitle from '@/hooks/use-document-title'

export default function SignInLayout({ children }: { children: React.ReactNode }) {
  useGlobalPublicStore(state => state.systemFeatures)
  useDocumentTitle('')

  return (
    <>
      {children}
    </>
  )
}
