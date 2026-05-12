// Ruta: frontend/src/stores/auth.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import http from '@/core/http'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('landha_token') || null)
  const user = ref(JSON.parse(localStorage.getItem('landha_user') || 'null'))

  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isSeller = computed(() => user.value?.role === 'seller')

  async function login(username, password) {
    const { data } = await http.post('/auth/login', { username, password })
    token.value = data.access_token
    user.value = { id: data.user_id, username: data.username, role: data.role }
    localStorage.setItem('landha_token', data.access_token)
    localStorage.setItem('landha_user', JSON.stringify(user.value))
    return data
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('landha_token')
    localStorage.removeItem('landha_user')
  }

  return { token, user, isAuthenticated, isAdmin, isSeller, login, logout }
})