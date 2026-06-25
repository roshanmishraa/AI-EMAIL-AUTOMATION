import client from './axiosClient'

export interface EmailFilterParams {
  status?: string
  category?: string
  sentiment?: string
  skip?: number
  limit?: number
}

export const getEmails = (params?: EmailFilterParams) =>
  client.get('/emails/', { params })

export const getEmail = (id: number) =>
  client.get(`/emails/${id}`)

export const approveReply = (id: number) =>
  client.post(`/emails/${id}/reply`, {})

export const escalateEmail = (id: number) =>
  client.post(`/emails/${id}/escalate`)

export const processEmail = (id: number) =>
  client.post(`/emails/${id}/process`)

export const triggerFetch = () =>
  client.post('/emails/trigger-fetch')