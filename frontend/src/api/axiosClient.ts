import axios from 'axios'

const client = axios.create({
  baseURL: '/api/v1',
  headers: {
    'X-API-Key': import.meta.env.VITE_API_KEY ?? 'supersecret-change-me',
  },
})

export default client
