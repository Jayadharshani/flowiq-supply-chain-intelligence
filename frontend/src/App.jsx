
import { useState } from "react";
import "./App.css";
import Login from "./Login";
import PredictForm from "./PredictForm";
 
/*
  App.jsx is now just a "gatekeeper":
  - No token in state -> show Login
  - Token in state -> show PredictForm (the actual dashboard)
 
  The token lives in React state here (in memory) - it's the
  SINGLE source of truth for "am I logged in?" for the whole app.
  Note: this means refreshing the page logs you out, since React
  state resets on reload. That's expected for now - persisting
  login across refreshes (via localStorage) is a further
  improvement you can add later once this works.
*/
 
function App() {
  const [token, setToken] = useState(null);
 
  function handleLoginSuccess(newToken) {
    setToken(newToken);
  }
 
  function handleLogout() {
    setToken(null);
  }
 
  if (!token) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }
 
  return <PredictForm token={token} onLogout={handleLogout} />;
}
 
export default App;