import React, { useState, useEffect } from 'react';
import './App.css';
import { useMsal, useIsAuthenticated } from '@azure/msal-react';

function AppContent() {
  const { instance } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  const [userInfo, setUserInfo] = useState(null);
  const [authToken, setAuthToken] = useState(null);
  const [data, setData] = useState([]); // Store fetched data

  const login = async () => {
    console.log("🔹 Login button clicked.");
    try {
      const response = await instance.loginPopup({
        scopes: ["User.Read", "Files.Read", "Sites.Read.All"], // ✅ Ensure correct scopes
      });

      console.log("✅ Login successful:", response);
      setUserInfo(response.account);

      // Acquire the user's access token
      const tokenResponse = await instance.acquireTokenSilent({
        scopes: ["Files.Read", "Sites.Read.All"],
        account: response.account,
      });

      console.log("🔹 Received User Auth Token:", tokenResponse.accessToken);
      setAuthToken(tokenResponse.accessToken);

      // ✅ Fetch data using the user's token
      fetchData(tokenResponse.accessToken);
    } catch (error) {
      console.error("🚨 Login failed:", error);
    }
  };

  const logout = () => {
    instance.logoutPopup();
    setUserInfo(null);
    setAuthToken(null);
    setData([]); // Clear data on logout
  };

  const fetchData = async (token) => {
    try {
      console.log("🔹 Fetching data with token:", token ? token.slice(0, 20) + "..." : "No token");
      const response = await fetch("http://localhost:3001/fetch-excel", {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${token}`, // ✅ Ensure this is included
        },
      });

      if (!response.ok) {
        throw new Error(`Server Error: ${response.statusText}`);
      }

      const jsonData = await response.json();
      console.log("✅ Data received:", jsonData);
      setData(jsonData);
    } catch (error) {
      console.error("🚨 Error fetching data:", error);
    }
  };

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
          {data.length > 0 ? (
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
            <p>Fetching data...</p>
          )}
        </div>
      )}
    </div>
  );
}

export default AppContent;