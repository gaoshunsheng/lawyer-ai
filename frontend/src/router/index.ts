import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import NProgress from 'nprogress'
import Cookies from 'js-cookie'

// 路由配置
const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { title: '登录', hideLayout: true },
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '工作台', icon: 'House' },
      },
      {
        path: 'case',
        name: 'Case',
        redirect: '/case/list',
        meta: { title: '案件管理', icon: 'Briefcase' },
        children: [
          {
            path: 'list',
            name: 'CaseList',
            component: () => import('@/views/case/list.vue'),
            meta: { title: '案件列表', icon: 'List' },
          },
          {
            path: 'detail/:id',
            name: 'CaseDetail',
            component: () => import('@/views/case/detail.vue'),
            meta: { title: '案件详情', hideMenu: true },
          },
          {
            path: 'create',
            name: 'CaseCreate',
            component: () => import('@/views/case/form.vue'),
            meta: { title: '创建案件', hideMenu: true },
          },
          {
            path: 'edit/:id',
            name: 'CaseEdit',
            component: () => import('@/views/case/form.vue'),
            meta: { title: '编辑案件', hideMenu: true },
          },
        ],
      },
      {
        path: 'document',
        name: 'Document',
        redirect: '/document/list',
        meta: { title: '文书中心', icon: 'Document' },
        children: [
          {
            path: 'list',
            name: 'DocumentList',
            component: () => import('@/views/document/list.vue'),
            meta: { title: '文书列表', icon: 'List' },
          },
          {
            path: 'template',
            name: 'DocumentTemplate',
            component: () => import('@/views/document/template.vue'),
            meta: { title: '文书模板', icon: 'Tickets' },
          },
          {
            path: 'create',
            name: 'DocumentCreate',
            component: () => import('@/views/document/form.vue'),
            meta: { title: '创建文书', hideMenu: true },
          },
          {
            path: 'edit/:id',
            name: 'DocumentEdit',
            component: () => import('@/views/document/form.vue'),
            meta: { title: '编辑文书', hideMenu: true },
          },
        ],
      },
      {
        path: 'chat',
        name: 'Chat',
        component: () => import('@/views/chat/index.vue'),
        meta: { title: '智能咨询', icon: 'ChatDotSquare' },
      },
      {
        path: 'knowledge',
        name: 'Knowledge',
        redirect: '/knowledge/list',
        meta: { title: '知识库', icon: 'Collection' },
        children: [
          {
            path: 'list',
            name: 'KnowledgeList',
            component: () => import('@/views/knowledge/list.vue'),
            meta: { title: '知识列表', icon: 'List' },
          },
          {
            path: 'law',
            name: 'KnowledgeLaw',
            component: () => import('@/views/knowledge/law.vue'),
            meta: { title: '法规库', icon: 'Notebook' },
          },
          {
            path: 'case',
            name: 'KnowledgeCase',
            component: () => import('@/views/knowledge/case.vue'),
            meta: { title: '案例库', icon: 'Files' },
          },
        ],
      },
      {
        path: 'calculator',
        name: 'Calculator',
        component: () => import('@/views/calculator/index.vue'),
        meta: { title: '赔偿计算', icon: 'Calculator' },
      },
      {
        path: 'statistics',
        name: 'Statistics',
        component: () => import('@/views/statistics/index.vue'),
        meta: { title: '数据统计', icon: 'DataAnalysis' },
      },
      {
        path: 'user',
        name: 'User',
        redirect: '/user/profile',
        meta: { title: '用户中心', icon: 'User' },
        children: [
          {
            path: 'profile',
            name: 'UserProfile',
            component: () => import('@/views/user/profile.vue'),
            meta: { title: '个人中心', icon: 'UserFilled' },
          },
          {
            path: 'management',
            name: 'UserManagement',
            component: () => import('@/views/user/management.vue'),
            meta: { title: '用户管理', icon: 'Avatar' },
          },
        ],
      },
    ],
  },
  {
    path: '/403',
    name: 'Forbidden',
    component: () => import('@/views/error/403.vue'),
    meta: { title: '无权限', hideLayout: true },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/error/404.vue'),
    meta: { title: '页面不存在', hideLayout: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  NProgress.start()

  // 设置页面标题
  document.title = `${to.meta.title || '首页'} - 律师AI助手`

  // 检查登录状态
  const token = Cookies.get('token')
  if (to.path !== '/login' && !token) {
    next('/login')
    return
  }

  // 已登录时访问登录页，跳转到首页
  if (to.path === '/login' && token) {
    next('/dashboard')
    return
  }

  next()
})

router.afterEach(() => {
  NProgress.done()
})

export default router
