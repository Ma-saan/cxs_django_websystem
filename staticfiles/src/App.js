import React, { useState, useEffect } from 'react';
import './App.css';
import CalendarView from './components/CalendarView';
import { fetchWorkCenters } from './api/scheduleApi';

function App() {
  const [workCenters, setWorkCenters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // ワークセンターデータの取得
  useEffect(() => {
    const loadWorkCenters = async () => {
      try {
        setLoading(true);
        const data = await fetchWorkCenters();
        setWorkCenters(data);
        setError(null);
      } catch (err) {
        console.error('ワークセンター取得エラー:', err);
        setError('データ取得中にエラーが発生しました。');
      } finally {
        setLoading(false);
      }
    };

    loadWorkCenters();
  }, []);

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>生産予定管理</h1>
      </header>
      
      <main className="app-content">
        {loading && <div className="loading">データ読み込み中...</div>}
        {error && <div className="error">{error}</div>}
        {!loading && !error && (
          <CalendarView workCenters={workCenters} />
        )}
      </main>
      
      <footer className="app-footer">
        <p>掛川工場充填課管理システム © {new Date().getFullYear()}</p>
      </footer>
    </div>
  );
}

export default App;