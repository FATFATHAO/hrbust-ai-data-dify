'use client'

import type { ChangeEvent, KeyboardEvent } from 'react'
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import Input from '@/app/components/base/input'
import DataDevelopmentLogo from '@/app/components/base/logo/data-development-logo'
import { Button } from '@/app/components/base/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/app/components/base/ui/card'
import { Label } from '@/app/components/base/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/app/components/base/ui/tabs'
import { toast } from '@/app/components/base/ui/toast'
import { emailRegex } from '@/config'
import { useGlobalPublicStore } from '@/context/global-public-context'
import { useLocale } from '@/context/i18n'
import Link from '@/next/link'
import { useRouter, useSearchParams } from '@/next/navigation'
import { login } from '@/service/common'
import { useSendMail } from '@/service/use-common'
import { setWebAppAccessToken } from '@/service/webapp-auth'
import { encryptPassword } from '@/utils/encryption'
import Split from './split'
import { resolvePostLoginRedirect } from './utils/post-login-redirect'

// Login Form Component
const LoginForm = () => {
  const { t } = useTranslation()
  const locale = useLocale()
  const router = useRouter()
  const searchParams = useSearchParams()
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const identifierFromLink = decodeURIComponent(searchParams.get('email') || '')
  const [identifier, setIdentifier] = useState(identifierFromLink)
  const [password, setPassword] = useState('')

  // Username format: 3-30 chars, alphanumeric and underscore
  const usernameRegex = /^\w{3,30}$/

  const handleLogin = async () => {
    if (!identifier.trim()) {
      toast.error('请输入用户名或邮箱')
      return
    }

    // Check if it's an email format or username format
    const isEmailFormat = emailRegex.test(identifier)
    if (!isEmailFormat && !usernameRegex.test(identifier)) {
      toast.error('用户名或邮箱格式不正确')
      return
    }

    if (!password?.trim()) {
      toast.error(t('error.passwordEmpty', { ns: 'login' }))
      return
    }

    try {
      setIsLoading(true)
      const res = await login({
        url: '/login',
        body: {
          email: identifier,
          password: encryptPassword(password),
          language: locale,
          remember_me: true,
        },
      })
      if (res.result === 'success') {
        if (res?.data?.access_token) {
          setWebAppAccessToken(res.data.access_token)
        }
        const redirectUrl = resolvePostLoginRedirect()
        router.replace(redirectUrl || '/apps')
      }
      else {
        toast.error(res.data)
      }
    }
    catch (error: unknown) {
      if ((error as { code?: string })?.code === 'authentication_failed') {
        toast.error(t('error.invalidEmailOrPassword', { ns: 'login' }))
      }
    }
    finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <div>
        <Label htmlFor="login-identifier">用户名 / 邮箱</Label>
        <Input
          id="login-identifier"
          type="text"
          value={identifier}
          onChange={(e: ChangeEvent<HTMLInputElement>) => setIdentifier(e.target.value)}
          placeholder="请输入用户名或邮箱"
          className="mt-1"
          autoComplete="username"
        />
      </div>

      <div>
        <div className="flex items-center justify-between">
          <Label htmlFor="login-password">{t('password', { ns: 'login' })}</Label>
          <Link
            href="/reset-password"
            className="system-xs-regular text-components-button-secondary-accent-text hover:underline"
          >
            {t('forget', { ns: 'login' })}
          </Link>
        </div>
        <div className="relative mt-1">
          <Input
            id="login-password"
            type={showPassword ? 'text' : 'password'}
            value={password}
            onChange={(e: ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)}
            onKeyDown={(e: KeyboardEvent<HTMLInputElement>) => {
              if (e.key === 'Enter')
                handleLogin()
            }}
            placeholder={t('passwordPlaceholder', { ns: 'login' }) || ''}
            autoComplete="current-password"
          />
          <Button
            type="button"
            variant="ghost"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute inset-y-0 right-0 px-3"
          >
            {showPassword ? '👀' : '😝'}
          </Button>
        </div>
      </div>

      <Button
        variant="primary"
        onClick={handleLogin}
        disabled={isLoading || !identifier || !password}
        className="w-full"
        loading={isLoading}
      >
        {t('signBtn', { ns: 'login' })}
      </Button>
    </div>
  )
}

