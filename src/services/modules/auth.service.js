import apiClient from '../apiClient';

export default {
    async login(username, password) {
        const response = await apiClient.post('/login', { username, password });
        return response.data;
    }
}
