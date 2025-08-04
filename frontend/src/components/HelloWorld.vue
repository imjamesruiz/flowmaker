<script setup>
import { onMounted } from 'vue'
import axios from 'axios'

onMounted(() => {
  axios.get('http://localhost:8000/api/ping')
    .then(res => console.log(res.data))
    .catch(err => console.error('API error:', err))
})
</script>

<template>
  <div class="text-xl font-semibold text-blue-600">
    Check the browser console for backend response.
  </div>
</template>
