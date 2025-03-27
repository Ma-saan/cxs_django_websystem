import { getCsrfToken } from '../utils/csrf';

const API_BASE_URL = '/schedule_manager/api';

// CSRF対応のヘッダー生成
const getHeaders = () => {
  return {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCsrfToken(),
  };
};

// スケジュールデータの取得（日付範囲指定）
export const fetchSchedules = async (startDate, endDate) => {
  try {
    const response = await fetch(`${API_BASE_URL}/schedules/?start_date=${startDate}&end_date=${endDate}`);
    
    if (!response.ok) {
      throw new Error(`APIエラー: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('スケジュールデータの取得に失敗しました:', error);
    throw error;
  }
};

// 特定日のスケジュールデータ取得
export const fetchSchedulesByDate = async (date) => {
  try {
    const response = await fetch(`${API_BASE_URL}/schedules/?date=${date}`);
    
    if (!response.ok) {
      throw new Error(`APIエラー: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('日別スケジュールデータの取得に失敗しました:', error);
    throw error;
  }
};

// スケジュールの位置更新
export const updateSchedulePosition = async (scheduleId, gridRow, gridColumn) => {
  try {
    const response = await fetch(`${API_BASE_URL}/schedules/update_position/`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({
        id: scheduleId,
        grid_row: gridRow,
        grid_column: gridColumn
      })
    });
    
    if (!response.ok) {
      throw new Error(`APIエラー: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('スケジュール位置の更新に失敗しました:', error);
    throw error;
  }
};

// 新規スケジュール作成
export const createSchedule = async (scheduleData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/schedules/`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(scheduleData)
    });
    
    if (!response.ok) {
      throw new Error(`APIエラー: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('スケジュールの作成に失敗しました:', error);
    throw error;
  }
};

// スケジュール更新
export const updateSchedule = async (scheduleId, scheduleData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/schedules/${scheduleId}/`, {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify(scheduleData)
    });
    
    if (!response.ok) {
      throw new Error(`APIエラー: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('スケジュールの更新に失敗しました:', error);
    throw error;
  }
};

// スケジュール削除
export const deleteSchedule = async (scheduleId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/schedules/${scheduleId}/`, {
      method: 'DELETE',
      headers: getHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`APIエラー: ${response.statusText}`);
    }
    
    return true;
  } catch (error) {
    console.error('スケジュールの削除に失敗しました:', error);
    throw error;
  }
};

// ワークセンター一覧取得
export const fetchWorkCenters = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/work-centers/`);
    
    if (!response.ok) {
      throw new Error(`APIエラー: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('ワークセンターデータの取得に失敗しました:', error);
    throw error;
  }
};