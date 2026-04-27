import { useState, useEffect } from "react";
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import { getMerchantId, clearMerchantCookie } from "./lib/cookies";

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  // check cookie on mount — auto-redirect if already logged in
  useEffect(() => {
    if (getMerchantId()) setIsLoggedIn(true);
  }, []);

  const handleLogin = () => setIsLoggedIn(true);

  const handleLogout = () => {
    clearMerchantCookie();
    setIsLoggedIn(false);
  };

  return isLoggedIn ? (
    <DashboardPage onLogout={handleLogout} />
  ) : (
    <LoginPage onLogin={handleLogin} />
  );
}
