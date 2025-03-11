import React, { useState, useEffect } from 'react';
import axios from 'axios';

const DataFetcher = ({ authCode }) => {  
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (authCode) {
      console.log("🔹 Sending authCode to Flask:", authCode); // Log authCode before sending
  
      axios.post('http://localhost:3001/fetch-excel', { code: authCode })
        .then(response => {
          setData(response.data);
        })
        .catch(err => {
          console.error("🚨 Error fetching data:", err);
          setError('Error fetching data: ' + err.message);
        });
    } else {
      console.error("🚨 authCode is null! Not sending request to Flask.");
    }
  }, [authCode]);
  

  if (error) {
    return <div>{error}</div>;
  }

  if (!data) {
    return <div>No data available</div>;  
  }

  return (
    <div>
      <h2>Lessons Learned Data</h2>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
};

export default DataFetcher;
