import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import { apiService } from "../services/api";
import { enhancedApiService } from "../services/enhancedApi";

interface User {
  id: number;
  username: string;
  email?: string;
  is_active: boolean;
  created_at: string;
}

interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  login: (userData: any) => void;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // Initialize auth state from localStorage
  useEffect(() => {
    const initializeAuth = async () => {
      const storedToken = localStorage.getItem("auth_token");

      if (storedToken) {
        setToken(storedToken);
        apiService.setToken(storedToken);
        enhancedApiService.setToken(storedToken);

        // Verify token with backend
        try {
          const result = await apiService.getCurrentUser();
          if (result.data && !result.error) {
            setUser(result.data);
            setIsAuthenticated(true);
          } else {
            // Token is invalid, clear it
            localStorage.removeItem("auth_token");
            apiService.clearToken();
            enhancedApiService.clearToken();
            setToken(null);
          }
        } catch (error) {
          console.error("Auth verification error:", error);
          localStorage.removeItem("auth_token");
          apiService.clearToken();
          enhancedApiService.clearToken();
          setToken(null);
        }
      }

      setLoading(false);
    };

    initializeAuth();
  }, []);

  const login = (userData: any) => {
    setUser(userData.user || userData);
    setToken(userData.access_token || userData.token);
    setIsAuthenticated(true);

    // Store token in both API services
    if (userData.access_token) {
      apiService.setToken(userData.access_token);
      enhancedApiService.setToken(userData.access_token);
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    setIsAuthenticated(false);
    localStorage.removeItem("auth_token");
    apiService.clearToken();
    enhancedApiService.clearToken();
  };

  const value: AuthContextType = {
    isAuthenticated,
    user,
    token,
    login,
    logout,
    loading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
