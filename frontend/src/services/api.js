import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes — model loading + inference can be slow
})

/**
 * Analyze an uploaded file (PDF or image).
 * @param {File} file
 * @param {function} onUploadProgress - called with progress percentage 0-100
 * @returns {Promise<Object>} AnalysisResponse
 */
export async function analyzeFile(file, onUploadProgress) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await api.post('/analyze', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (event) => {
      if (onUploadProgress && event.total) {
        const percent = Math.round((event.loaded * 100) / event.total)
        onUploadProgress(percent)
      }
    },
  })

  return response.data
}

/**
 * Analyze raw text input.
 * @param {string} text
 * @returns {Promise<Object>} AnalysisResponse
 */
export async function analyzeText(text) {
  const response = await api.post('/analyze/text', { text })
  return response.data
}

/**
 * Health check.
 * @returns {Promise<Object>}
 */
export async function checkHealth() {
  const response = await api.get('/health')
  return response.data
}

export default api
