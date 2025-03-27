// schedule_manager/static/src/index.js
import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import './styles.css';

document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('schedule-manager-app');
  if (container) {
    const root = createRoot(container);
    root.render(<App />);
  }
});