import { createContext, useContext, useEffect, useState } from "react";
import { api } from "../api/client";

type User = {
  id: string;
  name: string;
  email: string;
  avatarUrl?: string;
};

type AuthContextType = {
  user: User | null;
  isReady: boolean;
  googleEnabled: boolean;
  loginWithGoogle: () => Promise<void>;
  loginWithEmail: (email: string, password: string) => Promise<void>;
  signupWithEmail: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  openLogin: () => void;
  openSignup: () => void;
  closeModals: () => void;
  isLoginOpen: boolean;
  isSignupOpen: boolean;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isReady, setIsReady] = useState(false);
  const [googleEnabled, setGoogleEnabled] = useState(false);
  const [isLoginOpen, setIsLoginOpen] = useState(false);
  const [isSignupOpen, setIsSignupOpen] = useState(false);

  useEffect(() => {
    const hydrate = async () => {
      try {
        const providers = await api.post("/auth/providers");
        setGoogleEnabled(Boolean(providers.data?.google_enabled));
      } catch {
        setGoogleEnabled(false);
      }

      const raw = localStorage.getItem("bimba3d:user");
      if (raw) {
        try {
          setUser(JSON.parse(raw));
        } catch {
          localStorage.removeItem("bimba3d:user");
        }
      }
      const accessToken = localStorage.getItem("bimba3d:accessToken");
      if (accessToken) {
        try {
          const me = await api.get("/auth/me", {
            headers: { Authorization: `Bearer ${accessToken}` },
          });
          const payload = me.data;
          const hydratedUser: User = {
            id: payload.id,
            name: payload.name,
            email: payload.email,
          };
          setUser(hydratedUser);
          localStorage.setItem("bimba3d:user", JSON.stringify(hydratedUser));
        } catch {
          localStorage.removeItem("bimba3d:accessToken");
          localStorage.removeItem("bimba3d:refreshToken");
          localStorage.removeItem("bimba3d:user");
          setUser(null);
        }
      }
      setIsReady(true);
    };

    hydrate();
  }, []);

  const setAuthSession = (payload: any) => {
    localStorage.setItem("bimba3d:accessToken", payload.access_token);
    localStorage.setItem("bimba3d:refreshToken", payload.refresh_token);
    const nextUser: User = {
      id: payload.user.id,
      name: payload.user.name,
      email: payload.user.email,
    };
    setUser(nextUser);
    localStorage.setItem("bimba3d:user", JSON.stringify(nextUser));
  };

  const loginWithEmail = async (email: string, password: string) => {
    const res = await api.post("/auth/login", { email, password });
    setAuthSession(res.data);
    setIsSignupOpen(false);
    setIsLoginOpen(false);
  };

  const signupWithEmail = async (name: string, email: string, password: string) => {
    const res = await api.post("/auth/signup", { name, email, password });
    setAuthSession(res.data);
    setIsSignupOpen(false);
    setIsLoginOpen(false);
  };

  const loginWithGoogle = async () => {
    const origin = window.location.origin;
    const start = await api.get("/auth/google/start", { params: { origin } });
    const authUrl = start.data?.authorization_url as string | undefined;
    if (!authUrl) {
      throw new Error("Google OAuth is not available");
    }

    const width = 520;
    const height = 680;
    const left = window.screenX + Math.max(0, (window.outerWidth - width) / 2);
    const top = window.screenY + Math.max(0, (window.outerHeight - height) / 2);
    const popup = window.open(
      authUrl,
      "bimba3d-google-login",
      `popup=yes,width=${width},height=${height},left=${left},top=${top}`
    );

    if (!popup) {
      throw new Error("Popup blocked. Please allow popups and try again.");
    }

    const apiOrigin = new URL(api.defaults.baseURL || window.location.origin).origin;

    await new Promise<void>((resolve, reject) => {
      const timer = window.setInterval(() => {
        if (popup.closed) {
          window.clearInterval(timer);
          window.removeEventListener("message", onMessage);
          reject(new Error("Google sign-in was closed before completion."));
        }
      }, 300);

      const onMessage = (event: MessageEvent) => {
        if (event.origin !== apiOrigin) return;
        const data = event.data;
        if (!data || typeof data !== "object") return;
        if (data.type === "bimba3d-google-auth-success") {
          window.clearInterval(timer);
          window.removeEventListener("message", onMessage);
          setAuthSession(data.payload);
          setIsSignupOpen(false);
          setIsLoginOpen(false);
          try { popup.close(); } catch {}
          resolve();
          return;
        }
        if (data.type === "bimba3d-google-auth-failure") {
          window.clearInterval(timer);
          window.removeEventListener("message", onMessage);
          try { popup.close(); } catch {}
          reject(new Error(data.payload?.error || "Google sign-in failed"));
        }
      };

      window.addEventListener("message", onMessage);
    });
  };

  const logout = () => {
    const refreshToken = localStorage.getItem("bimba3d:refreshToken");
    if (refreshToken) {
      api.post("/auth/logout", { refresh_token: refreshToken }).catch(() => undefined);
    }
    setUser(null);
    localStorage.removeItem("bimba3d:accessToken");
    localStorage.removeItem("bimba3d:refreshToken");
    localStorage.removeItem("bimba3d:user");
  };

  const openLogin = () => {
    setIsSignupOpen(false);
    setIsLoginOpen(true);
  };
  const openSignup = () => {
    setIsLoginOpen(false);
    setIsSignupOpen(true);
  };
  const closeModals = () => { setIsLoginOpen(false); setIsSignupOpen(false); };

  return (
    <AuthContext.Provider value={{ user, isReady, googleEnabled, loginWithGoogle, loginWithEmail, signupWithEmail, logout, openLogin, openSignup, closeModals, isLoginOpen, isSignupOpen }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
