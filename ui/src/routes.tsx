import { createBrowserRouter } from 'react-router-dom'
import Layout from './pages/Layout'
import Unlock from './pages/Unlock'
import Vault from './pages/Vault'

export default createBrowserRouter([
  { path: '/', element: <Layout />, children: [
    { index: true, element: <Unlock /> },
    { path: 'vault', element: <Vault /> }
  ]},
])
