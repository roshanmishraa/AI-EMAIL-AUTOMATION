// Email API calls
import client from './axiosClient'

export const getEmails = (params?: object) => client.get('/emails/', { params })
export const getEmail  = (id: number)       => client.get(`/emails/${id}`)
export const approveReply = (id: number, body: object) => client.post(`/emails/${id}/reply`, body)
export const escalateEmail = (id: number)   => client.post(`/emails/${id}/escalate`)
