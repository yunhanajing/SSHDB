import axios from 'axios'

const request = axios.create({
  // Keep API URLs relative: Vite proxies them locally, Nginx proxies them in production.
  baseURL: '',
  timeout: 300000,
})

export default request
