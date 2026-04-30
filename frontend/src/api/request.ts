import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse, type AxiosError } from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import NProgress from 'nprogress'
import { useUserStore } from '@/stores/user'
import router from '@/router'
import Cookies from 'js-cookie'

// 创建axios实例
const service: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    NProgress.start()

    // 添加token
    const userStore = useUserStore()
    const token = userStore.token || Cookies.get('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // 添加租户ID
    const tenantId = userStore.user?.tenantId
    if (tenantId) {
      config.headers['X-Tenant-Id'] = tenantId
    }

    return config
  },
  (error) => {
    NProgress.done()
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  (response: AxiosResponse) => {
    NProgress.done()

    const res = response.data

    // 根据业务状态码处理
    if (res.code !== 200) {
      ElMessage({
        message: res.message || '请求失败',
        type: 'error',
        duration: 5000,
      })

      // 401: 未登录或token过期
      if (res.code === 401) {
        const userStore = useUserStore()
        userStore.logout()

        ElMessageBox.confirm('登录状态已过期，请重新登录', '提示', {
          confirmButtonText: '重新登录',
          cancelButtonText: '取消',
          type: 'warning',
        }).then(() => {
          router.push('/login')
        })
      }

      // 403: 无权限
      if (res.code === 403) {
        ElMessage.error('没有权限访问该资源')
        router.push('/403')
      }

      return Promise.reject(new Error(res.message || 'Error'))
    }

    return res
  },
  (error: AxiosError) => {
    NProgress.done()

    let message = '请求失败'

    if (error.response) {
      switch (error.response.status) {
        case 400:
          message = '请求参数错误'
          break
        case 401:
          message = '未授权，请登录'
          const userStore = useUserStore()
          userStore.logout()
          router.push('/login')
          break
        case 403:
          message = '拒绝访问'
          break
        case 404:
          message = '请求地址不存在'
          break
        case 408:
          message = '请求超时'
          break
        case 500:
          message = '服务器内部错误'
          break
        case 501:
          message = '服务未实现'
          break
        case 502:
          message = '网关错误'
          break
        case 503:
          message = '服务不可用'
          break
        case 504:
          message = '网关超时'
          break
        case 505:
          message = 'HTTP版本不受支持'
          break
        default:
          message = `请求失败: ${error.response.status}`
      }
    } else if (error.code === 'ECONNABORTED') {
      message = '请求超时'
    } else if (error.message.includes('Network Error')) {
      message = '网络错误，请检查网络连接'
    }

    ElMessage.error(message)
    return Promise.reject(error)
  }
)

// 封装请求方法
export interface RequestOptions extends AxiosRequestConfig {
  showLoading?: boolean
  showSuccess?: boolean
  successMessage?: string
  showError?: boolean
}

export const request = {
  get<T = any>(url: string, params?: object, options?: RequestOptions): Promise<T> {
    return service.get(url, { params, ...options })
  },

  post<T = any>(url: string, data?: object, options?: RequestOptions): Promise<T> {
    return service.post(url, data, options)
  },

  put<T = any>(url: string, data?: object, options?: RequestOptions): Promise<T> {
    return service.put(url, data, options)
  },

  delete<T = any>(url: string, params?: object, options?: RequestOptions): Promise<T> {
    return service.delete(url, { params, ...options })
  },

  patch<T = any>(url: string, data?: object, options?: RequestOptions): Promise<T> {
    return service.patch(url, data, options)
  },

  upload<T = any>(url: string, file: File, onProgress?: (progress: number) => void): Promise<T> {
    const formData = new FormData()
    formData.append('file', file)

    return service.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total && onProgress) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(progress)
        }
      },
    })
  },

  download(url: string, params?: object, filename?: string): Promise<void> {
    return service
      .get(url, {
        params,
        responseType: 'blob',
      })
      .then((response: any) => {
        const blob = new Blob([response])
        const downloadUrl = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = downloadUrl
        link.download = filename || 'download'
        link.click()
        window.URL.revokeObjectURL(downloadUrl)
      })
  },
}

export default service
