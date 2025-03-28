// 名前空間の作成
const ScheduleBoard = (function() {
    // 定数
    const API_URL = '/schedule_manager/api/';
    const WORK_CENTERS = [
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
    const COLOR_PALETTE = [
        "#ffff09", "#ffffc4", "#a1ff84", "#00fb00", "#00ffff", "#00c1c1", 
        "#ff8000", "#ffd481", "#8080ff", "#ccccff", "#ff80ff", "#ffdcff", 
        "#cb9696", "#a1e6ff", "#b3b3b3", "#ffffff"
    ];
    
    // 状態変数
    let currentDate = new Date();
    let selectedDate = null;
    let selectedCard = null;
    let boardData = {
        left: {},
        right: {}
    };
    
    // CSRFトークン取得
    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
    
    // 日付フォーマット (YYYY-MM-DD → YYYYMMDD)
    function formatDateForApi(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}${month}${day}`;
    }
    
    // 日付フォーマット (表示用)
    function formatDateForDisplay(date) {
        const year = date.getFullYear();
        const month = date.getMonth() + 1;
        const day = date.getDate();
        const weekdays = ['日', '月', '火', '水', '木', '金', '土'];
        const weekday = weekdays[date.getDay()];
        return `${year}年${month}月${day}日(${weekday})`;
    }
    
    // カレンダー初期化
    function initCalendar() {
        const calendarGrid = $('#calendar-grid');
        const currentMonthDisplay = $('#current-month');
        
        // 曜日のヘッダーを追加
        const weekdays = ["日", "月", "火", "水", "木", "金", "土"];
        weekdays.forEach(day => {
            calendarGrid.append(
                $('<div>').addClass('calendar-day-header').text(day)
            );
        });
        
        // カレンダー更新
        function updateCalendar() {
            // 現在の年月を表示
            currentMonthDisplay.text(
                `${currentDate.getFullYear()}年${currentDate.getMonth() + 1}月`
            );
            
            // 日付部分をクリア (ヘッダーは残す)
            calendarGrid.children().slice(7).remove();
            
            // 月初の日付
            const firstDay = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
            // 月初の曜日（0-6, 0が日曜）
            const firstDayIndex = firstDay.getDay();
            
            // 月末の日付
            const lastDay = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);
            const lastDate = lastDay.getDate();
            
            // 前月の末日
            const prevLastDay = new Date(currentDate.getFullYear(), currentDate.getMonth(), 0);
            const prevLastDate = prevLastDay.getDate();
            
            // 前月の日を追加
            for (let i = firstDayIndex; i > 0; i--) {
                const dayElement = $('<div>')
                    .addClass('calendar-day previous-month')
                    .text(prevLastDate - i + 1)
                    .css('opacity', '0.5');
                calendarGrid.append(dayElement);
            }
            
            // 現在の月の日を追加
            for (let i = 1; i <= lastDate; i++) {
                const dayElement = $('<div>')
                    .addClass('calendar-day current-month')
                    .text(i);
                
                // 今日の日付をハイライト
                const today = new Date();
                if (i === today.getDate() && 
                    currentDate.getMonth() === today.getMonth() && 
                    currentDate.getFullYear() === today.getFullYear()) {
                    dayElement.css({
                        'background-color': '#e8f4ff',
                        'border-color': '#007bff',
                        'font-weight': 'bold'
                    });
                }
                
                // 日付クリック時の処理
                dayElement.on('click', function() {
                    // 選択されているすべての日付のハイライトを解除
                    $('.calendar-day.selected').removeClass('selected').css('background-color', '');
                    
                    // この日付をハイライト
                    dayElement.addClass('selected').css('background-color', '#cce5ff');
                    
                    // 選択された日付の予定を表示
                    selectedDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), i);
                    loadBoardData();
                });
                
                calendarGrid.append(dayElement);
            }
            
            // 翌月の日を必要に応じて追加
            const totalCells = firstDayIndex + lastDate;
            const remainingCells = 42 - totalCells; // 6行 × 7列
            
            for (let i = 1; i <= remainingCells; i++) {
                const dayElement = $('<div>')
                    .addClass('calendar-day next-month')
                    .text(i)
                    .css('opacity', '0.5');
                calendarGrid.append(dayElement);
            }
        }
        
        // 前月ボタンのイベント
        $('#prev-month').on('click', function() {
            currentDate = new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1);
            updateCalendar();
        });
        
        // 次月ボタンのイベント
        $('#next-month').on('click', function() {
            currentDate = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1);
            updateCalendar();
        });
        
        // 初期表示
        updateCalendar();
    }
    
    // ボード初期化
    function initBoard() {
        const leftBoard = $('#board-left .production-lines');
        const rightBoard = $('#board-right .production-lines');
        
        // ライン生成
        function createLines(container) {
            container.empty();
            
            WORK_CENTERS.forEach(workCenter => {
                const lineContainer = $('<div>')
                    .addClass('line-container')
                    .css('border-top', `3px solid ${workCenter.color}`);
                
                const lineHeader = $('<div>')
                    .addClass('line-header')
                    .css('background-color', workCenter.color)
                    .text(workCenter.name);
                
                const lineCards = $('<div>')
                    .addClass('line-cards')
                    .attr('data-line-id', workCenter.id);
                
                lineContainer.append(lineHeader, lineCards);
                container.append(lineContainer);
                
                // sortable初期化
                lineCards.sortable({
                    connectWith: '.line-cards',
                    placeholder: 'ui-sortable-placeholder',
                    update: function(event, ui) {
                        // ドロップ元から呼ばれないようにする
                        if (this !== ui.item.parent()[0]) return;
                        
                        const cardId = ui.item.data('card-id');
                        const side = $(this).closest('.production-side').attr('id') === 'board-left' ? 'left' : 'right';
                        const lineId = $(this).data('line-id');
                        const newPosition = ui.item.index();
                        
                        // APIで位置更新
                        updateCardPosition(cardId, side, lineId, newPosition);
                    }
                }).disableSelection();
            });
        }
        
        // 両ボードにライン生成
        createLines(leftBoard);
        createLines(rightBoard);
        
        // DB保存ボタン
        $('#save-to-db').on('click', function() {
            saveToDatabase();
        });
        
        // DB読込ボタン
        $('#load-from-db').on('click', function() {
            loadFromDatabase();
        });
    }
    
    // ボードデータ読み込み
    function loadBoardData() {
        if (!selectedDate) return;
        
        // 左側のボード（選択日）
        const leftDate = new Date(selectedDate);
        $('#left-date').text(formatDateForDisplay(leftDate));
        
        // 右側のボード（翌日）
        const rightDate = new Date(leftDate);
        rightDate.setDate(rightDate.getDate() + 1);
        $('#right-date').text(formatDateForDisplay(rightDate));
        
        // データ取得
        fetchScheduleData('left', leftDate);
        fetchScheduleData('right', rightDate);
    }
    
    // スケジュールデータ取得
    function fetchScheduleData(side, date) {
        const formattedDate = formatDateForApi(date);
        
        $.ajax({
            url: `${API_URL}schedules/?date=${formattedDate}`,
            type: 'GET',
            success: function(data) {
                // ライン別にデータをグループ化
                const groupedData = {};
                
                WORK_CENTERS.forEach(workCenter => {
                    groupedData[workCenter.id] = data.filter(
                        item => item.work_center === workCenter.id
                    ).sort((a, b) => (a.grid_row - b.grid_row || a.grid_column - b.grid_column));
                });
                
                // 状態を更新
                boardData[side] = groupedData;
                
                // ボードを更新
                updateBoard(side);
            },
            error: function(xhr, status, error) {
                console.error('データ取得エラー:', error);
                alert('スケジュールデータの取得に失敗しました');
            }
        });
    }
    
    // ボード更新
    function updateBoard(side) {
        const boardSelector = side === 'left' ? '#board-left' : '#board-right';
        
        // 各ラインのカードを更新
        WORK_CENTERS.forEach(workCenter => {
            const lineCards = $(`${boardSelector} .line-cards[data-line-id="${workCenter.id}"]`);
            lineCards.empty();
            
            const cards = boardData[side][workCenter.id] || [];
            
            cards.forEach(card => {
                const cardElement = createCardElement(card, side);
                lineCards.append(cardElement);
            });
        });
    }
    
    // カード要素の作成
    function createCardElement(card, side) {
        const cardColor = card.display_color || '#ffffff';
        
        // テキスト色の決定（背景が明るいか暗いかで）
        const getBrightness = (hexColor) => {
            const rgb = parseInt(hexColor.substring(1), 16);
            const r = (rgb >> 16) & 0xff;
            const g = (rgb >> 8) & 0xff;
            const b = (rgb >> 0) & 0xff;
            return (r * 299 + g * 587 + b * 114) / 1000;
        };
        
        const textColor = getBrightness(cardColor) > 128 ? '#000000' : '#ffffff';
        
        const cardElement = $('<div>')
            .addClass('product-card')
            .attr('data-card-id', card.id)
            .css({
                'background-color': cardColor,
                'color': textColor
            });
        
        const nameElement = $('<div>')
            .addClass('product-name')
            .text(card.product_name);
        
        const detailsElement = $('<div>')
            .addClass('product-details')
            .append(
                $('<span>').addClass('product-number').text(`品番: ${card.product_number}`),
                $('<span>').addClass('product-quantity').text(`数量: ${card.production_quantity}`)
            );
        
        cardElement.append(nameElement, detailsElement);
        
        // 特殊属性の表示
        if (card.attributes && card.attributes.length > 0) {
            const attributesElement = $('<div>').addClass('product-attributes');
            
            card.attributes.forEach(attr => {
                let attributeText = '';
                
                if (attr.attribute_type === 'mixing') attributeText = '↻ 連続撹拌';
                else if (attr.attribute_type === 'rapid_fill') attributeText = '⚡ 早充依頼';
                else if (attr.attribute_type === 'special_transfer') attributeText = '⚠️ 特急移庫';
                else if (attr.attribute_type === 'icon_6b') attributeText = '6B';
                else if (attr.attribute_type === 'icon_7c') attributeText = '7C';
                else if (attr.attribute_type === 'icon_2c') attributeText = '2C';
                
                if (attributeText) {
                    attributesElement.append(
                        $('<span>')
                            .addClass(`product-attribute ${attr.attribute_type}`)
                            .text(attributeText)
                    );
                }
            });
            
            cardElement.append(attributesElement);
        }
        
        // コンテキストメニュー
        cardElement.on('contextmenu', function(e) {
            e.preventDefault();
            
            // 現在選択中のカード情報を更新
            selectedCard = {
                id: card.id,
                side: side,
                lineId: $(this).closest('.line-cards').data('line-id'),
                element: $(this)
            };
            
            // コンテキストメニュー表示
            const contextMenu = $('#context-menu');
            contextMenu.css({
                top: e.pageY + 'px',
                left: e.pageX + 'px',
                display: 'block'
            });
            
            // 属性の表示状態を反映
            const hasAttribute = (type) => {
                return card.attributes && card.attributes.some(attr => attr.attribute_type === type);
            };
            
            contextMenu.find('[data-action="toggle-mixing"]').text(
                `${hasAttribute('mixing') ? '✓ ' : ''}連続撹拌`
            );
            contextMenu.find('[data-action="toggle-rapid-fill"]').text(
                `${hasAttribute('rapid_fill') ? '✓ ' : ''}早充依頼`
            );
            contextMenu.find('[data-action="toggle-special-transfer"]').text(
                `${hasAttribute('special_transfer') ? '✓ ' : ''}特急移庫`
            );
            contextMenu.find('[data-action="toggle-icon-6b"]').text(
                `${hasAttribute('icon_6b') ? '✓ ' : ''}6B表示`
            );
            contextMenu.find('[data-action="toggle-icon-7c"]').text(
                `${hasAttribute('icon_7c') ? '✓ ' : ''}7C表示`
            );
            contextMenu.find('[data-action="toggle-icon-2c"]').text(
                `${hasAttribute('icon_2c') ? '✓ ' : ''}2C表示`
            );
        });
        
        return cardElement;
    }
    
    // カードの位置更新
    function updateCardPosition(cardId, side, lineId, position) {
        $.ajax({
            url: `${API_URL}schedules/update-position/`,
            type: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken()
            },
            contentType: 'application/json',
            data: JSON.stringify({
                id: cardId,
                position: {
                    side: side,
                    lineId: lineId,
                    position: position,
                    date: formatDateForApi(side === 'left' ? selectedDate : new Date(selectedDate.getTime() + 86400000))
                }
            }),
            success: function(data) {
                console.log('位置更新成功:', data);
                
                // ローカルデータの更新
                updateLocalCardData(cardId, side, lineId);
            },
            error: function(xhr, status, error) {
                console.error('位置更新エラー:', error);
                alert('位置情報の更新に失敗しました');
                
                // 元の状態に戻すために再読み込み
                loadBoardData();
            }
        });
    }
    
    // ローカルカードデータの更新
    function updateLocalCardData(cardId, side, lineId) {
        // 元の位置からカードデータを探す
        let cardData = null;
        let originalLineId = null;
        
        for (const [currentLineId, cards] of Object.entries(boardData[side])) {
            const cardIndex = cards.findIndex(card => card.id === cardId);
            if (cardIndex !== -1) {
                cardData = cards[cardIndex];
                originalLineId = currentLineId;
                // 元の位置から削除
                cards.splice(cardIndex, 1);
                break;
            }
        }
        
        // 新しい位置に追加
        if (cardData) {
            if (!boardData[side][lineId]) {
                boardData[side][lineId] = [];
            }
            
            // ワークセンターIDを更新
            cardData.work_center = lineId;
            
            // 新しい配列に追加
            boardData[side][lineId].push(cardData);
            
            // グリッド位置でソート
            boardData[side][lineId].sort((a, b) => a.grid_row - b.grid_row);
        }
    }
    
    // 色変更
    function changeCardColor(cardId, color) {
        $.ajax({
            url: `${API_URL}schedules/${cardId}/update_attribute/`,
            type: 'PATCH',
            headers: {
                'X-CSRFToken': getCsrfToken()
            },
            contentType: 'application/json',
            data: JSON.stringify({
                display_color: color
            }),
            success: function(data) {
                console.log('色変更成功:', data);
                
                // カード要素の色を更新
                if (selectedCard && selectedCard.element) {
                    const brightness = (hexColor) => {
                        const rgb = parseInt(hexColor.substring(1), 16);
                        const r = (rgb >> 16) & 0xff;
                        const g = (rgb >> 8) & 0xff;
                        const b = (rgb >> 0) & 0xff;
                        return (r * 299 + g * 587 + b * 114) / 1000;
                    };
                    
                    const textColor = brightness(color) > 128 ? '#000000' : '#ffffff';
                    
                    selectedCard.element.css({
                        'background-color': color,
                        'color': textColor
                    });
                }
                
                // ローカルデータも更新
                updateCardAttributeInLocalData(cardId, 'display_color', color);
            },
            error: function(xhr, status, error) {
                console.error('色変更エラー:', error);
                alert('色の変更に失敗しました');
            }
        });
    }
    
    // 製品名更新
    function updateProductName(cardId, newName) {
        $.ajax({
            url: `${API_URL}schedules/${cardId}/update_attribute/`,
            type: 'PATCH',
            headers: {
                'X-CSRFToken': getCsrfToken()
            },
            contentType: 'application/json',
            data: JSON.stringify({
                product_name: newName
            }),
            success: function(data) {
                console.log('名前更新成功:', data);
                
                // カード要素の名前を更新
                if (selectedCard && selectedCard.element) {
                    selectedCard.element.find('.product-name').text(newName);
                }
                
                // ローカルデータも更新
                updateCardAttributeInLocalData(cardId, 'product_name', newName);
            },
            error: function(xhr, status, error) {
                console.error('名前更新エラー:', error);
                alert('製品名の更新に失敗しました');
            }
        });
    }
    
    // 特殊属性の切り替え
    function toggleCardAttribute(cardId, attributeType) {
        // 現在の属性状態を確認
        const card = findCardInLocalData(cardId);
        const hasAttribute = card && card.attributes && 
                            card.attributes.some(attr => attr.attribute_type === attributeType);
        
        const action = hasAttribute ? 'remove' : 'add';
        
        $.ajax({
            url: `${API_URL}schedules/${cardId}/update_attribute/`,
            type: 'PATCH',
            headers: {
                'X-CSRFToken': getCsrfToken()
            },
            contentType: 'application/json',
            data: JSON.stringify({
                attribute_type: attributeType,
                attribute_action: action
            }),
            success: function(data) {
                console.log('属性更新成功:', data);
                
                // ローカルデータの更新
                if (card) {
                    if (action === 'add') {
                        if (!card.attributes) card.attributes = [];
                        card.attributes.push({
                            id: Date.now(), // 一時的なID
                            attribute_type: attributeType,
                            value: 'true'
                        });
                    } else {
                        card.attributes = card.attributes.filter(
                            attr => attr.attribute_type !== attributeType
                        );
                    }
                }
                
                // UI更新
                if (selectedCard && selectedCard.side && selectedCard.lineId) {
                    updateBoard(selectedCard.side);
                }
            },
            error: function(xhr, status, error) {
                console.error('属性更新エラー:', error);
                alert('属性の更新に失敗しました');
            }
        });
    }
    
    // ローカルデータでカードを検索
    function findCardInLocalData(cardId) {
        for (const side of ['left', 'right']) {
            for (const lineId in boardData[side]) {
                const card = boardData[side][lineId].find(c => c.id === cardId);
                if (card) return card;
            }
        }
        return null;
    }
    
    // ローカルデータの属性更新
    function updateCardAttributeInLocalData(cardId, attribute, value) {
        const card = findCardInLocalData(cardId);
        if (card) {
            card[attribute] = value;
        }
    }
    
    // データベースへの保存
    function saveToDatabase() {
        $.ajax({
            url: '/schedule_manager/api/save-to-db/',
            type: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken()
            },
            success: function(data) {
                alert('データベースへの保存が完了しました');
            },
            error: function(xhr, status, error) {
                console.error('DB保存エラー:', error);
                alert('データベースへの保存に失敗しました');
            }
        });
    }
    
    // データベースからの読み込み
    function loadFromDatabase() {
        $.ajax({
            url: '/schedule_manager/api/load-from-db/',
            type: 'GET',
            success: function(data) {
                alert('データベースからの読み込みが完了しました');
                // 表示を更新
                if (selectedDate) {
                    loadBoardData();
                }
            },
            error: function(xhr, status, error) {
                console.error('DB読込エラー:', error);
                alert('データベースからの読み込みに失敗しました');
            }
        });
    }
    
    // 初期化
    function init() {
        // カレンダー初期化
        initCalendar();
        
        // ボード初期化
        initBoard();
        
        // カラーピッカー初期化
        initColorPicker();
        
        // コンテキストメニュー初期化
        initContextMenu();
        
        // モーダル初期化
        initModals();
        
        // ドキュメントクリックでコンテキストメニューを閉じる
        $(document).on('click', function() {
            $('#context-menu').hide();
        });
    }
    
    // カラーピッカー初期化
    function initColorPicker() {
        const colorGrid = $('#color-picker-modal .color-grid');
        
        // 色スウォッチ生成
        COLOR_PALETTE.forEach(color => {
            const swatch = $('<div>')
                .addClass('color-swatch')
                .css('background-color', color)
                .data('color', color)
                .on('click', function() {
                    const selectedColor = $(this).data('color');
                    if (selectedCard) {
                        changeCardColor(selectedCard.id, selectedColor);
                    }
                    $('#color-picker-modal').hide();
                });
            
            colorGrid.append(swatch);
        });
        
        // 閉じるボタン
        $('#color-picker-modal .close').on('click', function() {
            $('#color-picker-modal').hide();
        });
    }
    
    // コンテキストメニュー初期化
    function initContextMenu() {
        $('#context-menu li').on('click', function(e) {
            e.stopPropagation();
            
            if (!selectedCard) return;
            
            const action = $(this).data('action');
            
            if (action === 'change-color') {
                $('#color-picker-modal').show();
            } else if (action === 'edit-name') {
                const card = findCardInLocalData(selectedCard.id);
                if (card) {
                    $('#product-name-input').val(card.product_name);
                    $('#edit-card-id').val(selectedCard.id);
                    $('#edit-name-modal').show();
                }
            } else if (action === 'toggle-mixing') {
                toggleCardAttribute(selectedCard.id, 'mixing');
            } else if (action === 'toggle-rapid-fill') {
                toggleCardAttribute(selectedCard.id, 'rapid_fill');
            } else if (action === 'toggle-special-transfer') {
                toggleCardAttribute(selectedCard.id, 'special_transfer');
            } else if (action === 'toggle-icon-6b') {
                toggleCardAttribute(selectedCard.id, 'icon_6b');
            } else if (action === 'toggle-icon-7c') {
                toggleCardAttribute(selectedCard.id, 'icon_7c');
            } else if (action === 'toggle-icon-2c') {
                toggleCardAttribute(selectedCard.id, 'icon_2c');
            }
            
            $('#context-menu').hide();
        });
    }
    
    // モーダル初期化
    function initModals() {
        // 名前編集モーダル
        $('#save-name').on('click', function() {
            const cardId = $('#edit-card-id').val();
            const newName = $('#product-name-input').val().trim();
            
            if (newName) {
                updateProductName(cardId, newName);
            }
            
            $('#edit-name-modal').hide();
        });
        
        // 閉じるボタン
        $('.close-modal, .modal .close').on('click', function() {
            $(this).closest('.modal').hide();
        });
    }
    
    // 公開API
    return {
        init: init
    };
})();

// DOM準備完了時に初期化
$(document).ready(function() {
    ScheduleBoard.init();
});