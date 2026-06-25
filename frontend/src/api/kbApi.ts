// KB API calls
import client from './axiosClient'

export const getKBDocs     = ()             => client.get('/kb/')
export const uploadKBDoc   = (form: FormData) => client.post('/kb/upload', form)
export const deleteKBDoc   = (id: number)   => client.delete(`/kb/${id}`)
