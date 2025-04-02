/**
 * schedule_manager_utils.js
 * 
 * 生産予定管理システムのユーティリティ関数と拡張機能
 * 既存のschedule_board.jsとproduct_cards.jsを補完する機能を提供
 * 
 * 依存: jQuery, schedule_board.js
 * このスクリプトはjQueryとschedule_board.jsの後に読み込む必要があります
 */

// 名前空間を作成して競合を防止
const ScheduleManagerUtils = (function() {
    // プライベート変数
    let config = {
        debug: true,
        apiUrl: '/schedule_manager/api/',
        dateFormat: 'YYYYMMDD'
    };
    
    /**
     * デバッグログを出力
     * @param {string} message - ログメッセージ
     * @param {*} data - 追加データ（オプション）
     */
    function debugLog(message, data) {
        if (config.debug) {
            if (data !== undefined) {
                console.log(`[ScheduleManagerUtils] ${message}`, data);
            } else {
                console.log(`[ScheduleManagerUtils] ${message}`);
            }
        }
    }
    
    /**
     * エラーログを出力
     * @param {string} message - エラーメッセージ
     * @param {*} error - エラーオブジェクト
     */
    function errorLog(message, error) {
        console.error(`[ScheduleManagerUtils] エラー: ${message}`, error);
    }
    
    /**
     * CSRFトークンを取得
     * @returns {string} CSRFトークン
     */
    function getCsrfToken() {
        const tokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
        if (!tokenElement) {
            errorLog('CSRFトークン要素が見つかりません');
            return '';
        }
        return tokenElement.value;
    }
    
    /**
     * AJAXリクエストをCSRF保護付きで送信
     * @param {Object} options - AJAXオプション
     * @returns {Promise} AJAXリクエストのPromise
     */
    function sendRequest(options) {
        return new Promise((resolve, reject) => {
            // デフォルトオプションを設定
            const defaultOptions = {
                url: '',
                type: 'GET',
                dataType: 'json',
                contentType: 'application/json',
                headers: {},
                data: null
            };
            
            // オプションをマージ
            const requestOptions = {...defaultOptions, ...options};
            
            // GETでない場合はCSRFトークンを追加
            if (requestOptions.type !== 'GET') {
                requestOptions.headers['X-CSRFToken'] = getCsrfToken();
            }
            
            // データがオブジェクトでcontentTypeがJSONの場合は文字列化
            if (requestOptions.data && 
                typeof requestOptions.data === 'object' && 
                requestOptions.contentType === 'application/json') {
                requestOptions.data = JSON.stringify(requestOptions.data);
            }
            
            debugLog(`${requestOptions.type} リクエスト送信: ${requestOptions.url}`, requestOptions.data);
            
            // AJAXリクエスト実行
            $.ajax(requestOptions)
                .done(function(response) {
                    debugLog('リクエスト成功', response);
                    resolve(response);
                })
                .fail(function(xhr, status, error) {
                    errorLog(`リクエスト失敗: ${status}`, error);
                    // レスポンス内容の確認
                    try {
                        const responseText = xhr.responseText;
                        errorLog('サーバーレスポンス:', responseText);
                    } catch (e) {
                        // 無視
                    }
                    reject({xhr, status, error});
                });
        });
    }
    
    /**
     * 日付オブジェクトをAPIフォーマット(YYYYMMDD)に変換
     * @param {Date} date - 日付オブジェクト
     * @returns {string} YYYYMMDD形式の文字列
     */
    function formatDateForApi(date) {
        if (!date || !(date instanceof Date) || isNaN(date.getTime())) {
            errorLog('formatDateForApiに無効な日付が提供されました', date);
            // 今日の日付をフォールバックとして使用
            date = new Date();
        }
        
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}${month}${day}`;
    }
    
    /**
     * 日付オブジェクトを表示用フォーマット(YYYY年MM月DD日(曜日))に変換
     * @param {Date} date - 日付オブジェクト
     * @returns {string} 表示用の日付文字列
     */
    function formatDateForDisplay(date) {
        if (!date || !(date instanceof Date) || isNaN(date.getTime())) {
            errorLog('formatDateForDisplayに無効な日付が提供されました', date);
            date = new Date();
        }
        
        const year = date.getFullYear();
        const month = date.getMonth() + 1;
        const day = date.getDate();
        const weekdays = ['日', '月', '火', '水', '木', '金', '土'];
        const weekday = weekdays[date.getDay()];
        
        return `${year}年${month}月${day}日(${weekday})`;
    }
    
    /**
     * 日付文字列からDateオブジェクトを生成
     * @param {string} dateStr - 日付文字列 (YYYYMMDD形式)
     * @returns {Date|null} 日付オブジェクト、解析失敗時はnull
     */
    function parseDate(dateStr) {
        if (!dateStr || typeof dateStr !== 'string') {
            errorLog('parseDateに無効な日付文字列が提供されました', dateStr);
            return null;
        }
        
        try {
            // YYYYMMDD形式
            if (dateStr.length === 8 && !isNaN(dateStr)) {
                const year = parseInt(dateStr.substring(0, 4));
                const month = parseInt(dateStr.substring(4, 6)) - 1; // JavaScriptの月は0-11
                const day = parseInt(dateStr.substring(6, 8));
                return new Date(year, month, day);
            }
            
            // YY/MM/DD形式
            if (dateStr.includes('/') && dateStr.length === 8) {
                const parts = dateStr.split('/');
                if (parts.length === 3) {
                    const year = 2000 + parseInt(parts[0]); // 20年代として解釈
                    const month = parseInt(parts[1]) - 1;
                    const day = parseInt(parts[2]);
                    return new Date(year, month, day);
                }
            }
            
            errorLog('サポートされていない日付形式', dateStr);
            return null;
        } catch (error) {
            errorLog('日付解析エラー', error);
            return null;
        }
    }
    
    /**
     * 背景色の明るさに基づいてテキスト色を決定
     * @param {string} backgroundColor - 16進数カラーコード (#RRGGBB)
     * @returns {string} テキスト色の16進数カラーコード
     */
    function getTextColorForBackground(backgroundColor) {
        try {
            // 無効なカラーコードの場合はデフォルト（黒）を返す
            if (!backgroundColor || !backgroundColor.startsWith('#') || backgroundColor.length !== 7) {
                return '#000000';
            }
            
            // 明るさを計算
            const rgb = parseInt(backgroundColor.substring(1), 16);
            const r = (rgb >> 16) & 0xff;
            const g = (rgb >> 8) & 0xff;
            const b = (rgb >> 0) & 0xff;
            const brightness = (r * 299 + g * 587 + b * 114) / 1000;
            
            // 明るい背景には暗いテキスト、暗い背景には明るいテキスト
            return brightness > 128 ? '#000000' : '#FFFFFF';
        } catch (error) {
            errorLog('テキスト色計算エラー', error);
            return '#000000'; // エラー時は黒をデフォルトとして使用
        }
    }
    
    /**
     * 指定された日付のスケジュールデータを取得
     * @param {Date|string} date - 日付オブジェクトまたはYYYYMMDD形式の文字列
     * @returns {Promise} スケジュールデータを解決するPromise
     */
    function fetchScheduleData(date) {
        // 日付が文字列の場合はDateオブジェクトに変換
        let dateObj = date;
        if (typeof date === 'string') {
            dateObj = parseDate(date);
            if (!dateObj) {
                return Promise.reject(new Error('無効な日付形式'));
            }
        }
        
        const formattedDate = formatDateForApi(dateObj);
        debugLog(`日付 ${formattedDate} のスケジュールデータを取得中`);
        
        return sendRequest({
            url: `${config.apiUrl}schedules/?date=${formattedDate}`,
            type: 'GET'
        });
    }
    
    /**
     * 今日の日付を取得
     * @returns {Date} 今日の日付オブジェクト
     */
    function getToday() {
        const today = new Date();
        // 時間部分をクリア（00:00:00）
        today.setHours(0, 0, 0, 0);
        return today;
    }
    
    /**
     * DOM要素がドキュメント内に存在するか確認
     * @param {string} selector - CSSセレクタ
     * @returns {boolean} 要素が存在するか
     */
    function elementExists(selector) {
        return document.querySelector(selector) !== null;
    }
    
    /**
     * 指定されたIDを持つ要素のテキストコンテンツを更新
     * @param {string} elementId - 要素のID
     * @param {string} text - 新しいテキスト
     * @returns {boolean} 更新に成功したか
     */
    function updateElementText(elementId, text) {
        const element = document.getElementById(elementId);
        if (!element) {
            errorLog(`ID "${elementId}" の要素が見つかりません`);
            return false;
        }
        
        element.textContent = text;
        return true;
    }
    
    /**
     * 手動テスト機能 - カレンダークリックをシミュレート
     * @param {number} day - クリックする日付
     * @returns {boolean} 操作が成功したか
     */
    function simulateCalendarClick(day) {
        debugLog(`日付 ${day} のカレンダークリックをシミュレート`);
        
        // 現在の月の対象日をクリック
        const dayElement = document.querySelector(`.calendar-day.current-month:not(.previous-month):not(.next-month):contains('${day}')`);
        if (!dayElement) {
            errorLog(`日付 ${day} の要素が見つかりません`);
            return false;
        }
        
        // クリックイベントをシミュレート
        dayElement.click();
        return true;
    }
    
    /**
     * 設定値を更新
     * @param {Object} newConfig - 新しい設定オブジェクト
     */
    function updateConfig(newConfig) {
        config = {...config, ...newConfig};
        debugLog('設定を更新しました', config);
    }
    
    /**
     * 初期化関数
     */
    function init() {
        debugLog('ScheduleManagerUtils を初期化中...');
        
        // AJAX共通設定
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!(/^(GET|HEAD|OPTIONS|TRACE)$/.test(settings.type)) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", getCsrfToken());
                }
            }
        });
        
        debugLog('初期化完了');
    }
    
    // DOMが読み込まれたら初期化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // デバッグツール - 特定の処理を直接実行して結果を確認
    function debug() {
        const debugInfo = {
            config: config,
            today: getToday(),
            todayFormatted: formatDateForDisplay(getToday()),
            apiDateFormat: formatDateForApi(getToday()),
            csrfToken: getCsrfToken().substring(0, 6) + '...',
            userAgent: navigator.userAgent,
            screenSize: `${window.innerWidth}x${window.innerHeight}`,
            elementsFound: {
                calendarGrid: elementExists('#calendar-grid'),
                leftBoard: elementExists('#board-left'),
                rightBoard: elementExists('#board-right'),
                contextMenu: elementExists('#context-menu')
            }
        };
        
        console.log('===== ScheduleManagerUtils デバッグ情報 =====');
        console.table(debugInfo);
        console.log('============================================');
        
        return debugInfo;
    }
    
    // 公開API
    return {
        formatDateForApi,
        formatDateForDisplay,
        parseDate,
        getTextColorForBackground,
        fetchScheduleData,
        getToday,
        updateElementText,
        sendRequest,
        simulateCalendarClick,
        updateConfig,
        debug
    };
})();

// グローバルスコープに公開
window.ScheduleManagerUtils = ScheduleManagerUtils;

// コンソールにロード完了を表示
console.log('schedule_manager_utils.js がロードされました');