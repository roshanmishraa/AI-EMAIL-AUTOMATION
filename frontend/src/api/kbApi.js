// ============================================================
// FILE:  frontend/src/api/kbApi.ts
// CHANGE: fetchChunksForEmail() function add kiya
// ============================================================
import client from './axiosClient';
export const getKBDocs = () => client.get('/kb/');
export const uploadKBDoc = (form) => client.post('/kb/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
});
export const deleteKBDoc = (id) => client.delete(`/kb/${id}`);
export const fetchChunksForEmail = (emailId) => client.get(`/kb/preview?email_id=${emailId}`);
