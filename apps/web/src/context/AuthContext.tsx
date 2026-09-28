import React, { createContext, useContext, useState, useEffect } from 'react';
import type { User, LoginResponse } from '../types';
import { apiRequest } from '../services/api';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  quickLogin: (role: 'Admin' | 'Branch Manager' | 'Analyst') => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem('mmi_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [token, setToken] = useState<string | null>(() => {
    return localStorage.getItem('mmi_auth_token');
  });
  const [isLoading, setIsLoading] = useState<boolean>(false);

  useEffect(() => {
    const handleUnauthorized = () => {
      setUser(null);
      setToken(null);
    };
    window.addEventListener('mmi_auth_unauthorized', handleUnauthorized);
    return () => window.removeEventListener('mmi_auth_unauthorized', handleUnauthorized);
  }, []);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const data = await apiRequest<LoginResponse>('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      });
      setToken(data.access_token);
      setUser(data.user);
      localStorage.setItem('mmi_auth_token', data.access_token);
      localStorage.setItem('mmi_user', JSON.stringify(data.user));
    } finally {
      setIsLoading(false);
    }
  };

  const quickLogin = async (role: 'Admin' | 'Branch Manager' | 'Analyst') => {
    let email = 'admin@mmi-demo.com';
    if (role === 'Branch Manager') email = 'manager@mmi-demo.com';
    if (role === 'Analyst') email = 'analyst@mmi-demo.com';
    await login(email, 'Demo@12345');
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('mmi_auth_token');
    localStorage.removeItem('mmi_user');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!user && !!token,
        isLoading,
        login,
        quickLogin,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
};
