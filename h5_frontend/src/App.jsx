import { Routes, Route, Navigate } from 'react-router-dom';
import Auth from './pages/Auth';
import Home from './pages/Home';
import './App.css';

function PrivateRoute({ children }) {
  const token = localStorage.getItem('h5_token');
  return token ? children : <Navigate to="/auth" />;
}

function App() {
  return (
    <Routes>
      <Route path="/auth" element={<Auth />} />
      <Route
        path="/"
        element={
          <PrivateRoute>
            <Home />
          </PrivateRoute>
        }
      />
    </Routes>
  );
}

export default App;
