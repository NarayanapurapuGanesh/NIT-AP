'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';

export interface UserProfile {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  department: string;
  academicRole: string;
  password?: string;
  accessToken?: string;
}

interface RegisterData {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  department: string;
  academicRole: string;
}

interface LoginData {
  email: string;
  password: string;
}

interface UpdateProfileData {
  firstName: string;
  lastName: string;
  currentPassword?: string;
  newPassword?: string;
}

interface AuthContextType {
  user: UserProfile | null;
  loading: boolean;
  register: (data: RegisterData) => Promise<{ success: boolean; error?: string }>;
  login: (data: LoginData) => Promise<{ success: boolean; error?: string }>;
  updateProfile: (data: UpdateProfileData) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const USERS_DB_KEY = 'facultyiq_users_db';
const CURRENT_USER_KEY = 'facultyiq_current_user';

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  // Initialize from LocalStorage
  useEffect(() => {
    try {
      const storedUser = localStorage.getItem(CURRENT_USER_KEY);
      if (storedUser) {
        setUser(JSON.parse(storedUser));
      }
    } catch {
      // Ignore storage parse error
    } finally {
      setLoading(false);
    }
  }, []);

  const getUsersFromDb = (): UserProfile[] => {
    try {
      const data = localStorage.getItem(USERS_DB_KEY);
      return data ? JSON.parse(data) : [];
    } catch {
      return [];
    }
  };

  const saveUsersToDb = (users: UserProfile[]) => {
    try {
      localStorage.setItem(USERS_DB_KEY, JSON.stringify(users));
    } catch {
      // Ignore storage write error
    }
  };

  const register = async (data: RegisterData): Promise<{ success: boolean; error?: string }> => {
    const users = getUsersFromDb();
    const normalizedEmail = data.email.trim().toLowerCase();

    // 1. Check local DB duplicate email
    const existing = users.find((u) => u.email.toLowerCase() === normalizedEmail);
    if (existing) {
      return {
        success: false,
        error: 'An account with this email address already exists. Please sign in instead.',
      };
    }

    // 2. Attempt backend API call if reachable
    let backendToken: string | undefined;
    try {
      const res = await fetch('https://localhost:7150/api/v1/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: normalizedEmail,
          password: data.password,
          firstName: data.firstName,
          lastName: data.lastName,
          roleName: data.academicRole,
        }),
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => null);
        if (res.status === 409 || errorData?.error?.includes('exists')) {
          return {
            success: false,
            error: 'An account with this email address already exists. Please sign in instead.',
          };
        }
      } else {
        const apiResult = await res.json();
        backendToken = apiResult.accessToken;
      }
    } catch {
      // Backend offline: proceed with local database storage
    }

    // 3. Save new user account
    const newUser: UserProfile = {
      id: `usr_${Date.now()}`,
      email: normalizedEmail,
      firstName: data.firstName.trim(),
      lastName: data.lastName.trim(),
      department: data.department || 'Computer Science & Engineering',
      academicRole: data.academicRole || 'Assistant Professor',
      password: data.password,
      accessToken: backendToken,
    };

    users.push(newUser);
    saveUsersToDb(users);

    // Save as logged-in session user
    const sessionUser = { ...newUser };
    delete sessionUser.password;
    localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(sessionUser));
    setUser(sessionUser);

    return { success: true };
  };

  const login = async (data: LoginData): Promise<{ success: boolean; error?: string }> => {
    const normalizedEmail = data.email.trim().toLowerCase();
    const users = getUsersFromDb();

    // Attempt backend API login if available
    let backendUser: UserProfile | null = null;
    try {
      const res = await fetch('https://localhost:7150/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: normalizedEmail, password: data.password }),
      });

      if (res.ok) {
        const apiData = await res.json();
        backendUser = {
          id: apiData.user.id,
          email: apiData.user.email,
          firstName: apiData.user.firstName,
          lastName: apiData.user.lastName,
          department: 'Computer Science & Engineering',
          academicRole: apiData.user.roles?.[0] || 'Faculty Member',
          accessToken: apiData.accessToken,
        };
      }
    } catch {
      // Backend offline fallback
    }

    if (backendUser) {
      localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(backendUser));
      setUser(backendUser);
      return { success: true };
    }

    // Fallback to local user DB validation
    const existing = users.find((u) => u.email.toLowerCase() === normalizedEmail);
    if (!existing || existing.password !== data.password) {
      return {
        success: false,
        error: 'Invalid email or password. Please check your credentials and try again.',
      };
    }

    const sessionUser = { ...existing };
    delete sessionUser.password;
    localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(sessionUser));
    setUser(sessionUser);

    return { success: true };
  };

  const updateProfile = async (data: UpdateProfileData): Promise<{ success: boolean; error?: string }> => {
    if (!user) return { success: false, error: 'Not authenticated' };

    const users = getUsersFromDb();
    const userIndex = users.findIndex((u) => u.email.toLowerCase() === user.email.toLowerCase());

    // Password validation if password change is requested
    if (data.newPassword) {
      if (!data.currentPassword) {
        return { success: false, error: 'Please enter your current password to update password.' };
      }
      if (userIndex !== -1 && users[userIndex].password && users[userIndex].password !== data.currentPassword) {
        return { success: false, error: 'Current password does not match our records.' };
      }
    }

    // Call backend profile update API if token exists
    if (user.accessToken) {
      try {
        await fetch('https://localhost:7150/api/v1/auth/profile', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${user.accessToken}`,
          },
          body: JSON.stringify({ firstName: data.firstName, lastName: data.lastName }),
        }).catch(() => null);

        if (data.newPassword && data.currentPassword) {
          await fetch('https://localhost:7150/api/v1/auth/change-password', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${user.accessToken}`,
            },
            body: JSON.stringify({
              currentPassword: data.currentPassword,
              newPassword: data.newPassword,
            }),
          }).catch(() => null);
        }
      } catch {
        // Backend offline
      }
    }

    // Update in local database
    if (userIndex !== -1) {
      users[userIndex].firstName = data.firstName;
      users[userIndex].lastName = data.lastName;
      if (data.newPassword) {
        users[userIndex].password = data.newPassword;
      }
      saveUsersToDb(users);
    }

    const updatedUser: UserProfile = {
      ...user,
      firstName: data.firstName,
      lastName: data.lastName,
    };

    localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(updatedUser));
    setUser(updatedUser);

    return { success: true };
  };

  const logout = () => {
    localStorage.removeItem(CURRENT_USER_KEY);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, register, login, updateProfile, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
