<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Reset your password
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Enter the verification code sent to {{ email }} and your new password.
        </p>
      </div>
      
      <form class="mt-8 space-y-6" @submit.prevent="handleResetPassword">
        <div class="space-y-4">
          <div>
            <label for="verification-code" class="sr-only">Verification Code</label>
            <input
              id="verification-code"
              v-model="verificationCode"
              name="verification_code"
              type="text"
              maxlength="6"
              required
              class="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm text-center text-lg tracking-widest"
              placeholder="000000"
            />
          </div>
          
          <div>
            <label for="new-password" class="sr-only">New Password</label>
            <input
              id="new-password"
              v-model="newPassword"
              name="new_password"
              type="password"
              autocomplete="new-password"
              required
              class="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
              placeholder="New password"
            />
          </div>
          
          <div>
            <label for="confirm-password" class="sr-only">Confirm Password</label>
            <input
              id="confirm-password"
              v-model="confirmPassword"
              name="confirm_password"
              type="password"
              autocomplete="new-password"
              required
              class="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
              placeholder="Confirm new password"
            />
          </div>
        </div>

        <div v-if="error" class="text-red-600 text-sm text-center">
          {{ error }}
        </div>

        <div v-if="success" class="text-green-600 text-sm text-center">
          {{ success }}
        </div>

        <div>
          <button
            type="submit"
            :disabled="loading"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="loading" class="absolute left-0 inset-y-0 flex items-center pl-3">
              <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </span>
            {{ loading ? 'Resetting...' : 'Reset Password' }}
          </button>
        </div>

        <div class="text-center space-y-2">
          <div>
            <button
              type="button"
              @click="resendCode"
              :disabled="resendLoading"
              class="text-blue-600 hover:text-blue-500 disabled:opacity-50"
            >
              {{ resendLoading ? 'Sending...' : 'Resend code' }}
            </button>
          </div>
          <div>
            <router-link to="/login" class="font-medium text-blue-600 hover:text-blue-500">
              Back to login
            </router-link>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useToast } from 'vue-toastification'
import { passwordResetAPI } from '@/services/api'

const router = useRouter()
const route = useRoute()
const toast = useToast()

const email = computed(() => route.params.email || '')
const verificationCode = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const resendLoading = ref(false)
const error = ref('')
const success = ref('')

const handleResetPassword = async () => {
  if (!verificationCode.value || !newPassword.value || !confirmPassword.value) {
    error.value = 'Please fill in all fields'
    return
  }

  if (newPassword.value !== confirmPassword.value) {
    error.value = 'Passwords do not match'
    return
  }

  if (newPassword.value.length < 8) {
    error.value = 'Password must be at least 8 characters long'
    return
  }

  loading.value = true
  error.value = ''
  success.value = ''

  try {
    const response = await passwordResetAPI.confirmReset(
      email.value,
      verificationCode.value,
      newPassword.value,
      confirmPassword.value
    )
    
    success.value = response.data.message
    toast.success('Password reset successfully!')
    
    // Navigate to login page
    setTimeout(() => {
      router.push('/login')
    }, 2000)
    
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to reset password'
    toast.error(error.value)
  } finally {
    loading.value = false
  }
}

const resendCode = async () => {
  if (!email.value) {
    error.value = 'Email address is required'
    return
  }

  resendLoading.value = true
  error.value = ''

  try {
    await passwordResetAPI.requestReset(email.value)
    toast.success('Reset code resent! Check your email.')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to resend code'
    toast.error(error.value)
  } finally {
    resendLoading.value = false
  }
}
</script>
