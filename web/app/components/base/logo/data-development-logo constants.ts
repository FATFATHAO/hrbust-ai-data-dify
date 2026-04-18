export type DataDevelopmentLogoStyle = 'default' | 'monochromeWhite'

export const dataDevelopmentLogoPathMap: Record<DataDevelopmentLogoStyle, string> = {
  default: '/logo/Data-Development-Logo.svg',
  monochromeWhite: '/logo/Data-Delelopment-Text-Logo.svg',
}

export type DataDevelopmentLogoSize = 'large' | 'medium' | 'small'

export const dataDevelopmentLogoSizeMap: Record<DataDevelopmentLogoSize, string> = {
  // 侧边栏折叠时使用
  small: 'w-10 h-5',
  // 侧边栏展开时使用
  medium: 'w-14 h-7',
  // 登录页使用
  large: 'w-20 h-10',
}
