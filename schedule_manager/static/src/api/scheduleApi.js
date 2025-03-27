// schedule_manager/static/src/api/scheduleApi.js

import { getCsrfToken } from '../utils/csrf';

const API_BASE_URL = '/schedule_manager/api';

/**
 * API用のHTTPヘッダーを生成
 * CSRF対策トークンを含む
 */
const getHeaders = () => {
  return {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCsrfToken(),
  };
};

/**
 * 指定した日付の生産予定データを取得
 * @param {string} dateStr - YYYYMMDD形式の日付文字列
 * @returns {Promise<Array>} - 生産予定データの配列
 */
export const fetchSchedulesByDate = async (dateStr) => {
  try {
    const response = await fetch(`${API_BASE_URL}/schedules/?date=${dateStr}`);
    
    if (!response.ok) {
      throw new Error(`APIエラー: ${response.status} ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('スケジュールデータの取得に失敗しました:', error);
    throw error;
  }
};

/**
 * 生産予定の位置情報を更新
 * @param {number} scheduleId - 更新対象のスケジュールID
 * @param {Object} position - 位置情報
 * @returns {Promise<Object>} - 更新されたスケジュールデータ
 */
export const updateSchedulePosition = async (scheduleId, position) => {
  try {
    const response = await fetch(`${API_BASE_URL}/schedules/update-position/`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({
        id: scheduleId,
        position: position
      })
    });
    
    if (!response.ok) {
      throw new Error(`APIエラー: ${response.status} ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('位置情報の更新に失敗しました:', error);
    throw error;
  }
};

/**
 * WebSocketを使用してリアルタイム更新を行うためのクラス
 */
export class ScheduleWebSocket {
  constructor(onMessage) {
    this.socket = null;
    this.onMessage = onMessage;
    this.isConnected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
  }
  
  /**
   * WebSocket接続を確立
   */
  connect() {
    if (this.socket) {
      return;
    }
    
    // WebSocketのURL構築（http→ws, https→wssに変換）
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const wsUrl = `${protocol}//${host}/ws/schedule_manager/`;
    
    this.socket = new WebSocket(wsUrl);
    
    this.socket.onopen = () => {
      console.log('WebSocket接続が確立されました');
      this.isConnected = true;
      this.reconnectAttempts = 0;
      
      // 初期データ同期リクエスト
      this.sendMessage({
        action: 'sync',
        date: new Date().toISOString().split('T')[0].replace(/-/g, '')
      });
    };
    
    this.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        if (typeof this.onMessage === 'function') {
          this.onMessage(data);
        }
      } catch (error) {
        console.error('WebSocketメッセージの処理に失敗しました:', error);
      }
    };
    
    this.socket.onclose = (event) => {
      console.log(`WebSocket接続が閉じられました: ${event.code} ${event.reason}`);
      this.isConnected = false;
      
      // 再接続を試みる
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++;
        const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
        
        console.log(`${delay}ms後に再接続を試みます (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        setTimeout(() => this.connect(), delay);
      }
    };
    
    this.socket.onerror = (error) => {
      console.error('WebSocketエラー:', error);
    };
  }
  
  /**
   * WebSocketにメッセージを送信
   * @param {Object} data - 送信するデータ
   */
  sendMessage(data) {
    if (this.socket && this.isConnected) {
      this.socket.send(JSON.stringify(data));
    } else {
      console.warn('WebSocketが接続されていません。メッセージを送信できません。');
    }
  }
  
  /**
   * WebSocket接続を閉じる
   */
  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
      this.isConnected = false;
    }
  }
  
  /**
   * 特定の日付のデータ同期をリクエスト
   * @param {string} dateStr - YYYYMMDD形式の日付文字列
   */
  syncDate(dateStr) {
    this.sendMessage({
      action: 'sync',
      date: dateStr
    });
  }
}

/**
 * 全ワークセンター情報を取得
 * @returns {Promise<Array>} - ワークセンター情報の配列
 */
export const fetchWorkCenters = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/work-centers/`);
    
    if (!response.ok) {
      throw new Error(`APIエラー: ${response.status} ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('ワークセンターデータの取得に失敗しました:', error);
    throw error;
  }
};