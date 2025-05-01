<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-3xl font-bold">App Store</h1>
      <div class="flex space-x-4">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search apps..."
          class="px-4 py-2 rounded bg-gray-800 text-white"
        />
        <select
          v-model="selectedCategory"
          class="px-4 py-2 rounded bg-gray-800 text-white"
        >
          <option value="">All Categories</option>
          <option v-for="category in categories" :key="category" :value="category">
            {{ category }}
          </option>
        </select>
      </div>
    </div>

    <!-- Installed Apps Section -->
    <div v-if="installedApps.length > 0" class="mb-8">
      <h2 class="text-2xl font-bold mb-4">Installed Apps</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="app in installedApps"
          :key="app.id"
          class="bg-gray-800 rounded-lg p-6 hover:bg-gray-700 transition-colors"
        >
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center space-x-4">
              <img
                :src="getAppIcon(app.name)"
                :alt="app.name"
                class="w-12 h-12 rounded"
                @error="handleImageError"
              />
              <div>
                <h2 class="text-xl font-semibold">{{ app.name }}</h2>
                <p class="text-gray-400">{{ app.status }}</p>
              </div>
            </div>
            <div class="flex space-x-2">
              <button
                v-if="app.status === 'running'"
                @click="stopApp(app.id)"
                class="px-3 py-1 bg-red-600 rounded hover:bg-red-700 transition-colors"
              >
                Stop
              </button>
              <button
                v-else
                @click="startApp(app.id)"
                class="px-3 py-1 bg-green-600 rounded hover:bg-green-700 transition-colors"
              >
                Start
              </button>
              <button
                @click="restartApp(app.id)"
                class="px-3 py-1 bg-blue-600 rounded hover:bg-blue-700 transition-colors"
              >
                Restart
              </button>
            </div>
          </div>
          <div class="text-sm text-gray-400">
            <p>Port: {{ app.port }}</p>
            <p>Installed: {{ formatDate(app.created_at) }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Available Apps Section -->
    <h2 class="text-2xl font-bold mb-4">Available Apps</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="app in filteredApps"
        :key="app.name"
        class="bg-gray-800 rounded-lg p-6 hover:bg-gray-700 transition-colors"
      >
        <div class="flex items-center space-x-4 mb-4">
          <img
            :src="app.icon"
            :alt="app.name"
            class="w-12 h-12 rounded"
            @error="handleImageError"
          />
          <div>
            <h2 class="text-xl font-semibold">{{ app.name }}</h2>
            <p class="text-gray-400">{{ app.category }}</p>
          </div>
        </div>
        <p class="text-gray-300 mb-4">{{ app.description }}</p>
        
        <!-- App Details -->
        <div class="space-y-2 mb-4">
          <div class="flex justify-between text-sm">
            <span class="text-gray-400">Version:</span>
            <span class="text-gray-300">{{ app.version }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-400">Memory:</span>
            <span class="text-gray-300">{{ app.requirements.memory }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-400">Storage:</span>
            <span class="text-gray-300">{{ app.requirements.storage }}</span>
          </div>
        </div>

        <!-- Tags -->
        <div class="flex flex-wrap gap-2 mb-4">
          <span
            v-for="tag in app.tags"
            :key="tag"
            class="px-2 py-1 bg-gray-700 rounded text-sm"
          >
            {{ tag }}
          </span>
        </div>

        <div class="flex justify-between items-center">
          <span class="text-gray-400">Port: {{ app.port }}</span>
          <button
            v-if="isAdmin"
            @click="installApp(app)"
            class="px-4 py-2 bg-blue-600 rounded hover:bg-blue-700 transition-colors"
          >
            Install
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import axios from 'axios'
import { useToast } from 'vue-toastification'

export default {
  name: 'AppStore',
  setup() {
    const toast = useToast()
    const apps = ref([])
    const installedApps = ref([])
    const searchQuery = ref('')
    const selectedCategory = ref('')
    const isAdmin = ref(false)

    const fetchApps = async () => {
      try {
        const response = await axios.get('/api/apps')
        apps.value = response.data.apps
      } catch (error) {
        toast.error('Failed to fetch apps')
        console.error('Error fetching apps:', error)
      }
    }

    const fetchInstalledApps = async () => {
      try {
        const response = await axios.get('/api/apps/installed')
        installedApps.value = response.data
      } catch (error) {
        toast.error('Failed to fetch installed apps')
        console.error('Error fetching installed apps:', error)
      }
    }

    const checkAdminStatus = async () => {
      try {
        const response = await axios.get('/api/check-auth')
        isAdmin.value = response.data.role === 'admin'
      } catch (error) {
        isAdmin.value = false
      }
    }

    const installApp = async (app) => {
      try {
        await axios.post('/api/apps/install', {
          name: app.name,
          image: app.image,
          port: app.port,
          config: app.config
        })
        toast.success(`${app.name} installed successfully`)
        fetchInstalledApps()
      } catch (error) {
        toast.error(`Failed to install ${app.name}`)
        console.error('Error installing app:', error)
      }
    }

    const stopApp = async (appId) => {
      try {
        await axios.post(`/api/apps/${appId}/stop`)
        toast.success('App stopped successfully')
        fetchInstalledApps()
      } catch (error) {
        toast.error('Failed to stop app')
        console.error('Error stopping app:', error)
      }
    }

    const startApp = async (appId) => {
      try {
        await axios.post(`/api/apps/${appId}/start`)
        toast.success('App started successfully')
        fetchInstalledApps()
      } catch (error) {
        toast.error('Failed to start app')
        console.error('Error starting app:', error)
      }
    }

    const restartApp = async (appId) => {
      try {
        await axios.post(`/api/apps/${appId}/restart`)
        toast.success('App restarted successfully')
        fetchInstalledApps()
      } catch (error) {
        toast.error('Failed to restart app')
        console.error('Error restarting app:', error)
      }
    }

    const handleImageError = (event) => {
      event.target.src = 'https://via.placeholder.com/48'
    }

    const getAppIcon = (appName) => {
      const app = apps.value.find(a => a.name === appName)
      return app ? app.icon : 'https://via.placeholder.com/48'
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }

    const categories = computed(() => {
      const uniqueCategories = new Set(apps.value.map(app => app.category))
      return Array.from(uniqueCategories)
    })

    const filteredApps = computed(() => {
      return apps.value.filter(app => {
        const matchesSearch = app.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                            app.description.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                            app.tags.some(tag => tag.toLowerCase().includes(searchQuery.value.toLowerCase()))
        const matchesCategory = !selectedCategory.value || app.category === selectedCategory.value
        return matchesSearch && matchesCategory
      })
    })

    // Fetch data on component mount
    fetchApps()
    fetchInstalledApps()
    checkAdminStatus()

    return {
      apps,
      installedApps,
      searchQuery,
      selectedCategory,
      categories,
      filteredApps,
      isAdmin,
      installApp,
      stopApp,
      startApp,
      restartApp,
      handleImageError,
      getAppIcon,
      formatDate
    }
  }
}
</script> 