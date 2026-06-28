/// <reference types="vite/client" />
import axios from 'axios'


const client = axios.create({
  baseURL: '/api/v1',
  headers: {
    'X-API-Key': import.meta.env.VITE_API_KEY ?? 'supersecret-change-me',
  },
})

client.interceptors.response.use(
  res => res,
  err => {
    console.error('[API Error]', err.response?.status, err.response?.data)
    return Promise.reject(err)
  }
)

export default client
