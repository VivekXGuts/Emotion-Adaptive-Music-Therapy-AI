import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../Constants';
import { Play, Square, Mic, MicOff, Heart, Camera } from 'lucide-react';

const speak = (text) => {
  window.speechSynthesis.cancel();
  const utter = new SpeechSynthesisUtterance(text);
  utter.rate = 0.95; // Slightly slower for better clarity
  utter.pitch = 1.0; // Natural pitch prevents audio resampling/cracking
  utter.volume = 1;
  const voices = window.speechSynthesis.getVoices();
  // Prefer premium built-in voices that don't crack
  const preferred = voices.find(v => v.name.includes('Samantha') || v.name.includes('Google US English') || v.name.includes('Daniel') || v.name.includes('Karen'));
  if (preferred) utter.voice = preferred;

  // Prevent garbage collection bug in Chrome which stops onend from firing
  window._currentUtterance = utter;

  window.speechSynthesis.speak(utter);
  return utter;
};

const MOOD_SONGS = {
  sad: [
    { title: "Fix You", id: "k4V3Mo61fJM" },
    { title: "Someone Like You", id: "hLQl3WQQoQ0" },
    { title: "Breathe Me", id: "ghPcYqn0p4Y" }
  ],
  depressed: [
    { title: "Fix You", id: "k4V3Mo61fJM" },
    { title: "Someone Like You", id: "hLQl3WQQoQ0" },
    { title: "Breathe Me", id: "ghPcYqn0p4Y" }
  ],
  stressed: [
    { title: "Roar", id: "CevxZvSJLk8" },
    { title: "Shake It Off", id: "nfWlot6h_JM" },
    { title: "Stronger", id: "Xn676-fLq7I" }
  ],
  tense: [
    { title: "Roar", id: "CevxZvSJLk8" },
    { title: "Shake It Off", id: "nfWlot6h_JM" },
    { title: "Stronger", id: "Xn676-fLq7I" }
  ],
  angry: [
    { title: "Roar", id: "CevxZvSJLk8" },
    { title: "Shake It Off", id: "nfWlot6h_JM" },
    { title: "Stronger", id: "Xn676-fLq7I" }
  ],
  happy: [
    { title: "Happy", id: "ZbZSe6N_BXs" },
    { title: "Walking On Sunshine", id: "iPUmE-tne5U" },
    { title: "Good Vibrations", id: "Eab_beh07HU" }
  ],
  elated: [
    { title: "Happy", id: "ZbZSe6N_BXs" },
    { title: "Walking On Sunshine", id: "iPUmE-tne5U" },
    { title: "Good Vibrations", id: "Eab_beh07HU" }
  ],
  calm: [
    { title: "Weightless", id: "UfcAVejslrU" },
    { title: "Sunset Lover", id: "WUcjxaRmVpM" },
    { title: "Clair de Lune", id: "CvFH_6DNRCY" }
  ],
  relaxed: [
    { title: "Weightless", id: "UfcAVejslrU" },
    { title: "Sunset Lover", id: "WUcjxaRmVpM" },
    { title: "Clair de Lune", id: "CvFH_6DNRCY" }
  ],
  neutral: [
    { title: "Weightless", id: "UfcAVejslrU" },
    { title: "Sunset Lover", id: "WUcjxaRmVpM" },
    { title: "Clair de Lune", id: "CvFH_6DNRCY" }
  ],
  anxious: [
    { title: "Weightless", id: "UfcAVejslrU" },
    { title: "Sunset Lover", id: "WUcjxaRmVpM" },
    { title: "Clair de Lune", id: "CvFH_6DNRCY" }
  ],
  fatigued: [
    { title: "Happy", id: "ZbZSe6N_BXs" },
    { title: "Walking On Sunshine", id: "iPUmE-tne5U" },
    { title: "Good Vibrations", id: "Eab_beh07HU" }
  ],
  alert: [
    { title: "Weightless", id: "UfcAVejslrU" },
    { title: "Sunset Lover", id: "WUcjxaRmVpM" },
    { title: "Clair de Lune", id: "CvFH_6DNRCY" }
  ],
  content: [
    { title: "Weightless", id: "UfcAVejslrU" },
    { title: "Sunset Lover", id: "WUcjxaRmVpM" },
    { title: "Clair de Lune", id: "CvFH_6DNRCY" }
  ]
};

