import client from './axiosClient'

export const getSettings = () => client.get('/settings/')

export const updateSettings = (payload: {
  auto_send_mode?: boolean
  escalation_confidence_threshold?: number
  polling_interval_seconds?: number
}) => client.post('/settings/', payload)