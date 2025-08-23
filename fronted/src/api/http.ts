// src/api/http.ts
import axios from "axios";

// 后端默认 http://localhost:8000
const baseURL = (import.meta as any).env?.VITE_API_BASE || "http://localhost:8000";

const http = axios.create({
  baseURL,
  timeout: 15000,
});

export default http;