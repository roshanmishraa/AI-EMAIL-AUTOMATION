import client from './axiosClient';
export const getSettings = () => client.get('/settings/');
export const updateSettings = (payload) => client.post('/settings/', payload);
