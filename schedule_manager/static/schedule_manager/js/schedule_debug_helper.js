/**
 * schedule_debug_helper.js
 * 
 * 生産予定管理システムのデバッグと問題診断用のヘルパースクリプト
 * 開発環境でのみ使用し、本番環境では読み込まないでください
 */

// 名前空間を使用して他のスクリプトとの競合を避ける
const ScheduleDebugHelper = (function() {
    // デバッグモード
    let isDebugMode = true;
    
    // 診断情報の全般チェック
    function runDiagnostics() {
        const diagnostics = {
            browser: detectBrowser(),
            domLoaded: document.readyState,
            screenSize: {
                width: window.innerWidth,
                height: window.innerHeight
            },
            scripts: getLoadedScripts(),
            csrfToken: checkCsrfToken(),
            domElements: checkDomElements(),
            dateSelectionIssue: checkDateSelection(),
            apiConnectivity: 'checking...' // 非同期で後で更新
        };
        
        console.log('%c==== 生産予定管理システム 診断レポート ====', 'color: #4CAF50; font-weight: bold; font-size: 14px;');
        console.table(diagnostics);
        
        // API接続テスト
        testApiConnection().then(result => {
            diagnostics.apiConnectivity = result;
            console.log('%cAPI接続テスト結果:', 'color: #2196F3; font-weight: bold;', result);
        });
        
        return diagnostics;
    }
    
    // ブラウザとバージョンを検出
    function detectBrowser() {
        const userAgent = navigator.userAgent;
        let browserName;
        let browserVersion;
        
        if (userAgent.includes('Firefox')) {
            browserName = 'Firefox';
            browserVersion = userAgent.match(/Firefox\/([\d.]+)/)[1];
        } else if (userAgent.includes('Chrome') && !userAgent.includes('Edg')) {
            browserName = 'Chrome';
            browserVersion = userAgent.match(/Chrome\/([\d.]+)/)[1];
        } else if (userAgent.includes('Safari') && !userAgent.includes('Chrome')) {
            browserName = 'Safari';
            browserVersion = userAgent.match(/Version\/([\d.]+)/)[1];
        } else if (userAgent.includes('Edg')) {
            browserName = 'Edge';
            browserVersion = userAgent.match(/Edg\/([\d.]+)/)[1];
        } else {
            browserName = 'Unknown';
            browserVersion = 'Unknown';
        }
        
        return `${browserName} ${browserVersion}`;
    }
    
    // ロードされているスクリプトを確認
    function getLoadedScripts() {
        const scripts = document.querySelectorAll('script[src]');
        const scriptData = {};
        
        scripts.forEach(script => {
            const src = script.getAttribute('src');
            const fileName = src.split('/').pop();
            scriptData[fileName] = {
                loaded: true,
                path: src,
                hasError: script.onerror !== null
            };
        });
        
        // 必要なスクリプトのリスト
        const requiredScripts = [
            'jquery.min.js',
            'jquery-ui.min.js', 
            'schedule_board.js',
            'product_cards.js'
        ];
        
        requiredScripts.forEach(script => {
            if (!scriptData[script]) {
                scriptData[script] = {
                    loaded: false,
                    path: 'Not loaded',
                    hasError: true
                };
            }
        });
        
        return scriptData;
    }
    
    // CSRFトークンを確認
    function checkCsrfToken() {
        const tokenElement = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (!tokenElement) {
            return 'CSRF Token missing';
        }
        const token = tokenElement.value;
        return token ? `Found (${token.substring(0, 6)}...)` : 'Empty token';
    }
    
    // 重要なDOM要素の存在を確認
    function checkDomElements() {
        const elements = {
            'calendar-grid': '#calendar-grid',
            'current-month': '#current-month',
            'board-left': '#board-left',
            'board-right': '#board-right',
            'left-date': '#left-date',
            'right-date': '#right-date',
            'context-menu': '#context-menu'
        };
        
        const results = {};
        for (const [name, selector] of Object.entries(elements)) {
            const element = document.querySelector(selector);
            results[name] = {
                exists: !!element,
                visible: element ? isVisible(element) : false
            };
        }
        
        return results;
    }
    
    // 要素が視覚的に表示されているか確認
    function isVisible(element) {
        const style = window.getComputedStyle(element);
        return style.display !== 'none' && 
               style.visibility !== 'hidden' && 
               style.opacity !== '0';
    }
    
    // 日付選択の問題を診断
    function checkDateSelection() {
        const calendarDays = document.querySelectorAll('.calendar-day');
        const selectedDay = document.querySelector('.calendar-day.selected');
        
        if (calendarDays.length === 0) {
            return 'カレンダー日付要素が見つかりません';
        }
        
        if (!selectedDay) {
            // 日付選択を試みる（テスト用）
            const today = new Date().getDate();
            const currentMonthDays = document.querySelectorAll('.calendar-day.current-month');
            
            for (let day of currentMonthDays) {
                if (day.textContent == today) {
                    day.click();
                    console.log('今日の日付をシミュレートクリックしました');
                    break;
                }
            }
            
            const selectedAfterClick = document.querySelector('.calendar-day.selected');
            if (!selectedAfterClick) {
                return 'カレンダークリック後も日付選択が機能していません';
            }
            return 'カレンダーの日付が選択されていません（テストクリックを実行）';
        }
        
        return `日付が選択されています: ${selectedDay.textContent}`;
    }
    
    // API接続テスト
    async function testApiConnection() {
        try {
            const response = await fetch('/schedule_manager/api/work-centers/');
            
            if (!response.ok) {
                return `APIエラー: ${response.status} ${response.statusText}`;
            }
            
            const data = await response.json();
            return `成功（${data.length}件のワークセンターが取得されました）`;
        } catch (error) {
            return `API接続エラー: ${error.message}`;
        }
    }
    
    // ネットワークリクエストをモニタリング
    function monitorNetworkRequests() {
        const originalFetch = window.fetch;
        const originalXhrOpen = XMLHttpRequest.prototype.open;
        const originalXhrSend = XMLHttpRequest.prototype.send;
        
        // Fetchリクエストをモニタリング
        window.fetch = async function(...args) {
            const url = args[0];
            const options = args[1] || {};
            
            console.log('%cFetch リクエスト:', 'color: #2196F3;', url, options);
            
            try {
                const response = await originalFetch.apply(this, args);
                const responseClone = response.clone();
                
                responseClone.text().then(text => {
                    try {
                        const data = JSON.parse(text);
                        console.log('%cFetch レスポンス:', 'color: #4CAF50;', url, data);
                    } catch (e) {
                        console.log('%cFetch レスポンス (テキスト):', 'color: #4CAF50;', url, text.substring(0, 500));
                    }
                }).catch(err => {
                    console.log('%cFetch レスポンス読み取りエラー:', 'color: #F44336;', url, err);
                });
                
                return response;
            } catch (error) {
                console.log('%cFetch エラー:', 'color: #F44336;', url, error);
                throw error;
            }
        };
        
        // XMLHttpRequestリクエストをモニタリング
        XMLHttpRequest.prototype.open = function(...args) {
            this._url = args[1];
            this._method = args[0];
            return originalXhrOpen.apply(this, args);
        };
        
        XMLHttpRequest.prototype.send = function(body) {
            console.log('%cXHR リクエスト:', 'color: #FF9800;', this._method, this._url, body || '');
            
            this.addEventListener('load', function() {
                try {
                    let responseText = this.responseText;
                    let data;
                    
                    try {
                        data = JSON.parse(responseText);
                    } catch (e) {
                        data = responseText.substring(0, 500);
                    }
                    
                    console.log('%cXHR レスポンス:', 'color: #8BC34A;', this._method, this._url, data);
                } catch (e) {
                    console.log('%cXHR レスポンス読み取りエラー:', 'color: #F44336;', e);
                }
            });
            
            this.addEventListener('error', function(event) {
                console.log('%cXHR エラー:', 'color: #F44336;', this._method, this._url, event);
            });
            
            return originalXhrSend.apply(this, arguments);
        };
        
        console.log('%cネットワークリクエストのモニタリングを開始しました', 'color: #9C27B0; font-weight: bold;');
    }
    
    // jQuery要素検索のヘルパー
    function showElements(selector) {
        const elements = $(selector);
        console.log(`セレクタ "${selector}" で ${elements.length} 要素が見つかりました:`);
        
        elements.each(function(index) {
            const element = $(this);
            console.log(`${index + 1}. ${element.prop('tagName')}`, {
                id: element.attr('id') || '(なし)',
                classes: element.attr('class') || '(なし)',
                text: element.text().substring(0, 50),
                visible: element.is(':visible'),
                dimensions: `${element.width()}x${element.height()}`
            });
        });
        
        return elements.length > 0;
    }
    
    // 手動でスケジュールデータをロード
    function loadScheduleData(dateStr) {
        console.log('%cスケジュールデータを手動でロード中...', 'color: #FF5722; font-weight: bold;');
        
        let date;
        if (!dateStr) {
            // 日付が指定されていない場合は今日を使用
            date = new Date();
        } else if (typeof dateStr === 'string') {
            // 日付文字列を解析
            if (dateStr.length === 8 && !isNaN(dateStr)) {
                // YYYYMMDD 形式
                const year = parseInt(dateStr.substring(0, 4));
                const month = parseInt(dateStr.substring(4, 6)) - 1;
                const day = parseInt(dateStr.substring(6, 8));
                date = new Date(year, month, day);
            } else if (dateStr.includes('/')) {
                // YY/MM/DD 形式
                const parts = dateStr.split('/');
                if (parts.length === 3) {
                    const year = 2000 + parseInt(parts[0]);
                    const month = parseInt(parts[1]) - 1;
                    const day = parseInt(parts[2]);
                    date = new Date(year, month, day);
                }
            } else {
                console.error('不明な日付形式:', dateStr);
                return false;
            }
        } else if (dateStr instanceof Date) {
            date = dateStr;
        } else {
            console.error('無効な日付:', dateStr);
            return false;
        }
        
        if (!date || isNaN(date.getTime())) {
            console.error('無効な日付オブジェクト');
            return false;
        }
        
        // APIフォーマットに変換
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const formattedDate = `${year}${month}${day}`;
        
        console.log(`日付 ${formattedDate} のデータをロード中...`);
        
        // 左ボードのデータをロード
        const leftUrl = `/schedule_manager/api/schedules/?date=${formattedDate}`;
        fetch(leftUrl)
            .then(response => response.json())
            .then(data => {
                console.log('左ボードデータ取得成功:', data);
                const leftDateElement = document.getElementById('left-date');
                if (leftDateElement) {
                    // 日付表示を更新
                    const formattedDisplayDate = formatDateForDisplay(date);
                    leftDateElement.textContent = formattedDisplayDate;
                }
                
                // ここで必要な処理を行う（例えば、手動でボードを更新）
                updateBoardManually('left', data);
            })
            .catch(error => {
                console.error('左ボードデータ取得エラー:', error);
            });
            
        // 翌日の日付を計算
        const nextDay = new Date(date);
        nextDay.setDate(nextDay.getDate() + 1);
        const nextYear = nextDay.getFullYear();
        const nextMonth = String(nextDay.getMonth() + 1).padStart(2, '0');
        const nextDayDate = String(nextDay.getDate()).padStart(2, '0');
        const nextFormattedDate = `${nextYear}${nextMonth}${nextDayDate}`;
        
        // 右ボードのデータをロード
        const rightUrl = `/schedule_manager/api/schedules/?date=${nextFormattedDate}`;
        fetch(rightUrl)
            .then(response => response.json())
            .then(data => {
                console.log('右ボードデータ取得成功:', data);
                const rightDateElement = document.getElementById('right-date');
                if (rightDateElement) {
                    // 日付表示を更新
                    const formattedDisplayDate = formatDateForDisplay(nextDay);
                    rightDateElement.textContent = formattedDisplayDate;
                }
                
                // 右ボードを手動で更新
                updateBoardManually('right', data);
            })
            .catch(error => {
                console.error('右ボードデータ取得エラー:', error);
            });
            
        return true;
    }
    
    // 日付表示用にフォーマット
    function formatDateForDisplay(date) {
        const year = date.getFullYear();
        const month = date.getMonth() + 1;
        const day = date.getDate();
        const weekdays = ['日', '月', '火', '水', '木', '金', '土'];
        const weekday = weekdays[date.getDay()];
        return `${year}年${month}月${day}日(${weekday})`;
    }
    
    // ボードを手動で更新（デバッグ用）
    function updateBoardManually(side, data) {
        console.log(`${side}ボードを手動で更新中...`, data);
        
        const boardSelector = side === 'left' ? '#board-left' : '#board-right';
        
        // ワークセンター定義
        const workCenters = [
            { id: '200100', name: 'JP1', color: '#952bff' },
            { id: '200201', name: '2A', color: '#f21c36' },
            { id: '200200', name: '2B', color: '#ff68b4' },
            { id: '200202', name: '2C', color: '#ff68b4' },
            { id: '200300', name: 'JP3', color: '#44df60' },
            { id: '200400', name: 'JP4', color: '#00c6c6' },
            { id: '200601', name: '6A', color: '#9b88b9' },
            { id: '200602', name: '6B', color: '#9b88b9' },
            { id: '200700', name: '7A/7B', color: '#3c2dff' }
        ];
        
        // ライン別にデータをグループ化
        const groupedData = {};
        workCenters.forEach(workCenter => {
            groupedData[workCenter.id] = data.filter(
                item => item.work_center === workCenter.id
            ).sort((a, b) => (a.grid_row - b.grid_row || a.grid_column - b.grid_column));
        });
        
        // 各ラインのカードを更新
        workCenters.forEach(workCenter => {
            const lineSelector = `${boardSelector} .line-cards[data-line-id="${workCenter.id}"]`;
            const lineElement = document.querySelector(lineSelector);
            
            if (!lineElement) {
                console.warn(`ライン要素が見つかりません: ${lineSelector}`);
                return;
            }
            
            // 既存のカードをクリア
            lineElement.innerHTML = '';
            
            const cards = groupedData[workCenter.id] || [];
            console.log(`${side}ボード / ${workCenter.name}: ${cards.length}件のカード`);
            
            // カードを生成して追加
            cards.forEach(card => {
                const cardElement = createCardElement(card);
                lineElement.appendChild(cardElement);
            });
        });
        
        console.log(`${side}ボードの更新完了`);
    }
    
    // カード要素を作成（デバッグ用の単純な実装）
    function createCardElement(card) {
        // カードの背景色
        const cardColor = card.display_color || '#ffffff';
        
        // テキスト色を背景色に基づいて決定
        const getBrightness = (hexColor) => {
            if (!hexColor || !hexColor.startsWith('#') || hexColor.length !== 7) {
                return 255;
            }
            
            try {
                const rgb = parseInt(hexColor.substring(1), 16);
                const r = (rgb >> 16) & 0xff;
                const g = (rgb >> 8) & 0xff;
                const b = (rgb >> 0) & 0xff;
                return (r * 299 + g * 587 + b * 114) / 1000;
            } catch (error) {
                console.error("テキスト色計算エラー:", error);
                return 255;
            }
        };
        
        const textColor = getBrightness(cardColor) > 128 ? '#000000' : '#ffffff';
        
        // カード要素を作成
        const cardElement = document.createElement('div');
        cardElement.className = 'product-card';
        cardElement.dataset.cardId = card.id;
        cardElement.style.backgroundColor = cardColor;
        cardElement.style.color = textColor;
        
        // 製品名要素
        const nameElement = document.createElement('div');
        nameElement.className = 'product-name';
        nameElement.textContent = card.product_name || '名称なし';
        
        // 詳細情報要素
        const detailsElement = document.createElement('div');
        detailsElement.className = 'product-details';
        
        // 品番
        const numberSpan = document.createElement('span');
        numberSpan.className = 'product-number';
        numberSpan.textContent = `品番: ${card.product_number || 'なし'}`;
        detailsElement.appendChild(numberSpan);
        
        // 数量
        const quantitySpan = document.createElement('span');
        quantitySpan.className = 'product-quantity';
        quantitySpan.textContent = `数量: ${card.production_quantity || 0}`;
        detailsElement.appendChild(quantitySpan);
        
        // 要素を組み立て
        cardElement.appendChild(nameElement);
        cardElement.appendChild(detailsElement);
        
        return cardElement;
    }
    
    // デバッグパネルを表示
    function showDebugPanel() {
        // 既存のパネルがあれば削除
        const existingPanel = document.getElementById('schedule-debug-panel');
        if (existingPanel) {
            existingPanel.remove();
        }
        
        // デバッグパネル要素を作成
        const panel = document.createElement('div');
        panel.id = 'schedule-debug-panel';
        panel.style.position = 'fixed';
        panel.style.bottom = '10px';
        panel.style.right = '10px';
        panel.style.width = '300px';
        panel.style.backgroundColor = '#333';
        panel.style.color = '#fff';
        panel.style.padding = '10px';
        panel.style.borderRadius = '5px';
        panel.style.zIndex = '9999';
        panel.style.fontSize = '12px';
        panel.style.boxShadow = '0 0 10px rgba(0,0,0,0.5)';
        
        // タイトル
        const title = document.createElement('div');
        title.textContent = 'スケジュール管理デバッグパネル';
        title.style.fontWeight = 'bold';
        title.style.marginBottom = '10px';
        title.style.borderBottom = '1px solid #555';
        title.style.paddingBottom = '5px';
        panel.appendChild(title);
        
        // 操作ボタン
        const actions = [
            { name: '診断実行', callback: runDiagnostics },
            { name: 'ネットワークモニター開始', callback: monitorNetworkRequests },
            { name: '今日のデータロード', callback: () => loadScheduleData() },
            { name: 'DOM要素確認', callback: () => showElements('.calendar-day, .line-cards, .product-card') }
        ];
        
        actions.forEach(action => {
            const button = document.createElement('button');
            button.textContent = action.name;
            button.style.margin = '5px';
            button.style.padding = '5px 10px';
            button.style.backgroundColor = '#555';
            button.style.color = '#fff';
            button.style.border = 'none';
            button.style.borderRadius = '3px';
            button.style.cursor = 'pointer';
            
            button.addEventListener('click', action.callback);
            panel.appendChild(button);
        });
        
        // ステータス表示エリア
        const status = document.createElement('div');
        status.id = 'debug-status';
        status.style.marginTop = '10px';
        status.style.padding = '5px';
        status.style.backgroundColor = '#222';
        status.style.borderRadius = '3px';
        status.style.minHeight = '50px';
        status.textContent = 'ステータス: 準備完了';
        panel.appendChild(status);
        
        // 閉じるボタン
        const closeBtn = document.createElement('button');
        closeBtn.textContent = '閉じる';
        closeBtn.style.position = 'absolute';
        closeBtn.style.top = '5px';
        closeBtn.style.right = '5px';
        closeBtn.style.padding = '2px 5px';
        closeBtn.style.backgroundColor = '#555';
        closeBtn.style.color = '#fff';
        closeBtn.style.border = 'none';
        closeBtn.style.borderRadius = '3px';
        closeBtn.style.cursor = 'pointer';
        
        closeBtn.addEventListener('click', () => panel.remove());
        panel.appendChild(closeBtn);
        
        // ドキュメントに追加
        document.body.appendChild(panel);
        
        return panel;
    }
    
    // 初期化
    function init() {
        if (!isDebugMode) return;
        
        console.log('%cスケジュール管理デバッグヘルパーがロードされました', 'color: #4CAF50; font-weight: bold;');
        
        // ショートカットキーの登録
        document.addEventListener('keydown', function(event) {
            // Alt+Shift+D でデバッグパネル表示
            if (event.altKey && event.shiftKey && event.key === 'D') {
                showDebugPanel();
            }
        });
    }
    
    // ドキュメント読み込み完了時に初期化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // 公開API
    return {
        runDiagnostics,
        showElements,
        monitorNetworkRequests,
        loadScheduleData,
        showDebugPanel,
        setDebugMode: function(mode) {
            isDebugMode = !!mode;
            console.log(`デバッグモードを${isDebugMode ? '有効' : '無効'}に設定しました`);
        }
    };
})();

// グローバルスコープに公開
window.ScheduleDebugHelper = ScheduleDebugHelper;

// コンソールにロード完了を表示
console.log('schedule_debug_helper.js がロードされました');