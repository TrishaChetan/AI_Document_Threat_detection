import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 60000,
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error(error);

    if (error.response) {
      return Promise.reject(error.response.data);
    }

    return Promise.reject({
      detail: "Unable to connect to backend.",
    });
  },
);

export const getStatistics = async () => {
  const response = await api.get("/statistics");
  return response.data.statistics;
};

export const getHistory = async () => {
  const response = await api.get("/history");
  return response.data.history;
};

export const getScan = async (scanId) => {
  const response = await api.get(`/scan/${scanId}`);
  return response.data.scan;
};

export default api;
