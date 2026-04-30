import request from './request'
import type { LoginForm, LoginResult, User } from '@/types'

// 用户登录
export function login(data: LoginForm) {
  return request.post<LoginResult>('/auth/login', data)
}

// 用户登出
export function logout() {
  return request.post('/auth/logout')
}

// 刷新token
export function refreshToken(refreshToken: string) {
  return request.post<LoginResult>('/auth/refresh', { refreshToken })
}

// 获取当前用户信息
export function getCurrentUser() {
  return request.get<User>('/auth/me')
}

// 更新用户信息
export function updateUser(id: number, data: Partial<User>) {
  return request.put<User>(`/user/${id}`, data)
}

// 修改密码
export function changePassword(data: { oldPassword: string; newPassword: string }) {
  return request.put('/auth/password', data)
}

// 用户注册
export function register(data: {
  username: string
  password: string
  email: string
  phone: string
  realName: string
}) {
  return request.post<User>('/auth/register', data)
}

// 获取用户列表
export function getUsers(params: {
  page: number
  pageSize: number
  keyword?: string
  role?: string
  status?: number
}) {
  return request.get('/user', params)
}

// 创建用户
export function createUser(data: Partial<User>) {
  return request.post<User>('/user', data)
}

// 删除用户
export function deleteUser(id: number) {
  return request.delete(`/user/${id}`)
}

// 重置密码
export function resetPassword(id: number) {
  return request.put(`/user/${id}/reset-password`)
}
