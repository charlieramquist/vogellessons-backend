export const msalConfig = {
    auth: {
      clientId: "97cf4bca-47da-4bee-9c9e-703a5220af77", // Replace with your actual Client ID
      authority: "https://login.microsoftonline.com/14479aac-eea4-4daa-be4d-3e48dadcfab7", // Common authority for Microsoft accounts
      redirectUri: "http://localhost:3000", // Change to your redirect URI if different
    },
    cache: {
      cacheLocation: "localStorage", // Store tokens in localStorage for persistence
      storeAuthStateInCookie: true, // Set this to true for Internet Explorer support
    },
  };
  