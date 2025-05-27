import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  // State to track toggle status and room URL
  const [isToggled, setIsToggled] = useState(false);
  const [roomUrl, setRoomUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Toggle handler function
  const handleToggle = () => {
    setIsToggled(!isToggled);
  };

  // Function to fetch room URL from our Python backend
  const fetchRoomUrl = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // This calls our Python backend instead of directly calling the Simli API
      const response = await fetch("http://localhost:8000/api/room-url", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });
      
      if (!response.ok) {
        throw new Error(`API request failed with status: ${response.status}`);
      }
      
      const data = await response.json();
      setRoomUrl(data.roomUrl);
    } catch (err) {
      setError(err.message || 'Failed to fetch room URL');
      console.error('Error fetching room URL:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch room URL when the component mounts
  useEffect(() => {
    fetchRoomUrl();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">

        
        {/* Room Content Section with iframe */}
        <div className="bg-white rounded-xl shadow-lg overflow-hidden mb-8">
          <div className="p-6">
            <h2 className="text-xl font-semibold text-gray-700 mb-4">
              Room Content
            </h2>
            
            {isLoading ? (
              <div className="flex justify-center py-8">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
              </div>
            ) : error ? (
              <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-4">
                <p className="text-red-700">{error}</p>
              </div>
            ) : roomUrl ? (
              <div>
                <div className="relative pt-[56.25%] w-full bg-gray-100 rounded-lg overflow-hidden">
                  <iframe 
                    src={roomUrl} 
                    title="Room Content"
                    className="absolute top-0 left-0 w-full h-full"
                    sandbox="allow-same-origin allow-scripts allow-popups allow-forms allow-popups-to-escape-sandbox"
                    allow="camera; microphone; display-capture; autoplay; clipboard-write"
                    loading="lazy"
                  ></iframe>
                </div>
                
                <div className="mt-3 bg-amber-50 border border-amber-200 p-3 rounded-md">
                  <p className="text-amber-700 text-sm flex items-center">
                    <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                    Check your browser permissions if camera or mic isn't working
                  </p>
                </div>
              </div>
            ) : null}
            
            <div className="mt-4">
              <button 
                onClick={fetchRoomUrl} 
                className="flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                </svg>
                Refresh Room
              </button>
            </div>
          </div>
        </div>
      
        </div>
      </div>
  );
}

export default App;