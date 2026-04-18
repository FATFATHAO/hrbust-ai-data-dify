'use client'

import type { FC } from 'react'
import type { DataDevelopmentLogoSize, DataDevelopmentLogoStyle } from './data-development-logo constants'
import { cn } from '@langgenius/dify-ui/cn'
import useTheme from '@/hooks/use-theme'
import { basePath } from '@/utils/var'
import {
  dataDevelopmentLogoPathMap,

  dataDevelopmentLogoSizeMap,

} from './data-development-logo constants'

type DataDevelopmentLogoProps = {
  style?: DataDevelopmentLogoStyle
  size?: DataDevelopmentLogoSize
  className?: string
}

const DataDevelopmentLogo: FC<DataDevelopmentLogoProps> = ({
  style = 'default',
  size = 'medium',
  className,
}) => {
  const { theme } = useTheme()
  const themedStyle = (theme === 'dark' && style === 'default') ? 'monochromeWhite' : style

  return (
    <img
      src={`${basePath}${dataDevelopmentLogoPathMap[themedStyle]}`}
      className={cn('block object-contain', dataDevelopmentLogoSizeMap[size], className)}
      alt="Data Development Logo"
    />
  )
}

export default DataDevelopmentLogo
