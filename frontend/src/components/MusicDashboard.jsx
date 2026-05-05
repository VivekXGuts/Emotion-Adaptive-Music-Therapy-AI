import React, { useEffect, useState } from 'react';
import { Music, Play, FastForward, CheckCircle, Volume2, Info } from 'lucide-react';

// Emotion to Spotify Playlist Mapping
const SPOTIFY_PLAYLISTS = {
  anxious: "37i9dQZF1DWZqd5JICZI0u", // Calming Acoustic
  stressed: "37i9dQZF1DWZqd5JICZI0u",
  tense: "37i9dQZF1DWZqd5JICZI0u",
  angry: "37i9dQZF1DX1s9knjP51Oa", // Calm Down
  sad: "37i9dQZF1DX3rxVfibe1L0", // Mood Booster
  depressed: "37i9dQZF1DX3rxVfibe1L0",
  fatigued: "37i9dQZF1DX0b1hHYQtJso", // Energy Booster
  neutral: "37i9dQZF1DX8Uebhn9wzrS", // Chill Lofi
  alert: "37i9dQZF1DX8Uebhn9wzrS",
  happy: "37i9dQZF1DXdPec7aLTmlC", // Happy Hits
  elated: "37i9dQZF1DXdPec7aLTmlC",
  content: "37i9dQZF1DX889U0q85ZsJ", // Chill Vibes
  relaxed: "37i9dQZF1DX889U0q85ZsJ",
  calm: "37i9dQZF1DX889U0q85ZsJ"
};

const MusicDashboard = ({ params, customVideoId }) => {
  const [currentPlaylist, setCurrentPlaylist] = useState(null);
  const [youtubeLink, setYoutubeLink] = useState(null);

  useEffect(() => {
    if (params) {
      if (params.links) {
        if (params.links.spotify) {
          const playlistId = params.links.spotify.split('/').pop();
          if (playlistId !== currentPlaylist) setCurrentPlaylist(playlistId);
        }
        if (params.links.youtube) setYoutubeLink(params.links.youtube);
      } else if (params.label) {
        let emotionKey = params.label.split('_')[0].toLowerCase();
        const playlistId = SPOTIFY_PLAYLISTS[emotionKey] || SPOTIFY_PLAYLISTS["neutral"];
        if (playlistId !== currentPlaylist) {
          setCurrentPlaylist(playlistId);
        }
      }
    }
  }, [params, currentPlaylist]);

  if (!params) return null;

  const { tempo_bpm, scale, phase, label, instrument } = params;

  return (
    <div style={{ 
      background: 'rgba(30, 30, 30, 0.95)', 
      color: '#fff', 
      borderTop: '1px solid #333',
      padding: '10px 30px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      gap: '20px',
      backdropFilter: 'blur(10px)',
      boxShadow: '0 -5px 20px rgba(0,0,0,0.5)'
    }}>
      {/* Left: Phase & Label */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '15px', minWidth: '200px' }}>
        <div style={{ 
          width: '45px', 
          height: '45px', 
          borderRadius: '10px', 
          background: '#252526', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          border: '1px solid #444'
        }}>
          {phase === 'match' && <Play size={24} color="#4d94ff" />}
          {phase === 'guide' && <FastForward size={24} color="#ffcc00" />}
          {phase === 'target' && <CheckCircle size={24} color="#4dff4d" />}
        </div>
        <div>
          <div style={{ fontSize: '10px', color: '#888', textTransform: 'uppercase', letterSpacing: '1px' }}>Current Phase</div>
          <div style={{ fontWeight: 'bold', textTransform: 'uppercase', color: phase === 'match' ? '#4d94ff' : phase === 'guide' ? '#ffcc00' : '#4dff4d' }}>
            {phase} <span style={{ fontSize: '11px', color: '#666', marginLeft: '5px' }}>({label})</span>
          </div>
        </div>
      </div>

      {/* Center: Embed Player (Compact) */}
      <div style={{ flex: 1, maxWidth: '600px', height: '80px', borderRadius: '8px', overflow: 'hidden', border: '1px solid #333' }}>
        {customVideoId ? (
          <iframe 
            title="YouTube Player"
            width="100%" 
            height="80" 
            src={`https://www.youtube.com/embed/${customVideoId}?autoplay=1`} 
            frameBorder="0" 
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
          ></iframe>
        ) : currentPlaylist ? (
          <iframe 
            title="Spotify Player"
            src={`https://open.spotify.com/embed/playlist/${currentPlaylist}?utm_source=generator&theme=0`} 
            width="100%" 
            height="80" 
            frameBorder="0" 
            allowTransparency="true"
            allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" 
          ></iframe>
        ) : (
          <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#181818', color: '#444' }}>
            <Music size={20} style={{ marginRight: '10px' }} />
            Initializing adaptive therapy stream...
          </div>
        )}
      </div>

      {/* Right: Technical Details */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '20px', fontSize: '13px' }}>
        <div style={{ textAlign: 'right' }}>
          <div style={{ color: '#888', fontSize: '10px', textTransform: 'uppercase' }}>Tempo</div>
          <div style={{ fontWeight: '500' }}>{tempo_bpm.toFixed(1)} <span style={{ fontSize: '10px', color: '#666' }}>BPM</span></div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ color: '#888', fontSize: '10px', textTransform: 'uppercase' }}>Scale/Tone</div>
          <div style={{ fontWeight: '500', textTransform: 'capitalize' }}>{scale}</div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ color: '#888', fontSize: '10px', textTransform: 'uppercase' }}>Instrument</div>
          <div style={{ fontWeight: '500', textTransform: 'capitalize' }}>{instrument || 'Piano'}</div>
        </div>
        
        {youtubeLink && !customVideoId && (
          <a 
            href={youtubeLink} target="_blank" rel="noreferrer"
            style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '5px', 
              fontSize: '10px', 
              color: '#fff', 
              background: '#ff4d4d', 
              textDecoration: 'none', 
              padding: '6px 10px', 
              borderRadius: '6px',
              fontWeight: 'bold'
            }}
          >
            YOUTUBE
          </a>
        )}
      </div>
    </div>
  );
};

export default MusicDashboard;
