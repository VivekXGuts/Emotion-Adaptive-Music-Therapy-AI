import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from './Constants';

import EmotionChart from './components/EmotionChart';
import LiveStats from './components/LiveStats';
import MusicDashboard from './components/MusicDashboard';
import SessionControls from './components/SessionControls';

import { Activity, ShieldCheck, Zap } from 'lucide-react';

function App() {
  const [fusedState, setFusedState] = useState(null);
  const [musicParams, setMusicParams] = useState(null);
  const [session, setSession] = useState({ active: false });
  const [rppg, setRppg] = useState({ bpm: null });
  const [customVideoId, setCustomVideoId] = useState(null);
  const [healthInfo, setHealthInfo] = useState({ mock_mode: false });

  const fetchHealth = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/health`);
      setHealthInfo(res.data);
    } catch (err) {
      console.error("Fetch Health Error:", err);
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  const fetchStatus = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/session/status`);
      setFusedState(res.data.emotion);
      setMusicParams(res.data.music);
      setSession(res.data.session);
    } catch (err) {
      console.error("Fetch Status Error:", err);
    }
  };

  const fetchRppg = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/analyze/rppg`);
      setRppg(res.data);
    } catch (err) {
      console.error("Fetch RPPG Error:", err);
    }
  };

  useEffect(() => {
    const interval = setInterval(() => {
      fetchStatus();
      fetchRppg();
      
      if (session.active) {
        axios.post(`${API_BASE_URL}/analyze/facial`).catch(() => {});
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [session.active]);

  return (
    <div className="App" style={{ 
      background: '#0a0a0a', 
      minHeight: '100vh', 
      color: '#fff', 
      padding: '20px 20px 120px 20px', 
      fontFamily: 'Inter, system-ui, sans-serif' 
    }}>
      
      {/* Header */}
      <header style={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between',
        marginBottom: '30px', 
        borderBottom: '1px solid #222', 
        paddingBottom: '20px' 
      }}>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <div style={{ 
            background: 'linear-gradient(135deg, #4d94ff, #8866ff)', 
            padding: '8px', 
            borderRadius: '12px', 
            marginRight: '15px',
            boxShadow: '0 4px 15px rgba(77, 148, 255, 0.3)'
          }}>
            <Activity size={28} color="#fff" />
          </div>
          <div>
            <h1 style={{ margin: 0, fontSize: '24px', fontWeight: '800', letterSpacing: '-0.5px' }}>EAMTA <span style={{ color: '#4d94ff', fontWeight: '400' }}>AI</span></h1>
            <p style={{ margin: 0, fontSize: '12px', color: '#666', fontWeight: '500' }}>Emotion-Adaptive Music Therapy AI System</p>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '15px' }}>
          <div style={{ display: 'flex', alignItems: 'center', background: '#1a1a1a', padding: '6px 12px', borderRadius: '20px', border: '1px solid #333' }}>
            <Zap size={14} color="#ffcc00" style={{ marginRight: '6px' }} />
            <span style={{ fontSize: '10px', color: '#888', fontWeight: 'bold' }}>SYSTEM STABLE</span>
          </div>
        </div>
      </header>

      {/* Main Grid */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', 
        gap: '25px',
        width: '100%',
        maxWidth: '1400px',
        margin: '0 auto'
      }}>
        
        {/* Left Column: Emotion & Biometrics */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '25px' }}>
          <div style={{ background: '#111', padding: '20px', borderRadius: '16px', border: '1px solid #222' }}>
            <h4 style={{ margin: '0 0 20px 0', color: '#444', textTransform: 'uppercase', fontSize: '11px', fontWeight: 'bold', letterSpacing: '1.5px' }}>Biometric Fusion Analysis</h4>
            <EmotionChart 
              valence={fusedState?.valence || 0} 
              arousal={fusedState?.arousal || 0} 
              sessionActive={session.active}
            />
          </div>
          
          <div style={{ background: '#111', padding: '20px', borderRadius: '16px', border: '1px solid #222' }}>
            <h4 style={{ margin: '0 0 20px 0', color: '#444', textTransform: 'uppercase', fontSize: '11px', fontWeight: 'bold', letterSpacing: '1.5px' }}>Real-time Modality Stats</h4>
            <LiveStats 
              bpm={rppg?.bpm} 
              label={fusedState?.emotion_label}
              weights={fusedState?.weights_used}
              confidence={fusedState?.confidence || 0}
              sessionActive={session.active}
            />
          </div>
        </div>

        {/* Right Column: Session Controls */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '25px' }}>
          <div style={{ background: '#111', padding: '20px', borderRadius: '16px', border: '1px solid #222', flex: 1 }}>
            <h4 style={{ margin: '0 0 20px 0', color: '#444', textTransform: 'uppercase', fontSize: '11px', fontWeight: 'bold', letterSpacing: '1.5px' }}>Clinical Session Management</h4>
            <SessionControls 
              onStatusUpdate={fetchStatus} 
              sessionActive={session.active} 
              onSongSelect={setCustomVideoId}
            />
          </div>

          <div style={{ 
            background: 'linear-gradient(145deg, #161616, #0d0d0d)', 
            padding: '25px', 
            borderRadius: '16px', 
            border: '1px solid #222',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
            textAlign: 'center',
            minHeight: '150px'
          }}>
            {!session.active ? (
              <>
                <div style={{ color: '#444', marginBottom: '10px' }}><Activity size={32} /></div>
                <p style={{ margin: 0, fontSize: '14px', color: '#666', maxWidth: '250px' }}>
                  Awaiting session start to begin biometric adaptive music generation.
                </p>
              </>
            ) : (
              <>
                <div style={{ color: '#4d94ff', marginBottom: '10px' }}><Zap size={32} className="animate-pulse" /></div>
                <p style={{ margin: 0, fontSize: '14px', color: '#00ff88', fontWeight: 'bold' }}>
                  ACTIVE SESSION: MONITORING BIOMETRICS
                </p>
              </>
            )}
          </div>
        </div>

      </div>

      {/* Bottom Fixed Player Dashboard */}
      {session.active && (
        <div style={{ 
          position: 'fixed', 
          bottom: 0, 
          left: 0, 
          right: 0, 
          zIndex: 1000 
        }}>
          <MusicDashboard params={musicParams} customVideoId={customVideoId} />
        </div>
      )}

      {/* Footer / Status Bar */}
      <footer style={{ marginTop: '40px', fontSize: '10px', color: '#333', textAlign: 'center' }}>
        EAMTA PRO v2.4 | Mac M4 | React 19 | Flask Biometrics | {new Date().toLocaleDateString()}
      </footer>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
        .animate-pulse {
          animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
      `}</style>

    </div>
  );
}

export default App;
