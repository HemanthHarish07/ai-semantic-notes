import React from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import NotesDashboard from './pages/NotesDashboard';
import CreateNotePage from './pages/CreateNotePage';
import SemanticSearchPage from './pages/SemanticSearchPage';
import AuthLayout from './components/AuthLayout';

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      <Route
        path="/"
        element={
          <AuthLayout>
            <NotesDashboard />
          </AuthLayout>
        }
      />
      <Route
        path="/notes/new"
        element={
          <AuthLayout>
            <CreateNotePage />
          </AuthLayout>
        }
      />
      <Route
        path="/semantic-search"
        element={
          <AuthLayout>
            <SemanticSearchPage />
          </AuthLayout>
        }
      />

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

