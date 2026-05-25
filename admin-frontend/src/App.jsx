import { AuthProvider, useAuth } from './contexts/AuthContext';
import Layout from './layouts/Layout';
import LoginPage from './pages/LoginPage';

function AppShell() {
  const { isAuthenticated, isAdmin } = useAuth();
  if (!isAuthenticated) return <LoginPage />;
  if (!isAdmin) return <LoginPage />;
  return <Layout />;
}

function App() {
  return (
    <AuthProvider>
      <AppShell />
    </AuthProvider>
  );
}

export default App;
