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

    // ワークセンター配置設定 - 各エリアに配置するラインを定義
    const WORK_CENTER_LAYOUT = {
        topArea: ['200100', '200201', '200200'], // 上段エリア: JP1, 2A, 2B
        bottomArea: ['200300', '200400', '200202'], // 下段エリア: JP3, JP4, 2C
        rightArea: ['200601', '200602', '200700'] // 右側エリア: 6A, 6B, 7A/7B
    };
    
    // APIのwork_centerとクライアントのIDのマッピング
    const workCenterMapping = {
        1: '200100',  // JP1
        2: '200201',  // 2A
        3: '200200',  // 2B
        4: '200202',  // 2C
        5: '200300',  // JP3
        6: '200400',  // JP4
        7: '200601',  // 6A
        8: '200602',  // 6B
        9: '200700',  // 7A/7B
        10: '200700', // 予備
        11: '200700'  // 予備
    };
    
    // 状態変数
    let leftSelectedDate = null;
    let rightSelectedDate = null;
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
    
// ボード初期化関数の修正
function initBoard() {
    console.log('ボード初期化開始...');
    
    // ボードにライン生成
    function createLines(side) {
        const boardSelector = side === 'left' ? '#board-left' : '#board-right';
        console.log(`${side}ボードのライン生成開始`);
        
        // 各エリアの参照を取得
        const topAreaContent = $(`${boardSelector} .layout-left .area-horizontal.area-top .area-content`);
        const bottomAreaContent = $(`${boardSelector} .layout-left .area-horizontal.area-bottom .area-content`);
        const rightAreaContent = $(`${boardSelector} .layout-right .area-vertical.area-right .area-content`);
        
        console.log(`エリア要素確認 - 上段エリア:`, topAreaContent.length > 0);
        console.log(`エリア要素確認 - 下段エリア:`, bottomAreaContent.length > 0);
        console.log(`エリア要素確認 - 右側エリア:`, rightAreaContent.length > 0);
        
        // 各エリアを空にする
        topAreaContent.empty();
        bottomAreaContent.empty();
        rightAreaContent.empty();
        
        // エリアごとにラインを生成
        WORK_CENTERS.forEach(workCenter => {
            console.log(`ワークセンター [${workCenter.id}] ${workCenter.name} のライン生成`);
            
            // このワークセンターをどのエリアに配置するか判定
            let targetArea;
            if (WORK_CENTER_LAYOUT.topArea.includes(workCenter.id)) {
                targetArea = topAreaContent;
                console.log(`${workCenter.name} は上段エリアに配置`);
            } else if (WORK_CENTER_LAYOUT.bottomArea.includes(workCenter.id)) {
                targetArea = bottomAreaContent;
                console.log(`${workCenter.name} は下段エリアに配置`);
            } else if (WORK_CENTER_LAYOUT.rightArea.includes(workCenter.id)) {
                targetArea = rightAreaContent;
                console.log(`${workCenter.name} は右側エリアに配置`);
            } else {
                // どのエリアにも該当しない場合はスキップ
                console.warn(`${workCenter.name} はどのエリアにも配置されません`);
                return;
            }
            
            // ラインコンテナを作成
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
            targetArea.append(lineContainer);
            
            console.log(`${workCenter.name} ラインコンテナを生成しました`);
            
            // sortable初期化
            lineCards.sortable({
                connectWith: '.line-cards',
                placeholder: 'ui-sortable-placeholder',
                update: function(event, ui) {
                    // ドロップ元からは呼ばれないようにする
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
        
        console.log(`${side}ボードのライン生成完了`);
    }
    
    // 左右のボードを初期化
    createLines('left');
    createLines('right');
    
    console.log('ボード初期化完了');
}
    
    // ボードデータ読み込み
    function loadBoardData(side) {
        const selectedDate = side === 'left' ? leftSelectedDate : rightSelectedDate;
        if (!selectedDate) return;
        
        // 日付ヘッダーを更新
        $(`#${side}-date`).text(formatDateForDisplay(selectedDate));
        
        // データ取得
        fetchScheduleData(side, selectedDate);
    }
    
    // スケジュールデータ取得
    function fetchScheduleData(side, date) {
        const formattedDate = formatDateForApi(date);
        
        console.log(`${side}側のデータを取得: ${formattedDate}`);
        
        $.ajax({
            url: `${API_URL}schedules/?date=${formattedDate}`,
            type: 'GET',
            success: function(data) {
                console.log(`${side}ボードデータ取得成功:`, data);
                
                // ライン別にデータをグループ化
                const groupedData = {};
                
                WORK_CENTERS.forEach(workCenter => {
                    // APIから返されるwork_centerの値をマッピング
                    groupedData[workCenter.id] = data.filter(item => {
                        const itemWorkCenterId = workCenterMapping[item.work_center] || String(item.work_center);
                        return itemWorkCenterId === workCenter.id;
                    }).sort((a, b) => (a.grid_row - b.grid_row || a.grid_column - b.grid_column));
                    
                    console.log(`${side}ボード / ${workCenter.name}:`, groupedData[workCenter.id].length, '件のカード');
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
    
// ボード更新関数の修正
function updateBoard(side) {
    const boardSelector = side === 'left' ? '#board-left' : '#board-right';
    
    console.log(`${side}ボードを更新中...`);
    
    // 各ラインのカードを更新
    WORK_CENTERS.forEach(workCenter => {
        // ワークセンターがどのエリアに属するかを判断
        let lineSelector;
        if (WORK_CENTER_LAYOUT.topArea.includes(workCenter.id)) {
            lineSelector = `${boardSelector} .layout-left .area-horizontal.area-top .area-content .line-cards[data-line-id="${workCenter.id}"]`;
        } else if (WORK_CENTER_LAYOUT.bottomArea.includes(workCenter.id)) {
            lineSelector = `${boardSelector} .layout-left .area-horizontal.area-bottom .area-content .line-cards[data-line-id="${workCenter.id}"]`;
        } else if (WORK_CENTER_LAYOUT.rightArea.includes(workCenter.id)) {
            lineSelector = `${boardSelector} .layout-right .area-vertical.area-right .area-content .line-cards[data-line-id="${workCenter.id}"]`;
        } else {
            console.warn(`${workCenter.name}(${workCenter.id})はどのエリアにも配置されていません`);
            return;
        }
        
        // セレクタでライン要素を取得
        const lineCards = $(lineSelector);
        
        if (lineCards.length === 0) {
            console.warn(`ライン要素が見つかりません: ${workCenter.id} (セレクタ: ${lineSelector})`);
            return;
        }
        
        console.log(`${workCenter.name}のライン要素を更新します`);
        
        // 現在のライン内のカードをクリア
        lineCards.empty();
        
        const cards = boardData[side][workCenter.id] || [];
        console.log(`${side}ボード/${workCenter.name}: ${cards.length}件のカード`);
        
        // カードがない場合のメッセージ
        if (cards.length === 0) {
            lineCards.append('<div class="no-card-message">データがありません</div>');
            return;
        }
        
        // カードを追加
        cards.forEach(card => {
            const cardElement = createCardElement(card, side);
            lineCards.append(cardElement);
        });
    });
    
    console.log(`${side}ボードの更新完了`);
}
    
    // カード要素の作成
    function createCardElement(card, side) {
        let cardColor = card.display_color || '#ffffff';
        
        // 色形式の検証と修正
        if (!cardColor || typeof cardColor !== 'string') {
            cardColor = '#ffffff'; // デフォルト色
        } else if (!cardColor.startsWith('#')) {
            // #が付いていない場合は追加
            cardColor = '#' + cardColor;
        }
        
        // テキスト色の決定（背景が明るいか暗いかで）
        const getBrightness = (hexColor) => {
            try {
                if (!hexColor || !hexColor.startsWith('#') || hexColor.length < 4) {
                    return 255; // 異常値の場合は黒テキスト
                }
                
                // #RGBを#RRGGBBに変換
                if (hexColor.length === 4) {
                    const r = hexColor.charAt(1);
                    const g = hexColor.charAt(2);
                    const b = hexColor.charAt(3);
                    hexColor = `#${r}${r}${g}${g}${b}${b}`;
                }
                
                const rgb = parseInt(hexColor.substring(1), 16);
                const r = (rgb >> 16) & 0xff;
                const g = (rgb >> 8) & 0xff;
                const b = (rgb >> 0) & 0xff;
                return (r * 299 + g * 587 + b * 114) / 1000;
            } catch (e) {
                console.warn('色変換エラー:', hexColor, e);
                return 255; // エラー時は黒テキスト
            }
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
            .text(card.product_name || '名称不明');
        
        const detailsElement = $('<div>')
            .addClass('product-details')
            .append(
                $('<span>').addClass('product-number').text(`品番: ${card.product_number || 'なし'}`),
                $('<span>').addClass('product-quantity').text(`数量: ${card.production_quantity || 0}`)
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
                    date: formatDateForApi(side === 'left' ? leftSelectedDate : rightSelectedDate)
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
                loadBoardData(side);
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
    
    // 初期化
    function init() {
        // schedule_board.jsのinit関数内に追加
$(document).on('datepicker:dateSelected', function(e, data) {
    if (data.side === 'left') {
        leftSelectedDate = data.date;
        loadBoardData('left');
    } else if (data.side === 'right') {
        rightSelectedDate = data.date;
        loadBoardData('right');
    }
});
        
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
        init: init,
        // デバッグ機能
        debug: {
            loadDate: function(dateStr, side = 'left') {
                const year = parseInt(dateStr.substring(0, 4));
                const month = parseInt(dateStr.substring(4, 6)) - 1;
                const day = parseInt(dateStr.substring(6, 8));
                const date = new Date(year, month, day);
                
                if (side === 'left') {
                    leftSelectedDate = date;
                    loadBoardData('left');
                } else {
                    rightSelectedDate = date;
                    loadBoardData('right');
                }
                return true;
            },
            showData: function() {
                console.log('ボードデータ:', boardData);
                return boardData;
            },
            // テストカードを作成
            createTestCard: function(side, lineId) {
                const boardSelector = side === 'left' ? '#board-left' : '#board-right';
                const lineCards = $(`${boardSelector} .production-lines .line-cards[data-line-id="${lineId}"]`);
                
                if (lineCards.length === 0) {
                    return `ライン ${lineId} が見つかりません`;
                }
                
                const testCard = {
                    id: 'test-' + Date.now(),
                    product_name: 'テスト製品',
                    product_number: 'TEST-001',
                    production_quantity: 100,
                    work_center: lineId,
                    display_color: '#ffff00'
                };
                
                const cardElement = createCardElement(testCard, side);
                lineCards.append(cardElement);
                
                return `${side}ボードの${lineId}ラインにテストカードを追加しました`;
            },
            // レイアウト確認
            checkLayout: function() {
                const leftLines = $('#board-left .production-lines .line-cards');
                const rightLines = $('#board-right .production-lines .line-cards');
                
                console.log('左ボードのライン数:', leftLines.length);
                console.log('右ボードのライン数:', rightLines.length);
                
                leftLines.each(function() {
                    console.log('左ライン ID:', $(this).data('line-id'));
                });
                
                return `左ボード: ${leftLines.length}ライン, 右ボード: ${rightLines.length}ライン`;
            }
        }
    };
})();

// DOM準備完了時に初期化
$(document).ready(function() {
    ScheduleBoard.init();
});