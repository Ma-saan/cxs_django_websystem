import React, { useState, useEffect } from 'react';
import './DayScheduleView.css';
import { fetchSchedulesByDate } from '../api/scheduleApi';

const DayScheduleView = ({ date, onClose, workCenterColors }) => {
  const [schedules, setSchedules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // 日付のフォーマット
  const formatDate = (date) => {
    const d = new Date(date);
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    const weekdays = ['日', '月', '火', '水', '木', '金', '土'];
    const weekday = weekdays[d.getDay()];
    
    return `${year}年${month}月${day}日(${weekday})`;
  };

  // データ取得
  useEffect(() => {
    const loadDaySchedules = async () => {
      try {
        setLoading(true);
        const formattedDate = date.toISOString().split('T')[0].replace(/-/g, '');
        const data = await fetchSchedulesByDate(formattedDate);
        
        // ワークセンター別にグループ化
        const groupedByWorkCenter = data.reduce((acc, schedule) => {
          const workCenterId = schedule.work_center;
          if (!acc[workCenterId]) {
            acc[workCenterId] = [];
          }
          acc[workCenterId].push(schedule);
          return acc;
        }, {});
        
        setSchedules(groupedByWorkCenter);
        setError(null);
      } catch (err) {
        console.error('日別スケジュール取得エラー:', err);
        setError('スケジュールデータの取得中にエラーが発生しました。');
      } finally {
        setLoading(false);
      }
    };

    if (date) {
      loadDaySchedules();
    }
  }, [date]);

  // ワークセンターの表示順序
  const workCenterOrder = [
    '200100', // JP1
    '200201', // 2A
    '200200', // 2B
    '200202', // 2C
    '200300', // JP3
    '200400', // JP4
    '200601', // 6A
    '200602', // 6B
    '200700', // 7A/7B
  ];

  // ワークセンター名のマッピング
  const workCenterNames = {
    '200100': 'JP1',
    '200201': '2A',
    '200200': '2B',
    '200202': '2C',
    '200300': 'JP3',
    '200400': 'JP4',
    '200601': '6A',
    '200602': '6B',
    '200700': '7A/7B',
  };

  // ローディング表示
  if (loading) {
    return (
      <div className="day-schedule-container">
        <div className="day-schedule-header">
          <h2>{formatDate(date)} の生産予定</h2>
          <button className="close-button" onClick={onClose}>閉じる</button>
        </div>
        <div className="loading">データ読み込み中...</div>
      </div>
    );
  }

  // エラー表示
  if (error) {
    return (
      <div className="day-schedule-container">
        <div className="day-schedule-header">
          <h2>{formatDate(date)} の生産予定</h2>
          <button className="close-button" onClick={onClose}>閉じる</button>
        </div>
        <div className="error">{error}</div>
      </div>
    );
  }

  return (
    <div className="day-schedule-container">
      <div className="day-schedule-header">
        <h2>{formatDate(date)} の生産予定</h2>
        <button className="close-button" onClick={onClose}>閉じる</button>
      </div>
      
      <div className="day-schedule-content">
        {workCenterOrder.map(workCenterId => {
          const workCenterSchedules = schedules[workCenterId] || [];
          if (workCenterSchedules.length === 0) return null;
          
          return (
            <div key={workCenterId} className="work-center-group">
              <h3 
                className="work-center-name" 
                style={{ backgroundColor: workCenterColors[workCenterId] || '#999999' }}
              >
                {workCenterNames[workCenterId] || 'その他'}
              </h3>
              <div className="schedule-items">
                {workCenterSchedules.map(schedule => (
                  <div key={schedule.id} className="schedule-item">
                    <div className="schedule-product-name">{schedule.product_name}</div>
                    <div className="schedule-details">
                      <span>品番: {schedule.product_number}</span>
                      <span>生産数: {schedule.production_quantity}</span>
                      {schedule.notes && <span>備考: {schedule.notes}</span>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
        
        {Object.keys(schedules).length === 0 && (
          <div className="no-schedules">この日の予定はありません</div>
        )}
      </div>
    </div>
  );
};

export default DayScheduleView;