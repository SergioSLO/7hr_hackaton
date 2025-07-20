import axios from 'axios';

const api = axios.create({
  baseURL: 'http://132.191.1.161:8000',
});

export async function uploadAudio(uri) {
  const formData = new FormData();
  formData.append('file', {
    uri,
    name: 'recording.m4a',
    type: 'audio/m4a',
  });
  console.log(formData);

  const response = await api.post('/audio', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });

  console.log(response);
  return response;
}

export async function fetchTransactions(weekStart) {
  try {
    const response = await api.get('/movimientos', {
      params: { weekStart },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching transactions', error);
    throw error;
  }
}
