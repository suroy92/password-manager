import { createBrowserRouter } from 'react-router-dom'
import AppLayout from './components/AppLayout'
import Setup from './pages/Setup'
import Unlock from './pages/Unlock'
import Vault from './pages/Vault'

const router = createBrowserRouter([
  { path: '/', element: <AppLayout />, children: [
    { index: true, element: <Unlock /> },
    { path: 'setup', element: <Setup /> },
    { path: 'vault', element: <Vault /> },
  ]}
])

export default router
