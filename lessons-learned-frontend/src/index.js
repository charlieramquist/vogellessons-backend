import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import { PublicClientApplication } from "@azure/msal-browser";
import { MsalProvider } from "@azure/msal-react";
import { msalConfig } from "./authConfig";

// ✅ Create MSAL instance
const msalInstance = new PublicClientApplication(msalConfig);

msalInstance.initialize().then(() => {
    console.log("✅ MSAL Initialized Successfully");

    const rootElement = document.getElementById('root');
    if (!rootElement) {
        console.error("🚨 Root element not found! Ensure <div id='root'></div> exists in index.html.");
        return;
    }

    const root = ReactDOM.createRoot(rootElement);
    root.render(
        <React.StrictMode>
            <MsalProvider instance={msalInstance}>
                <App />
            </MsalProvider>
        </React.StrictMode>
    );
}).catch(error => {
    console.error("🚨 MSAL Initialization Error:", error);
});
