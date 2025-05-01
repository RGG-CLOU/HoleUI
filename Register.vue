<template>
  <div class="max-w-md mx-auto mt-10 p-6 bg-gray-800 rounded-lg">
    <h2 class="text-2xl font-bold mb-6">Register</h2>
    <form @submit.prevent="handleRegister" class="space-y-4">
      <div>
        <label class="block text-gray-300 mb-2">Username</label>
        <input
          v-model="username"
          type="text"
          class="w-full px-4 py-2 rounded bg-gray-700 text-white"
          required
        />
      </div>
      <div>
        <label class="block text-gray-300 mb-2">Password</label>
        <input
          v-model="password"
          type="password"
          class="w-full px-4 py-2 rounded bg-gray-700 text-white"
          required
        />
      </div>
      <div>
        <label class="block text-gray-300 mb-2">Confirm Password</label>
        <input
          v-model="confirmPassword"
          type="password"
          class="w-full px-4 py-2 rounded bg-gray-700 text-white"
          required
        />
      </div>
      <button
        type="submit"
        class="w-full py-2 bg-blue-600 rounded hover:bg-blue-700 transition-colors"
      >
        Register
      </button>
    </form>
    <p class="mt-4 text-center">
      Already have an account?
      <router-link to="/login" class="text-blue-400 hover:text-blue-300">
        Login here
      </router-link>
    </p>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useToast } from 'vue-toastification'

export default {
  name: 'Register',
  setup() {
    const router = useRouter()
    const toast = useToast()
    const username = ref('')
    const password = ref('')
    const confirmPassword = ref('')

    const handleRegister = async () => {
      if (password.value !== confirmPassword.value) {
        toast.error('Passwords do not match')
        return
      }

      try {
        await axios.post('/api/register', {
          username: username.value,
          password: password.value
        })
        
        toast.success('Registration successful')
        router.push('/login')
      } catch (error) {
        toast.error('Registration failed')
        console.error('Registration error:', error)
      }
    }

    return {
      username,
      password,
      confirmPassword,
      handleRegister
    }
  }
}
</script> 