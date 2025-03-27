// schedule_manager/static/src/App.js
import React, { useState, useEffect } from 'react';

function App() {
  const [scheduleData, setScheduleData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // APIからデータ取得
    const fetchData = async () => {
      try {
        const response = await fetch('/schedule_manager/api/schedules/');
        if (response.ok) {
          const data = await response.json();
          setScheduleData(data);
        } else {
          console.error('APIからのデータ取得に失敗:', response.status);
        }
      } catch (error) {
        console.error('データ取得エラー:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="schedule-manager">
      <h1>生産予定管理システム</h1>
      {loading ? (
        <p>データを読み込み中...</p>
      ) : (
        <div className="schedule-data">
          {scheduleData.length > 0 ? (
            <ul>
              {scheduleData.map(item => (
                <li key={item.id}>
                  {item.production_date}: {item.product_name}
                </li>
              ))}
            </ul>
          ) : (
            <p>表示するデータがありません</p>
          )}
        </div>
      )}
    </div>
  );
}

export default App;