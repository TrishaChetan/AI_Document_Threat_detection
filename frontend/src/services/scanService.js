import api from "../api/api";

export const uploadScan = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post("/scan", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  return response.data;
};

export const getStatistics = async () => {
  const response = await api.get("/statistics");
  return response.data;
};

export const getHealth = async () => {
  const response = await api.get("/health");
  return response.data;
};

export const getApiInfo = async () => {
  const response = await api.get("/info");
  return response.data;
};

export const generateReport = async () => {
  const response = await api.post("/report");
  return response.data;
};
