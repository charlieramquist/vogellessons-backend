import React, { useState, useEffect } from 'react';
import './App.css';
import { useMsal } from '@azure/msal-react';

function AppContent() {
  const { instance } = useMsal();
  const accounts = instance.getAllAccounts();
  const isAuthenticated = accounts && accounts.length > 0;

  const [userInfo, setUserInfo] = useState(null);
  const [authToken, setAuthToken] = useState(null);
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Manual login
  const login = async () => {
    console.log("🔹 Login button clicked.");
    try {
      const response = await instance.loginPopup({
        scopes: ["User.Read", "Files.Read", "Sites.Read.All"],
      });

      console.log("✅ Login successful:", response);
      setUserInfo(response.account);

      const tokenResponse = await instance.acquireTokenSilent({
        scopes: ["Files.Read", "Sites.Read.All"],
        account: response.account,
      });

      console.log("🔹 Received User Auth Token:", tokenResponse.accessToken);
      setAuthToken(tokenResponse.accessToken);
    } catch (error) {
      console.error("🚨 Login failed:", error);
    }
  };

  // Logout
  const logout = () => {
    instance.logoutPopup();
    setUserInfo(null);
    setAuthToken(null);
    setData([]);
    setError(null);
  };

  // Reacquire token on page reload
  useEffect(() => {
    const restoreSession = async () => {
      if (isAuthenticated && !authToken && accounts.length > 0) {
        try {
          const tokenResponse = await instance.acquireTokenSilent({
            scopes: ["Files.Read", "Sites.Read.All"],
            account: accounts[0],
          });
          console.log("🔄 Token re-acquired on reload:", tokenResponse.accessToken);
          setUserInfo(accounts[0]);
          setAuthToken(tokenResponse.accessToken);
        } catch (err) {
          console.error("🚨 Failed to re-acquire token on reload:", err);
        }
      }
    };

    restoreSession();
  }, [isAuthenticated, authToken]);

  // Fetch Excel data
  const fetchData = async (token) => {
    setLoading(true);
    setError(null);

    try {
      console.log("🔹 Fetching data with token:", token ? token.slice(0, 20) + "..." : "No token");

      const response = await fetch("https://vogellessons-backend.onrender.com/fetch-excel", {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Server Error: ${response.statusText}`);
      }

      const jsonData = await response.json();
      console.log("✅ Data received:", jsonData);
      setData(Array.isArray(jsonData) ? jsonData : []);
    } catch (error) {
      console.error("🚨 Error fetching data:", error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  // Fetch data once token is ready
  useEffect(() => {
    if (isAuthenticated && authToken && data.length === 0 && !loading) {
      fetchData(authToken);
    }
  }, [isAuthenticated, authToken]);

  return (
    <div className="App">
      {!isAuthenticated ? (
        <div className="login-container">
          <div className="login-box">
            <h1>Lessons Learned Website</h1>
            <button className="login-button" onClick={login}>
              Login with Microsoft
            </button>
          </div>
        </div>
      ) : (
        <div className="content-container">
          <p>Welcome, {userInfo?.name || userInfo?.username || "User"}</p>
          <button onClick={logout}>Logout</button>

          {loading ? (
            <p>Fetching data...</p>
          ) : error ? (
            <p style={{ color: 'red' }}>Error fetching data: {error}</p>
          ) : data.length > 0 ? (
            <table border="1">
              <thead>
                <tr>
                  {Object.keys(data[0]).map((key) => (
                    <th key={key}>{key}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.map((row, index) => (
                  <tr key={index}>
                    {Object.values(row).map((value, i) => (
                      <td key={i}>{String(value)}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p>No data available.</p>
          )}
        </div>
      )}
    </div>
  );
}

export default AppContent;
