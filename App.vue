<template>
  <div class="min-h-screen bg-gray-900 text-white">
    <!-- Navigation -->
    <nav class="bg-gray-800 p-4">
      <div class="container mx-auto flex justify-between items-center">
        <router-link to="/" class="text-2xl font-bold">HoleUI</router-link>
        <div class="flex items-center space-x-4">
          <template v-if="!isLoggedIn">
            <router-link to="/login" class="hover:text-gray-300">Login</router-link>
            <router-link to="/register" class="hover:text-gray-300">Register</router-link>
          </template>
          <template v-else>
            <span class="text-gray-300">{{ username }}</span>
            <button @click="logout" class="hover:text-gray-300">Logout</button>
          </template>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="container mx-auto p-4">
      <router-view></router-view>
    </main>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

export default {
  name: 'App',
  setup() {
    const router = useRouter()
    const isLoggedIn = ref(false)
    const username = ref('')

    const checkAuth = async () => {
      try {
        const response = await axios.get('/api/check-auth')
        isLoggedIn.value = true
        username.value = response.data.username
      } catch (error) {
        isLoggedIn.value = false
        username.value = ''
      }
    }

    const logout = async () => {
      try {
        await axios.post('/api/logout')
        isLoggedIn.value = false
        username.value = ''
        router.push('/login')
      } catch (error) {
        console.error('Logout failed:', error)
      }
    }

    // Check auth status on component mount
    checkAuth()

    return {
      isLoggedIn,
      username,
      logout
    }
  }
}
</script>

<style>
@import 'tailwindcss/base';
@import 'tailwindcss/components';
@import 'tailwindcss/utilities';
</style> 