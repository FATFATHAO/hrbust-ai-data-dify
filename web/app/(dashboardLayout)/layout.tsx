import type { ReactNode } from 'react'
import * as React from 'react'
import { AppInitializer } from '@/app/components/app-initializer'
import InSiteMessageNotification from '@/app/components/app/in-site-message/notification'
import AmplitudeProvider from '@/app/components/base/amplitude'
import GA, { GaType } from '@/app/components/base/ga'
import Zendesk from '@/app/components/base/zendesk'
import MainContent from '@/app/components/layout/main-content'
import Sidebar from '@/app/components/layout/sidebar'
import ReadmePanel from '@/app/components/plugins/readme-panel'
import { AppContextProvider } from '@/context/app-context-provider'
import { EventEmitterContextProvider } from '@/context/event-emitter-provider'
import { ModalContextProvider } from '@/context/modal-context-provider'
import { ProviderContextProvider } from '@/context/provider-context-provider'
import dynamic from '@/next/dynamic'
import PartnerStack from '../components/billing/partner-stack'
import Splash from '../components/splash'
import RoleRouteGuard from './role-route-guard'

const GotoAnything = dynamic(() => import('@/app/components/goto-anything'), {
  ssr: false,
})

// [HRBUST MODIFIED] 数据总览页面使用独立布局（带侧边栏）
const DashboardLayout = ({ children }: { children: ReactNode }) => {
  return (
    <>
      <GA gaType={GaType.admin} />
      <AmplitudeProvider />
      <AppInitializer>
        <AppContextProvider>
          <EventEmitterContextProvider>
            <ProviderContextProvider>
              <ModalContextProvider>
                {/* Custom Sidebar */}
                <Sidebar />
                <MainContent>
                  <RoleRouteGuard>
                    {children}
                  </RoleRouteGuard>
                </MainContent>
                <InSiteMessageNotification />
                <PartnerStack />
                <ReadmePanel />
                <GotoAnything />
                <Splash />
              </ModalContextProvider>
            </ProviderContextProvider>
          </EventEmitterContextProvider>
        </AppContextProvider>
        <Zendesk />
      </AppInitializer>
    </>
  )
}

export default DashboardLayout
