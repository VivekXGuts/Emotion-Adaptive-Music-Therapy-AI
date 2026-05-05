import React from 'react';
import { Heart, Activity, Target, Zap } from 'lucide-react';

const LiveStats = ({ bpm, label, weights, confidence, sessionActive }) => {
  return (
    <div className="stats-container" style={{ padding: '20px', background: '#252526', color: '#fff', borderRadius: '12px' }}>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        
        {/* BPM Card */}
        <div style={{ background: '#1e1e1e', padding: '15px', borderRadius: '8px', textAlign: 'center' }}>
          <Heart color="#ff4d4d" size={32} style={{ marginBottom: '5px' }} />
          <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{sessionActive && bpm ? bpm : '--'} BPM</div>
          <div style={{ fontSize: '12px', color: '#888' }}>Live Heart Rate (rPPG)</div>
        </div>

        {/* Emotion Card */}
        <div style={{ background: '#1e1e1e', padding: '15px', borderRadius: '8px', textAlign: 'center' }}>
          <Activity color="#4d94ff" size={32} style={{ marginBottom: '5px' }} />
          <div style={{ fontSize: '24px', fontWeight: 'bold', textTransform: 'capitalize' }}>{sessionActive && label ? label : '--'}</div>
          <div style={{ fontSize: '12px', color: '#888' }}>Detected Mood</div>
        </div>

        {/* Confidence Card */}
        <div style={{ background: '#1e1e1e', padding: '15px', borderRadius: '8px', textAlign: 'center' }}>
          <Target color="#4dff4d" size={32} style={{ marginBottom: '5px' }} />
          <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{sessionActive ? (confidence * 100).toFixed(0) : '0'}%</div>
          <div style={{ fontSize: '12px', color: '#888' }}>Fusion Confidence</div>
        </div>

        {/* Weights Card */}
        <div style={{ background: '#1e1e1e', padding: '15px', borderRadius: '8px' }}>
          <div style={{ fontSize: '12px', color: '#888', marginBottom: '10px', textAlign: 'center' }}>
            <Zap size={16} style={{ verticalAlign: 'middle', marginRight: '5px' }} />
            Modality Weights
          </div>
          {Object.entries(weights || {}).map(([mod, weight]) => (
            <div key={mod} style={{ marginBottom: '5px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px' }}>
                <span style={{ textTransform: 'capitalize' }}>{mod}</span>
                <span>{(weight * 100).toFixed(0)}%</span>
              </div>
              <div style={{ background: '#333', height: '4px', borderRadius: '2px', marginTop: '2px' }}>
                <div style={{ background: '#4d94ff', height: '100%', width: `${weight * 100}%`, borderRadius: '2px' }}></div>
              </div>
            </div>
          ))}
        </div>

      </div>
    </div>
  );
};

export default LiveStats;
