<template>
  <div class="space-y-6">
    <h1 class="text-3xl font-bold">User Management</h1>

    <div class="bg-gray-800 rounded-lg p-6">
      <table class="w-full">
        <thead>
          <tr class="text-left border-b border-gray-700">
            <th class="pb-4">Username</th>
            <th class="pb-4">Role</th>
            <th class="pb-4">Created At</th>
            <th class="pb-4">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id" class="border-b border-gray-700">
            <td class="py-4">{{ user.username }}</td>
            <td class="py-4">
              <span :class="{
                'px-2 py-1 rounded': true,
                'bg-blue-600': user.role === 'admin',
                'bg-gray-600': user.role === 'user'
              }">
                {{ user.role }}
              </span>
            </td>
            <td class="py-4">{{ formatDate(user.created_at) }}</td>
            <td class="py-4">
              <div class="flex space-x-2">
                <button
                  v-if="user.role === 'user'"
                  @click="promoteUser(user.id)"
                  class="px-3 py-1 bg-green-600 rounded hover:bg-green-700 transition-colors"
                >
                  Promote
                </button>
                <button
                  @click="deleteUser(user.id)"
                  class="px-3 py-1 bg-red-600 rounded hover:bg-red-700 transition-colors"
                >
                  Delete
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import axios from 'axios'
import { useToast } from 'vue-toastification'

export default {
  name: 'UserManagement',
  setup() {
    const toast = useToast()
    const users = ref([])

    const fetchUsers = async () => {
      try {
        const response = await axios.get('/api/users')
        users.value = response.data
      } catch (error) {
        toast.error('Failed to fetch users')
        console.error('Error fetching users:', error)
      }
    }

    const promoteUser = async (userId) => {
      try {
        await axios.post(`/api/users/${userId}/promote`)
        toast.success('User promoted to admin')
        fetchUsers()
      } catch (error) {
        toast.error('Failed to promote user')
        console.error('Error promoting user:', error)
      }
    }

    const deleteUser = async (userId) => {
      if (!confirm('Are you sure you want to delete this user?')) return

      try {
        await axios.delete(`/api/users/${userId}`)
        toast.success('User deleted successfully')
        fetchUsers()
      } catch (error) {
        toast.error('Failed to delete user')
        console.error('Error deleting user:', error)
      }
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }

    // Fetch users on component mount
    fetchUsers()

    return {
      users,
      promoteUser,
      deleteUser,
      formatDate
    }
  }
}
</script> 