import { useState } from "react";
import { Loader2, LogIn, Mail, UserPlus, X } from "lucide-react";
import { useAuth } from "../../context/AuthContext";

export default function LoginModal() {
  const { isLoginOpen, isSignupOpen, googleEnabled, closeModals, loginWithGoogle, loginWithEmail, signupWithEmail, openSignup, openLogin } = useAuth();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isOpen = isLoginOpen || isSignupOpen;
  const mode = isSignupOpen ? "signup" : "login";

  if (!isOpen) return null;

  const resetState = () => {
    setName("");
    setEmail("");
    setPassword("");
    setSubmitting(false);
    setError(null);
  };

  const closeAll = () => {
    resetState();
    closeModals();
  };

  const submit = async (kind: "login" | "signup" | "google") => {
    setSubmitting(true);
    setError(null);
    try {
      if (kind === "signup") {
        await signupWithEmail(name.trim(), email.trim(), password);
      } else if (kind === "google") {
        await loginWithGoogle();
      } else {
        await loginWithEmail(email.trim(), password);
      }
      resetState();
      closeModals();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Authentication failed");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50">
      <div className="absolute inset-0 bg-black/60" onClick={closeAll} />
      <div className="absolute inset-0 flex items-center justify-center p-4">
        <div className="w-full max-w-md bg-white rounded-xl shadow-2xl border border-slate-200 overflow-hidden">
          <div className="flex items-center justify-between px-4 py-3 border-b border-slate-200">
            <h3 className="text-base font-semibold text-slate-900">{mode === "signup" ? "Create account" : "Login"}</h3>
            <button className="p-2 rounded-lg hover:bg-slate-100" onClick={closeAll}>
              <X className="w-5 h-5 text-slate-700" />
            </button>
          </div>

          <div className="px-4 pt-4 flex gap-2">
            <button
              className={`flex-1 px-3 py-2 rounded-lg text-sm font-medium border ${mode === "login" ? "border-blue-300 bg-blue-50 text-blue-700" : "border-slate-300 text-slate-600 hover:bg-slate-50"}`}
              onClick={() => {
                openLogin();
                setError(null);
              }}
            >
              Login
            </button>
            <button
              className={`flex-1 px-3 py-2 rounded-lg text-sm font-medium border ${mode === "signup" ? "border-blue-300 bg-blue-50 text-blue-700" : "border-slate-300 text-slate-600 hover:bg-slate-50"}`}
              onClick={() => {
                openSignup();
                setError(null);
              }}
            >
              Sign Up
            </button>
          </div>

          <div className="px-4 py-4 space-y-3">
            {mode === "signup" && (
              <div className="space-y-1.5">
                <label className="text-sm font-medium text-slate-700">Full name</label>
                <input
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500/30"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Your name"
                  maxLength={120}
                  disabled={submitting}
                />
              </div>
            )}

            <div className="space-y-1.5">
              <label className="text-sm font-medium text-slate-700">Email</label>
              <input
                type="email"
                className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500/30"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@gmail.com"
                disabled={submitting}
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium text-slate-700">Password</label>
              <input
                type="password"
                className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500/30"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="At least 8 characters"
                disabled={submitting}
              />
            </div>

            {error && <div className="rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</div>}

            <div className="grid grid-cols-1 gap-2 pt-1">
              {mode === "signup" ? (
                <button
                  className="w-full inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-60"
                  onClick={() => submit("signup")}
                  disabled={submitting || !name.trim() || !email.trim() || password.length < 8}
                >
                  {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <UserPlus className="w-4 h-4" />}
                  Create Account
                </button>
              ) : (
                <>
                  <button
                    className="w-full inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-60"
                    onClick={() => submit("login")}
                    disabled={submitting || !email.trim() || password.length < 8}
                  >
                    {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <LogIn className="w-4 h-4" />}
                    Login
                  </button>
                  {googleEnabled && (
                    <button
                      className="w-full inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg border border-slate-300 hover:bg-slate-50 disabled:opacity-60"
                      onClick={() => submit("google")}
                      disabled={submitting}
                    >
                      <Mail className="w-4 h-4" />
                      Continue with Google
                    </button>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
