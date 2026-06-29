import client from './axiosClient';
export const getDashboard = () => client.get('/analytics/dashboard');
