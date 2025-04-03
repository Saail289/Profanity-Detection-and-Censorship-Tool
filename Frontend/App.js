import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [threshold, setThreshold] = useState(0.6);
  const [profaneWords, setProfaneWords] = useState([]);
  const [audioUrl, setAudioUrl] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  // Cleanup audio URL on unmount to prevent memory leaks
  useEffect(() => {
    return () => {
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
    };
  }, [audioUrl]);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setError(null); // Clear any previous errors when a new file is selected
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a video file before submitting.');
      return;
    }

    setLoading(true);
    setError(null);
    setProfaneWords([]);
    setAudioUrl(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('threshold', threshold);

    try {
      const response = await axios.post('http://localhost:8000/process-video/', formData, {
        timeout: 300000, // 5 minutes timeout
        responseType: 'json', // Expect JSON response
      });

      // Access audio and profane_words directly from response.data (already parsed JSON)
      const { audio, profane_words } = response.data;
      
      // Decode the audio bytes (latin1-encoded string) to a Blob
      const audioBytes = new Uint8Array([...audio].map(char => char.charCodeAt(0))); // Convert latin1 string to bytes
      const audioBlob = new Blob([audioBytes], { type: 'audio/wav' });
      setAudioUrl(URL.createObjectURL(audioBlob));
      setProfaneWords(profane_words || []);
    } catch (error) {
      console.error('Error processing video:', error);
      setError(`Failed to process video: ${error.message || 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <h1>Video Profanity Beeper</h1>
      <form onSubmit={handleSubmit}>
        <input 
          type="file" 
          accept="video/mp4"  // Restrict to .mp4 for compatibility with moviepy/whisper
          onChange={handleFileChange} 
        />
        <label>
          Profanity Threshold (0-1):
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={threshold}
            onChange={(e) => setThreshold(parseFloat(e.target.value))}
          />
          {threshold}
        </label>
        <button type="submit" disabled={loading}>
          {loading ? 'Processing...' : 'Process Video'}
        </button>
      </form>

      {error && (
        <div style={{ color: 'red', marginTop: '10px' }}>
          <p>Error: {error}</p>
        </div>
      )}

      {loading && (
        <div style={{ marginTop: '10px' }}>
          <p>Loading...</p>
        </div>
      )}

      {profaneWords.length > 0 && (
        <div style={{ marginTop: '20px' }}>
          <h3>Beeped Words:</h3>
          <ul>
            {profaneWords.map((word, i) => (
              <li key={i}>{word}</li>
            ))}
          </ul>
        </div>
      )}

      {audioUrl && (
        <div style={{ marginTop: '20px' }}>
          <h3>Beeped Audio:</h3>
          <audio controls src={audioUrl}></audio>
          <a 
            href={audioUrl} 
            download="beeped_audio.wav" 
            style={{ display: 'block', marginTop: '10px', color: 'blue', textDecoration: 'underline' }}
          >
            Download Beeped Audio
          </a>
        </div>
      )}
    </div>
  );
}

export default App;