// [HRBUST MODIFIED] Register Form with quick (username+password) and email modes
type RegisterMode = 'quick' | 'email'
type EmailRegisterStep = 'email' | 'code' | 'password'

const RegisterForm = () => {
  const { t } = useTranslation()
  const locale = useLocale()
  const router = useRouter()

  // Mode toggle: quick (username+password) or email (existing flow)
  const [mode, setMode] = useState<RegisterMode>('quick')

  // Quick register state (username + password)
  const [quickUsername, setQuickUsername] = useState('')
  const [quickPassword, setQuickPassword] = useState('')
  const [quickConfirmPassword, setQuickConfirmPassword] = useState('')

  // Email register state (existing flow)
  const [emailStep, setEmailStep] = useState<EmailRegisterStep>('email')
  const [email, setEmail] = useState('')
  const [code, setCode] = useState('')
  const [emailPassword, setEmailPassword] = useState('')
  const [emailConfirmPassword, setEmailConfirmPassword] = useState('')

  const [isLoading, setIsLoading] = useState(false)
  const { mutateAsync: sendMail, isPending: isSendingMail } = useSendMail()

  // Username validation regex: 3-30 chars, alphanumeric and underscore
  const usernameRegex = /^\w{3,30}$/

  // Quick register handler
  const handleQuickRegister = async () => {
    if (!quickUsername.trim()) {
      toast.error('请输入用户名')
      return
    }
    if (!usernameRegex.test(quickUsername)) {
      toast.error('用户名格式不正确（3-30个字符，仅限字母、数字和下划线）')
      return
    }
    if (!quickPassword || quickPassword.length < 8) {
      toast.error(t('error.passwordLengthInValid', { ns: 'login' }))
      return
    }
    if (quickPassword !== quickConfirmPassword) {
      toast.error('两次输入的密码不一致')
      return
    }

    try {
      setIsLoading(true)
      const res = await fetch('/console/api/username-register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: quickUsername,
          password: encryptPassword(quickPassword),
          password_confirm: encryptPassword(quickConfirmPassword),
          language: locale,
        }),
      })

      const data = await res.json()
      if (data.result === 'success') {
        if (data.data?.access_token) {
          // Login succeeded - auto login
          toast.success('账户创建成功')
          setWebAppAccessToken(data.data.access_token)
          router.replace('/apps')
        }
        else {
          // Registration succeeded but login failed - redirect to login
          toast.success('账户创建成功，请登录')
          router.replace('/signin')
        }
      }
      else {
        toast.error(data.message || data.data || '注册失败')
      }
    }
    catch {
      toast.error('注册失败')
    }
    finally {
      setIsLoading(false)
    }
  }

  // Email register handlers
  const handleSendCode = async () => {
    if (!email) {
      toast.error(t('error.emailEmpty', { ns: 'login' }))
      return
    }
    if (!emailRegex.test(email)) {
      toast.error(t('error.emailInValid', { ns: 'login' }))
      return
    }

    try {
      const res = await sendMail({ email, language: locale })
      if (res.result === 'success') {
        setEmailStep('code')
        toast.success('验证码已发送')
      }
    }
    catch {
      toast.error('验证码发送失败')
    }
  }

  const handleVerifyCode = () => {
    if (!code || code.length !== 6) {
      toast.error('请输入有效的6位验证码')
      return
    }
    setEmailStep('password')
  }

  const handleEmailRegister = async () => {
    if (!emailPassword || emailPassword.length < 8) {
      toast.error(t('error.passwordLengthInValid', { ns: 'login' }))
      return
    }
    if (emailPassword !== emailConfirmPassword) {
      toast.error('两次输入的密码不一致')
      return
    }

    try {
      setIsLoading(true)
      const res = await fetch('/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          verification_code: code,
          password: encryptPassword(emailPassword),
          password_confirm: encryptPassword(emailConfirmPassword),
        }),
      })

      const data = await res.json()
      if (data.result === 'success') {
        toast.success('账户创建成功')
        router.push('/signin')
      }
      else {
        toast.error(data.data || '注册失败')
      }
    }
    catch {
      toast.error('注册失败')
    }
    finally {
      setIsLoading(false)
    }
  }

  const resendCode = async () => {
    const res = await sendMail({ email, language: locale })
    if (res.result === 'success') {
      toast.success('验证码已重新发送')
    }
  }

  return (
    <div className="space-y-4">
      {/* Mode Toggle */}
      <div className="border-border-default mb-4 flex border-b">
        <button
          type="button"
          onClick={() => setMode('quick')}
          className={`flex-1 pb-2 text-sm font-medium transition-colors ${
            mode === 'quick'
              ? 'border-b-2 border-indigo-500 text-indigo-600'
              : 'text-text-tertiary hover:text-text-secondary'
          }`}
        >
          快速注册
        </button>
        <button
          type="button"
          onClick={() => setMode('email')}
          className={`flex-1 pb-2 text-sm font-medium transition-colors ${
            mode === 'email'
              ? 'border-b-2 border-indigo-500 text-indigo-600'
              : 'text-text-tertiary hover:text-text-secondary'
          }`}
        >
          邮箱注册
        </button>
      </div>

      {/* Quick Register: Username + Password */}
      {mode === 'quick' && (
        <>
          <div>
            <Label htmlFor="register-username">用户名</Label>
            <Input
              id="register-username"
              type="text"
              value={quickUsername}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setQuickUsername(e.target.value)}
              placeholder="3-30个字符，支持字母、数字和下划线"
              className="mt-1"
              autoComplete="username"
            />
          </div>

          <div>
            <Label htmlFor="register-quick-password">{t('password', { ns: 'login' })}</Label>
            <Input
              id="register-quick-password"
              type="password"
              value={quickPassword}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setQuickPassword(e.target.value)}
              placeholder={t('passwordPlaceholder', { ns: 'login' }) || ''}
              className="mt-1"
              autoComplete="new-password"
            />
          </div>

          <div>
            <Label htmlFor="register-quick-confirm">{t('confirmPassword', { ns: 'login' })}</Label>
            <Input
              id="register-quick-confirm"
              type="password"
              value={quickConfirmPassword}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setQuickConfirmPassword(e.target.value)}
              placeholder={t('confirmPasswordPlaceholder', { ns: 'login' }) || ''}
              className="mt-1"
              autoComplete="new-password"
            />
          </div>

          <Button
            variant="primary"
            onClick={handleQuickRegister}
            disabled={isLoading || !quickUsername || !quickPassword || !quickConfirmPassword}
            className="w-full"
            loading={isLoading}
          >
            {t('signup.createAccount', { ns: 'login' })}
          </Button>
        </>
      )}

      {/* Email Register: Email -> Code -> Password */}
      {mode === 'email' && emailStep === 'email' && (
        <>
          <div>
            <Label htmlFor="register-email">{t('email', { ns: 'login' })}</Label>
            <Input
              id="register-email"
              type="email"
              value={email}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setEmail(e.target.value)}
              placeholder={t('emailPlaceholder', { ns: 'login' }) || ''}
              className="mt-1"
              autoComplete="email"
            />
          </div>

          <Button
            variant="primary"
            onClick={handleSendCode}
            disabled={isSendingMail || !email}
            className="w-full"
            loading={isSendingMail}
          >
            {t('signup.verifyMail', { ns: 'login' })}
          </Button>
        </>
      )}

      {mode === 'email' && emailStep === 'code' && (
        <>
          <div>
            <div className="flex items-center justify-between">
              <Label htmlFor="verify-code">验证码</Label>
              <button
                type="button"
                onClick={resendCode}
                className="system-xs-regular text-components-button-secondary-accent-text hover:underline"
              >
                重新发送
              </button>
            </div>
            <Input
              id="verify-code"
              type="text"
              value={code}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setCode(e.target.value)}
              placeholder="请输入6位验证码"
              className="mt-1"
              maxLength={6}
            />
          </div>

          <Button
            variant="primary"
            onClick={handleVerifyCode}
            disabled={!code || code.length < 6}
            className="w-full"
          >
            验证
          </Button>

          <div className="text-center">
            <button
              type="button"
              onClick={() => setEmailStep('email')}
              className="system-xs-regular text-text-tertiary hover:text-text-secondary"
            >
              返回
            </button>
          </div>
        </>
      )}

      {mode === 'email' && emailStep === 'password' && (
        <>
          <div>
            <Label htmlFor="register-email-password">{t('password', { ns: 'login' })}</Label>
            <Input
              id="register-email-password"
              type="password"
              value={emailPassword}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setEmailPassword(e.target.value)}
              placeholder={t('passwordPlaceholder', { ns: 'login' }) || ''}
              className="mt-1"
            />
          </div>

          <div>
            <Label htmlFor="register-email-confirm">{t('confirmPassword', { ns: 'login' })}</Label>
            <Input
              id="register-email-confirm"
              type="password"
              value={emailConfirmPassword}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setEmailConfirmPassword(e.target.value)}
              placeholder={t('confirmPasswordPlaceholder', { ns: 'login' }) || ''}
              className="mt-1"
            />
          </div>

          <Button
            variant="primary"
            onClick={handleEmailRegister}
            disabled={isLoading || !emailPassword || !emailConfirmPassword}
            className="w-full"
            loading={isLoading}
          >
            {t('signup.createAccount', { ns: 'login' })}
          </Button>

          <div className="text-center">
            <button
              type="button"
              onClick={() => setEmailStep('email')}
              className="system-xs-regular text-text-tertiary hover:text-text-secondary"
            >
              返回
            </button>
          </div>
        </>
      )}
    </div>
  )
}

