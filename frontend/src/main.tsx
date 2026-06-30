// ============================================================
// FILE:  frontend/src/main.tsx
// CHANGE: QueryClient ko inline banane ki jagah lib/queryClient.ts
//         se import karta hai — taaki authStore.ts bhi usi instance
//         ko access kar sake (logout pe cache clear karne ke liye)
// ============================================================
import ReactDOM from 'react-dom/client'
import { QueryClientProvider } from '@tanstack/react-query'
import App from './App'
import './index.css'
import { queryClient } from './lib/queryClient'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <QueryClientProvider client={queryClient}>
    <App />
  </QueryClientProvider>
)