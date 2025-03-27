import React, { useState, useEffect } from 'react';
import { Calendar, momentLocalizer } from 'react-big-calendar';
import moment from 'moment';
import 'moment/locale/ja';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import './CalendarView.css';
import { fetchSchedules } from '../api/scheduleApi';
import DayScheduleView from './DayScheduleView';

// 日本語ロケール設定
moment.locale('ja');
const localizer = momentLocalizer(moment);

const CalendarView = () => {
  const [schedules, setSchedules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedDate, setSelectedDate] = useState(null);

  // ワークセンターの色設定
  const workCenterColors = {
    '200100': '#952bff', // JP1
    '200201': '#f21c36', // 2A
    '200200': '#ff68b4', // 2B
    '200202': '#ff68b4', // 2C
    '200300': '#44df60', // JP3
    '200400': '#00c6c6', // JP4
    '200601': '#9b88b9', // 6A
    '200602': '#9b88b9', // 6B
    '200700': '#3c2dff', // 7A/7B
  };

  // カレンダーイベント形式に変換する関数
  const transformToCalendarEvents = (scheduleData) => {
    return scheduleData.map(schedule => {
      const workCenterName = schedule.work_center_details?.display_name || 'その他';
      const workCenterId = schedule.work_center;
      
      return {
        id: schedule.id,
        title: `${workCenterName}: ${schedule.product_name}`,
        start: new Date(schedule.production_date),
        end: new Date(schedule.production_date),
        workCenter: schedule.work_center,
        productName: schedule.product_name,
        productNumber: schedule.product_number,
        quantity: schedule.production_quantity,
        backgroundColor: schedule.display_color || workCenterColors[workCenterId] || '#999999',
        allDay: true,
        resource: schedule
      };
    });
  };

  // データ取得
  useEffect(() => {
    const loadSchedules = async () => {
      try {
        setLoading(true);
        // 現在の月の初日と末日を取得
        const today = new Date();
        const startDate = new Date(today.getFullYear(), today.getMonth(), 1);
        const endDate = new Date(today.getFullYear(), today.getMonth() + 1, 0);
        
        const formattedStartDate = startDate.toISOString().split('T')[0].replace(/-/g, '');
        const formattedEndDate = endDate.toISOString().split('T')[0].replace(/-/g, '');
        
        const data = await fetchSchedules(formattedStartDate, formattedEndDate);
        setSchedules(transformToCalendarEvents(data));
        setError(null);
      } catch (err) {
        console.error('スケジュール取得エラー:', err);
        setError('スケジュールデータの取得中にエラーが発生しました。');
      } finally {
        setLoading(false);
      }
    };

    loadSchedules();
  }, []);

  // 月変更時の処理
  const handleRangeChange = async (range) => {
    try {
      setLoading(true);
      
      // 範囲が配列の場合（週ビュー等）
      const start = Array.isArray(range) ? range[0] : range.start;
      const end = Array.isArray(range) ? range[range.length - 1] : range.end;
      
      const formattedStartDate = start.toISOString().split('T')[0].replace(/-/g, '');
      const formattedEndDate = end.toISOString().split('T')[0].replace(/-/g, '');
      
      const data = await fetchSchedules(formattedStartDate, formattedEndDate);
      setSchedules(transformToCalendarEvents(data));
    } catch (err) {
      console.error('スケジュール更新エラー:', err);
      setError('スケジュールデータの更新中にエラーが発生しました。');
    } finally {
      setLoading(false);
    }
  };

  // 日付選択時の処理
  const handleSelectSlot = (slotInfo) => {
    setSelectedDate(slotInfo.start);
  };

  // イベントスタイルのカスタマイズ
  const eventStyleGetter = (event) => {
    return {
      style: {
        backgroundColor: event.backgroundColor,
        borderRadius: '3px',
        color: '#ffffff',
        border: '1px solid #555',
        display: 'block',
        padding: '2px 5px',
        fontSize: '0.8em'
      }
    };
  };

  // ローディング表示
  if (loading && schedules.length === 0) {
    return <div className="loading">データ読み込み中...</div>;
  }

  // エラー表示
  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="calendar-container">
      {selectedDate ? (
        <DayScheduleView 
          date={selectedDate} 
          onClose={() => setSelectedDate(null)}
          workCenterColors={workCenterColors}
        />
      ) : (
        <Calendar
          localizer={localizer}
          events={schedules}
          startAccessor="start"
          endAccessor="end"
          style={{ height: 'calc(100vh - 100px)' }}
          views={['month']}
          defaultView="month"
          onRangeChange={handleRangeChange}
          onSelectSlot={handleSelectSlot}
          selectable={true}
          eventPropGetter={eventStyleGetter}
          messages={{
            today: '今日',
            previous: '前へ',
            next: '次へ',
            month: '月',
            week: '週',
            day: '日',
            agenda: '予定',
            date: '日付',
            time: '時間',
            event: '予定',
            noEventsInRange: 'この期間には予定がありません',
          }}
        />
      )}
    </div>
  );
};

export default CalendarView;