const SessionControls = ({ onStatusUpdate, sessionActive, onEmotionDetected, onSongSelect }) => {
  const [userId, setUserId] = useState('Arya');
  const [feedback, setFeedback] = useState(3);
  const [isListening, setIsListening] = useState(false);
  const [spokenText, setSpokenText] = useState('');
  const [statusMsg, setStatusMsg] = useState('');
  const [isCameraOn, setIsCameraOn] = useState(false);
  
  const interactionPhaseRef = useRef('mood');
  const currentEmotionRef = useRef('neutral');

  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const recognitionRef = useRef(null);
  const canvasRef = useRef(null);

  // Load voices
  useEffect(() => {
    window.speechSynthesis.getVoices();
    window.speechSynthesis.onvoiceschanged = () => window.speechSynthesis.getVoices();
  }, []);

  // Start webcam
  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      streamRef.current = stream;
      if (videoRef.current) videoRef.current.srcObject = stream;
      setIsCameraOn(true);
    } catch (err) {
      setStatusMsg('Camera access denied. Check browser permissions.');
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(t => t.stop());
      streamRef.current = null;
    }
    setIsCameraOn(false);
  };

  // Capture frame and send to backend
  const captureAndAnalyzeFace = async () => {
    if (!videoRef.current || !canvasRef.current) return;
    const canvas = canvasRef.current;
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(videoRef.current, 0, 0);
    const base64 = canvas.toDataURL('image/jpeg', 0.8);
    try {
      await axios.post(`${API_BASE_URL}/analyze/facial`, { image: base64 });
      onStatusUpdate();
    } catch (err) {
      console.error('Face analysis error:', err);
    }
  };

  // Voice recognition
  const startListening = (phase = 'mood') => {
    interactionPhaseRef.current = phase;
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setStatusMsg('Voice not supported in this browser. Use Chrome.');
      return;
    }
    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    recognitionRef.current = recognition;
    recognition.onstart = () => {
      setIsListening(true);
      setStatusMsg(phase === 'mood' ? 'Listening... speak your mood' : 'Listening... pick a song');
    };
    recognition.onresult = async (event) => {
      const transcript = event.results[0][0].transcript;
      setSpokenText(transcript);
      setStatusMsg(`You said: "${transcript}"`);
      if (recognitionRef.current) recognitionRef.current.stop();
      setIsListening(false);
      
      if (interactionPhaseRef.current === 'mood') {
        try {
          const res = await axios.post(`${API_BASE_URL}/analyze/text`, { text: transcript });
          onStatusUpdate();
          
          const emotion = res.data.fused_state?.emotion_label || 'neutral';
          currentEmotionRef.current = emotion;
          
          const songs = MOOD_SONGS[emotion] || MOOD_SONGS['neutral'];
          
          // Join song names naturally: "Song A, Song B, or Song C"
          const songNames = songs.length > 1 
            ? `${songs.slice(0, -1).map(s => s.title).join(', ')}, or ${songs[songs.length - 1].title}`
            : songs[0].title;
          
          const utter = speak(`Got it. Based on your mood, I have curated a playlist. Would you like to hear ${songNames}?`);
          
          utter.onend = () => {
            setTimeout(() => {
              startListening('song');
            }, 500);
          };
        } catch (err) {
          console.error('Voice analysis error:', err);
        }
      } else if (interactionPhaseRef.current === 'song') {
        const emotion = currentEmotionRef.current;
        const songs = MOOD_SONGS[emotion] || MOOD_SONGS['neutral'];
        const text = transcript.toLowerCase();
        
        // Find the best matching song
        const chosenSong = songs.find(s => text.includes(s.title.toLowerCase()));
        
        // Keywords for 'your choice'
        const isUserAskingForChoice = ["choice", "choose", "best", "you pick", "anything", "whatever", "suggest"].some(kw => text.includes(kw));

        if (chosenSong) {
          speak(`Great choice. Playing ${chosenSong.title} for you now.`);
          if (onSongSelect) onSongSelect(chosenSong.id);
        } else if (isUserAskingForChoice) {
          speak(`Okay, I'll play the best one for you. Starting ${songs[0].title}.`);
          if (onSongSelect) onSongSelect(songs[0].id);
        } else {
          // Fallback if not recognized
          speak(`Okay, I'll play ${songs[0].title} for you.`);
          if (onSongSelect) onSongSelect(songs[0].id);
        }
      }
    };
    recognition.onerror = (e) => {
      if (recognitionRef.current) recognitionRef.current.stop();
      setIsListening(false);
      setStatusMsg(`Voice error: ${e.error}. Try again.`);
    };
    recognition.onend = () => {
      setIsListening(false);
    };
    recognition.start();
  };

  const stopListening = () => {
    if (recognitionRef.current) recognitionRef.current.stop();
    setIsListening(false);
  };

  const startSession = async () => {
    try {
      if (onSongSelect) onSongSelect(null); // Reset song
      await axios.post(`${API_BASE_URL}/session/start`, {
        user_id: userId,
        initial_emotion: 'neutral'
      });
      onStatusUpdate();
      await startCamera();
      
      setStatusMsg(`Session started for ${userId}`);
      
      // Full Voice Flow (Alexa style)
      setTimeout(() => {
        const utter = speak(`Hi ${userId}, how are you feeling today?`);
        utter.onend = () => {
          setTimeout(() => {
            startListening('mood');
          }, 500);
        };
      }, 500);

    } catch (err) {
      console.error('Start error:', err);
      setStatusMsg('Failed to start session. Check backend.');
    }
  };

  const stopSession = async () => {
    try {
      await axios.post(`${API_BASE_URL}/session/feedback`, { rating: feedback });
      onStatusUpdate();
      stopCamera();
      speak(`Thank you ${userId}. Your therapy session is complete. I hope you feel better!`);
      setStatusMsg('Session ended. Thank you!');
      setSpokenText('');
    } catch (err) {
      console.error('Stop error:', err);
    }
  };

  // Auto capture face every 5 seconds when session active
  useEffect(() => {
    if (!sessionActive || !isCameraOn) return;
    const interval = setInterval(captureAndAnalyzeFace, 5000);
    return () => clearInterval(interval);
  }, [sessionActive, isCameraOn]);

  return (
    <div style={{ padding: '20px', background: '#252526', color: '#fff', borderRadius: '12px' }}>

      {/* User + Start/Stop */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
        <div>
          <label style={{ fontSize: '12px', color: '#888', display: 'block' }}>Your Name</label>
          <input
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            disabled={sessionActive}
            style={{ background: '#1e1e1e', border: '1px solid #333', color: '#fff', padding: '6px 10px', borderRadius: '6px', fontSize: '14px' }}
          />
        </div>
        <button
          onClick={sessionActive ? stopSession : startSession}
          style={{
            background: sessionActive ? '#ff4d4d' : '#4d94ff',
            color: '#fff', border: 'none', padding: '10px 20px',
            borderRadius: '8px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px'
          }}
        >
          {sessionActive ? <Square size={16} /> : <Play size={16} />}
          {sessionActive ? 'End Session' : 'Start Session'}
        </button>
      </div>

      {/* Status message */}
      {statusMsg && (
        <div style={{ background: '#1a1a2e', border: '1px solid #4d94ff', borderRadius: '8px', padding: '10px', marginBottom: '15px', fontSize: '13px', color: '#4d94ff' }}>
          {statusMsg}
        </div>
      )}

      {/* Live webcam feed */}
      {sessionActive && (
        <div style={{ marginBottom: '20px', position: 'relative' }}>
          <label style={{ fontSize: '12px', color: '#888', display: 'block', marginBottom: '8px' }}>
            <Camera size={14} style={{ verticalAlign: 'middle', marginRight: '5px' }} />
            Live Face Scan
          </label>
          <video
            ref={videoRef}
            autoPlay
            muted
            playsInline
            style={{ width: '100%', borderRadius: '8px', border: '1px solid #333', maxHeight: '180px', objectFit: 'cover' }}
          />
          <canvas ref={canvasRef} style={{ display: 'none' }} />
          <div style={{
            position: 'absolute', top: '30px', right: '8px',
            background: isCameraOn ? '#4dff4d' : '#ff4d4d',
            borderRadius: '50%', width: '10px', height: '10px'
          }} />
        </div>
      )}

      <hr style={{ border: 'none', borderTop: '1px solid #333', margin: '15px 0' }} />

      {/* Voice Input */}
      <div style={{ marginBottom: '20px' }}>
        <label style={{ fontSize: '12px', color: '#888', display: 'block', marginBottom: '8px' }}>
          <Mic size={14} style={{ verticalAlign: 'middle', marginRight: '5px' }} />
          Voice Input
        </label>
        <button
          onClick={isListening ? stopListening : startListening}
          style={{
            width: '100%', padding: '12px',
            background: isListening ? 'rgba(255,77,77,0.15)' : 'rgba(77,148,255,0.15)',
            border: `1px solid ${isListening ? '#ff4d4d' : '#4d94ff'}`,
            color: isListening ? '#ff4d4d' : '#4d94ff',
            borderRadius: '8px', cursor: 'pointer', display: 'flex',
            alignItems: 'center', justifyContent: 'center', gap: '10px', fontSize: '14px'
          }}
        >
          {isListening ? <MicOff size={18} /> : <Mic size={18} />}
          {isListening ? 'Listening... (tap to stop)' : 'Tap to speak how you feel'}
        </button>
        {spokenText && (
          <div style={{ marginTop: '8px', fontSize: '12px', color: '#aaa', fontStyle: 'italic' }}>
            "{spokenText}"
          </div>
        )}
      </div>

      {/* Feedback slider */}
      {sessionActive && (
        <div style={{ background: 'rgba(77,255,77,0.05)', padding: '15px', borderRadius: '8px', border: '1px solid rgba(77,255,77,0.2)' }}>
          <label style={{ fontSize: '12px', color: '#4dff4d', display: 'block', marginBottom: '10px' }}>
            <Heart size={14} style={{ verticalAlign: 'middle', marginRight: '5px' }} />
            How do you feel? (1=Worse, 5=Better)
          </label>
          <input
            type="range" min="1" max="5"
            value={feedback}
            onChange={(e) => setFeedback(parseInt(e.target.value))}
            style={{ width: '100%', cursor: 'pointer' }}
          />
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', marginTop: '5px' }}>
            <span>Worse</span><span>Same</span><span>Better</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default SessionControls;