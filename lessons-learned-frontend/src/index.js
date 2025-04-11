import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import AppContent from './App';
import { PublicClientApplication } from '@azure/msal-browser';
import { MsalProvider } from '@azure/msal-react';
import { msalConfig } from './authConfig';

// ✅ Create MSAL instance
const msalInstance = new PublicClientApplication(msalConfig);

// ✅ Create root element
const rootElement = document.getElementById('root');
const root = ReactDOM.createRoot(rootElement);

// ✅ Wait for MSAL to initialize before rendering the app
msalInstance.initialize().then(() => {
  root.render(
    <React.StrictMode>
      <MsalProvider instance={msalInstance}>
        <AppContent />
      </MsalProvider>
    </React.StrictMode>
  );
}).catch((error) => {
  console.error("🚨 MSAL Initialization Error:", error);
});
