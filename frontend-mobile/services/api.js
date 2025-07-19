import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:3000', // Change to your backend URL
});

export async function uploadAudio(uri) {
  const formData = new FormData();
  formData.append('file', {
    uri,
    name: 'recording.m4a',
    type: 'audio/m4a',
  });

  return api.post('/audio', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
}
