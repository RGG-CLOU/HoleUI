<template>
  <div class="space-y-6">
    <h1 class="text-3xl font-bold">System Monitor</h1>
    
    <!-- Real-time Stats -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <!-- CPU Usage -->
      <div class="bg-gray-800 rounded-lg p-6">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-semibold">CPU Usage</h2>
          <span class="text-2xl font-bold" :class="getCpuColor(cpuUsage)">
            {{ cpuUsage }}%
          </span>
        </div>
        <div class="h-2 bg-gray-700 rounded-full">
          <div 
            class="h-full rounded-full transition-all duration-500"
            :class="getCpuColor(cpuUsage)"
            :style="{ width: `${cpuUsage}%` }"
          ></div>
        </div>
        <div class="mt-4 text-sm text-gray-400">
          <p>Temperature: {{ cpuTemp }}°C</p>
          <p>Frequency: {{ cpuFreq }} MHz</p>
        </div>
      </div>

      <!-- Memory Usage -->
      <div class="bg-gray-800 rounded-lg p-6">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-semibold">Memory Usage</h2>
          <span class="text-2xl font-bold" :class="getMemoryColor(memoryUsage)">
            {{ memoryUsage }}%
          </span>
        </div>
        <div class="h-2 bg-gray-700 rounded-full">
          <div 
            class="h-full rounded-full transition-all duration-500"
            :class="getMemoryColor(memoryUsage)"
            :style="{ width: `${memoryUsage}%` }"
          ></div>
        </div>
        <div class="mt-4 text-sm text-gray-400">
          <p>Used: {{ formatBytes(memoryUsed) }}</p>
          <p>Total: {{ formatBytes(memoryTotal) }}</p>
        </div>
      </div>

      <!-- Storage Usage -->
      <div class="bg-gray-800 rounded-lg p-6">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-semibold">Storage Usage</h2>
          <span class="text-2xl font-bold" :class="getStorageColor(storageUsage)">
            {{ storageUsage }}%
          </span>
        </div>
        <div class="h-2 bg-gray-700 rounded-full">
          <div 
            class="h-full rounded-full transition-all duration-500"
            :class="getStorageColor(storageUsage)"
            :style="{ width: `${storageUsage}%` }"
          ></div>
        </div>
        <div class="mt-4 text-sm text-gray-400">
          <p>Used: {{ formatBytes(storageUsed) }}</p>
          <p>Total: {{ formatBytes(storageTotal) }}</p>
        </div>
      </div>
    </div>

    <!-- Performance Settings -->
    <div class="bg-gray-800 rounded-lg p-6">
      <h2 class="text-xl font-semibold mb-4">Performance Settings</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- CPU Settings -->
        <div>
          <h3 class="text-lg font-medium mb-2">CPU Settings</h3>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-400">CPU Governor</label>
              <select 
                v-model="cpuGovernor"
                class="mt-1 block w-full rounded-md bg-gray-700 border-gray-600 text-white"
                @change="updateCpuGovernor"
              >
                <option value="performance">Performance</option>
                <option value="ondemand">On Demand</option>
                <option value="powersave">Power Save</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-400">CPU Frequency</label>
              <div class="flex items-center space-x-2">
                <input 
                  type="range" 
                  v-model="cpuFrequency"
                  :min="minCpuFreq"
                  :max="maxCpuFreq"
                  class="w-full"
                  @change="updateCpuFrequency"
                >
                <span class="text-sm text-gray-400">{{ cpuFrequency }} MHz</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Memory Settings -->
        <div>
          <h3 class="text-lg font-medium mb-2">Memory Settings</h3>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-400">Swappiness</label>
              <div class="flex items-center space-x-2">
                <input 
                  type="range" 
                  v-model="swappiness"
                  min="0"
                  max="100"
                  class="w-full"
                  @change="updateSwappiness"
                >
                <span class="text-sm text-gray-400">{{ swappiness }}</span>
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-400">Cache Pressure</label>
              <div class="flex items-center space-x-2">
                <input 
                  type="range" 
                  v-model="cachePressure"
                  min="0"
                  max="100"
                  class="w-full"
                  @change="updateCachePressure"
                >
                <span class="text-sm text-gray-400">{{ cachePressure }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- System Information -->
    <div class="bg-gray-800 rounded-lg p-6">
      <h2 class="text-xl font-semibold mb-4">System Information</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="text-sm">
          <p class="text-gray-400">Hostname: {{ systemInfo.hostname }}</p>
          <p class="text-gray-400">OS: {{ systemInfo.os }}</p>
          <p class="text-gray-400">Kernel: {{ systemInfo.kernel }}</p>
          <p class="text-gray-400">Uptime: {{ formatUptime(systemInfo.uptime) }}</p>
        </div>
        <div class="text-sm">
          <p class="text-gray-400">CPU Model: {{ systemInfo.cpuModel }}</p>
          <p class="text-gray-400">CPU Cores: {{ systemInfo.cpuCores }}</p>
          <p class="text-gray-400">Architecture: {{ systemInfo.architecture }}</p>
          <p class="text-gray-400">Load Average: {{ systemInfo.loadAverage }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import { useToast } from 'vue-toastification'

export default {
  name: 'SystemMonitor',
  setup() {
    const toast = useToast()
    const cpuUsage = ref(0)
    const memoryUsage = ref(0)
    const storageUsage = ref(0)
    const cpuTemp = ref(0)
    const cpuFreq = ref(0)
    const memoryUsed = ref(0)
    const memoryTotal = ref(0)
    const storageUsed = ref(0)
    const storageTotal = ref(0)
    const cpuGovernor = ref('ondemand')
    const cpuFrequency = ref(0)
    const minCpuFreq = ref(0)
    const maxCpuFreq = ref(0)
    const swappiness = ref(10)
    const cachePressure = ref(50)
    const systemInfo = ref({
      hostname: '',
      os: '',
      kernel: '',
      uptime: 0,
      cpuModel: '',
      cpuCores: 0,
      architecture: '',
      loadAverage: ''
    })

    let updateInterval

    const fetchSystemStats = async () => {
      try {
        const response = await axios.get('/api/system/stats')
        const data = response.data
        
        cpuUsage.value = data.cpu.usage
        memoryUsage.value = data.memory.usage
        storageUsage.value = data.storage.usage
        cpuTemp.value = data.cpu.temperature
        cpuFreq.value = data.cpu.frequency
        memoryUsed.value = data.memory.used
        memoryTotal.value = data.memory.total
        storageUsed.value = data.storage.used
        storageTotal.value = data.storage.total
      } catch (error) {
        console.error('Error fetching system stats:', error)
      }
    }

    const fetchSystemInfo = async () => {
      try {
        const response = await axios.get('/api/system/info')
        systemInfo.value = response.data
      } catch (error) {
        console.error('Error fetching system info:', error)
      }
    }

    const fetchCpuSettings = async () => {
      try {
        const response = await axios.get('/api/system/cpu-settings')
        const data = response.data
        cpuGovernor.value = data.governor
        cpuFrequency.value = data.frequency
        minCpuFreq.value = data.minFrequency
        maxCpuFreq.value = data.maxFrequency
      } catch (error) {
        console.error('Error fetching CPU settings:', error)
      }
    }

    const updateCpuGovernor = async () => {
      try {
        await axios.post('/api/system/cpu-settings/governor', {
          governor: cpuGovernor.value
        })
        toast.success('CPU governor updated successfully')
      } catch (error) {
        toast.error('Failed to update CPU governor')
        console.error('Error updating CPU governor:', error)
      }
    }

    const updateCpuFrequency = async () => {
      try {
        await axios.post('/api/system/cpu-settings/frequency', {
          frequency: cpuFrequency.value
        })
        toast.success('CPU frequency updated successfully')
      } catch (error) {
        toast.error('Failed to update CPU frequency')
        console.error('Error updating CPU frequency:', error)
      }
    }

    const updateSwappiness = async () => {
      try {
        await axios.post('/api/system/memory/swappiness', {
          value: swappiness.value
        })
        toast.success('Swappiness updated successfully')
      } catch (error) {
        toast.error('Failed to update swappiness')
        console.error('Error updating swappiness:', error)
      }
    }

    const updateCachePressure = async () => {
      try {
        await axios.post('/api/system/memory/cache-pressure', {
          value: cachePressure.value
        })
        toast.success('Cache pressure updated successfully')
      } catch (error) {
        toast.error('Failed to update cache pressure')
        console.error('Error updating cache pressure:', error)
      }
    }

    const getCpuColor = (usage) => {
      if (usage > 80) return 'bg-red-500'
      if (usage > 60) return 'bg-yellow-500'
      return 'bg-green-500'
    }

    const getMemoryColor = (usage) => {
      if (usage > 90) return 'bg-red-500'
      if (usage > 70) return 'bg-yellow-500'
      return 'bg-green-500'
    }

    const getStorageColor = (usage) => {
      if (usage > 90) return 'bg-red-500'
      if (usage > 70) return 'bg-yellow-500'
      return 'bg-green-500'
    }

    const formatBytes = (bytes) => {
      const units = ['B', 'KB', 'MB', 'GB', 'TB']
      let value = bytes
      let unitIndex = 0
      
      while (value >= 1024 && unitIndex < units.length - 1) {
        value /= 1024
        unitIndex++
      }
      
      return `${value.toFixed(1)} ${units[unitIndex]}`
    }

    const formatUptime = (seconds) => {
      const days = Math.floor(seconds / 86400)
      const hours = Math.floor((seconds % 86400) / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      
      return `${days}d ${hours}h ${minutes}m`
    }

    onMounted(() => {
      fetchSystemStats()
      fetchSystemInfo()
      fetchCpuSettings()
      
      updateInterval = setInterval(() => {
        fetchSystemStats()
      }, 5000)
    })

    onUnmounted(() => {
      clearInterval(updateInterval)
    })

    return {
      cpuUsage,
      memoryUsage,
      storageUsage,
      cpuTemp,
      cpuFreq,
      memoryUsed,
      memoryTotal,
      storageUsed,
      storageTotal,
      cpuGovernor,
      cpuFrequency,
      minCpuFreq,
      maxCpuFreq,
      swappiness,
      cachePressure,
      systemInfo,
      getCpuColor,
      getMemoryColor,
      getStorageColor,
      formatBytes,
      formatUptime,
      updateCpuGovernor,
      updateCpuFrequency,
      updateSwappiness,
      updateCachePressure
    }
  }
}
</script> 