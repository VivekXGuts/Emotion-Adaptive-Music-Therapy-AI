import React from 'react';
import { Scatter } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(LinearScale, PointElement, LineElement, Tooltip, Legend);

const EmotionChart = ({ valence, arousal, sessionActive }) => {
  const data = {
    datasets: [
      {
        label: 'Current Emotion',
        data: sessionActive ? [{ x: valence, y: arousal }] : [],
        backgroundColor: 'rgba(255, 99, 132, 1)',
        pointRadius: 10,
      },
    ],
  };

  const options = {
    scales: {
      x: {
        min: -1,
        max: 1,
        title: {
          display: true,
          text: 'Valence (Unpleasant ↔ Pleasant)',
          color: '#fff'
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
        ticks: { color: '#fff' }
      },
      y: {
        min: -1,
        max: 1,
        title: {
          display: true,
          text: 'Arousal (Calm ↔ Excited)',
          color: '#fff'
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
        ticks: { color: '#fff' }
      },
    },
    plugins: {
      legend: {
        display: false,
      },
    },
    maintainAspectRatio: false,
  };

  return (
    <div style={{ height: '300px', width: '100%', background: '#1e1e1e', padding: '10px', borderRadius: '10px' }}>
      <Scatter data={data} options={options} />
    </div>
  );
};

export default EmotionChart;
