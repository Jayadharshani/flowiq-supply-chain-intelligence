import { useState } from "react";

// Vite exposes environment variables prefixed with VITE_ via
// import.meta.env. On Vercel, we'll set VITE_API_BASE to the live
// Render URL. Locally (npm run dev), no such variable exists, so it
// falls back to your own machine's backend - same pattern as
// DATABASE_URL/SECRET_KEY on the backend.
const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

/*
  This component handles BOTH login and registration in one form,
  toggled by `isRegistering`. It doesn't hold the token itself -
  it calls `onLoginSuccess(token)` and lets the PARENT (App.jsx)
  decide what to do with it. This keeps Login "dumb" and reusable -
  it only knows how to talk to the API, not what happens after.
*/

function Login({ onLoginSuccess }) {
  const [isRegistering, setIsRegistering] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  async function handleLogin(e) {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      // /login expects form-encoded data (username=...&password=...),
      // NOT JSON - this matches OAuth2PasswordRequestForm on the
      // backend, same as the "Try it out" form you tested in /docs.
      const body = new URLSearchParams();
      body.append("username", username);
      body.append("password", password);

      const response = await fetch(`${API_BASE}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body,
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || "Login failed");
      }

      const data = await response.json();
      onLoginSuccess(data.access_token);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleRegister(e) {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || "Registration failed");
      }

      // After successful registration, log them in immediately
      // instead of making them submit the form twice.
      await handleLogin(e);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  }

  return (
    <div className="login-container">
      <div className="login-card">
        <h1>FlowIQ</h1>
        <p className="subtitle">Supply Chain Delay Prediction</p>

        <form onSubmit={isRegistering ? handleRegister : handleLogin}>
          <label>
            Username
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </label>

          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </label>

          {error && <p className="error">{error}</p>}

          <button type="submit" disabled={loading}>
            {loading ? "Please wait..." : isRegistering ? "Register" : "Login"}
          </button>
        </form>

        <p className="toggle-text">
          {isRegistering ? "Already have an account?" : "Don't have an account?"}{" "}
          <button
            type="button"
            className="link-btn"
            onClick={() => {
              setIsRegistering(!isRegistering);
              setError(null);
            }}
          >
            {isRegistering ? "Login" : "Register"}
          </button>
        </p>
      </div>
    </div>
  );
}

export default Login;