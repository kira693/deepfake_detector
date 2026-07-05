import axios from 'axios';

// Set your backend IP in mobile/.env as: EXPO_PUBLIC_API_URL=http://YOUR_IP:8000/api/v1
const BASE_URL = process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    'ngrok-skip-browser-warning': 'true',
  },
});


export const detectImage = async (imageUri: string, filename: string) => {
  const formData = new FormData();
  formData.append('file', {
    uri: imageUri,
    name: filename,
    type: 'image/jpeg',
  } as any);
  const response = await api.post('/detect/image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const detectDeepfake = async (imageUri: string, filename: string) => {
  const formData = new FormData();
  formData.append('file', {
    uri: imageUri,
    name: filename,
    type: 'image/jpeg',
  } as any);
  const response = await api.post('/detect/deepfake', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const detectVideo = async (videoUri: string, filename: string) => {
  const formData = new FormData();
  formData.append('file', {
    uri: videoUri,
    name: filename,
    type: 'video/mp4',
  } as any);
  const response = await api.post('/detect/video', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};  