// Main Unified Auth Page
const currentYear = new Date().getFullYear()

const SignIn = () => {
  const { t } = useTranslation()
  const { systemFeatures } = useGlobalPublicStore()

  return (
    <div className="flex min-h-screen w-full items-center justify-center bg-gradient-to-br from-indigo-500/10 to-violet-500/10 p-6">
      <div className="w-full max-w-[420px]">
        {/* Logo */}
        <div className="mb-8 flex flex-col items-center">
          <DataDevelopmentLogo size="large" />
          <p className="mt-1 text-sm text-text-secondary">
            {t('welcome', { ns: 'login' })}
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-center">
              {systemFeatures.branding.enabled
                ? t('pageTitleForE', { ns: 'login' })
                : t('pageTitle', { ns: 'login' })}
            </CardTitle>
            <CardDescription className="text-center">
              登录或创建账户
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="login" className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="login">登录</TabsTrigger>
                <TabsTrigger value="register">注册</TabsTrigger>
              </TabsList>

              <TabsContent value="login">
                <LoginForm />
              </TabsContent>

              <TabsContent value="register">
                <RegisterForm />
              </TabsContent>
            </Tabs>

            <Split className="mt-6" />

            {/* Footer Links */}
            <div className="mt-4 text-center system-xs-regular text-text-tertiary">
              {t('tosDesc', { ns: 'login' })}
              {' '}
              <Link
                className="text-text-secondary hover:underline"
                target="_blank"
                rel="noopener noreferrer"
                href="https://dify.ai/terms"
              >
                {t('tos', { ns: 'login' })}
              </Link>
              {' & '}
              <Link
                className="text-text-secondary hover:underline"
                target="_blank"
                rel="noopener noreferrer"
                href="https://dify.ai/privacy"
              >
                {t('pp', { ns: 'login' })}
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Copyright */}
        {!systemFeatures.branding.enabled && (
          <div className="mt-6 text-center system-xs-regular text-text-tertiary">
            ©
            {' '}
            {currentYear}
            {' '}
            LangGenius, Inc. All rights reserved.
          </div>
        )}
      </div>
    </div>
  )
}

export default SignIn
