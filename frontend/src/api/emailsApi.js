import client from './axiosClient';
export const getEmails = (params) => client.get('/emails/', { params });
export const getEmail = (id) => client.get(`/emails/${id}`);
export const approveReply = (id) => client.post(`/emails/${id}/reply`, {});
export const escalateEmail = (id) => client.post(`/emails/${id}/escalate`);
// NEW: human review complete → escalation resolve karta hai
export const resolveEscalation = (id, notes) => client.post(`/emails/${id}/resolve-escalation`, null, {
    params: notes ? { notes } : undefined,
});
export const processEmail = (id) => client.post(`/emails/${id}/process`);
export const triggerFetch = () => client.post('/emails/trigger-fetch');
