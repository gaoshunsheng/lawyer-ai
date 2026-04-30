import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, LoginForm, RegisterForm } from '@/types'
import { userApi } from '@/api/user'
import Cookies from 'js-cookie'
import router from '@/router'

export const useUserStore = defineStore('user', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string>('')
  const loading = ref(false)

  // Getters
  const isLoggedIn = computed(() => !!token.value)
  const userInfo = computed(() => user.value)

  // Actions
  async function login(form: LoginForm) {
    loading.value = true
    try {
      const res = await userApi.login(form)
      token.value = res.data.token
      user.value = res.data.user
      Cookies.set('token', res.data.token, { expires: 7 })
      return res
    } finally {
      loading.value = false
    }
  }

  async function register(form: RegisterForm) {
    loading.value = true
    try {
      const res = await userApi.register(form)
      return res
    } finally {
      loading.value = false
    }
  }

  async function getUserInfo() {
    if (!token.value) return
    loading.value = true
    try {
      const res = await userApi.getUserInfo()
      user.value = res.data
    } finally {
      loading.value = false
    }
  }

  async function updateUserInfo(data: Partial<User>) {
    loading.value = true
    try {
      const res = await userApi.updateUserInfo(data)
      user.value = res.data
      return res
    } finally {
      loading.value = false
    }
  }

  async function changePassword(oldPassword: string, newPassword: string) {
    loading.value = true
    try {
      const res = await userApi.changePassword({ oldPassword, newPassword })
      return res
    } finally {
      loading.value = false
    }
  }

  function logout() {
    user.value = null
    token.value = ''
    Cookies.remove('token')
    router.push('/login')
  }

  function setToken(newToken: string) {
    token.value = newToken
  }

  // 初始化时从cookie恢复token
  function initFromCookie() {
    const savedToken = Cookies.get('token')
    if (savedToken) {
      token.value = savedToken
      getUserInfo()
    }
  }

  return {
    // State
    user,
    token,
    loading,
    // Getters
    isLoggedIn,
    userInfo,
    // Actions
    login,
    register,
    getUserInfo,
    updateUserInfo,
    changePassword,
    logout,
    setToken,
    initFromCookie,
  }
})
