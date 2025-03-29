// 日付選択イベントのハンドラー設定
document.addEventListener('DOMContentLoaded', function() {
    // カレンダーの日付クリックイベントを捕捉
    const calendarDays = document.querySelectorAll('.calendar-day');
    calendarDays.forEach(day => {
        day.addEventListener('click', function() {
            const selectedDate = getSelectedDate(this);
            fetchProductData(selectedDate);
        });
    });
});

// 選択された日付の取得
function getSelectedDate(dayElement) {
    // カレンダーの日付要素から日付データを取得
    const day = dayElement.textContent.trim();
    const month = document.getElementById('current-month').textContent.match(/(\d+)月/)[1];
    const year = document.getElementById('current-month').textContent.match(/(\d+)年/)[1];
    
    // YYYYMMDD形式に変換
    return `${year}${month.padStart(2, '0')}${day.padStart(2, '0')}`;
}

// APIから生産予定データの取得
function fetchProductData(dateStr) {
    fetch(`/schedule_manager/api/schedules/?date=${dateStr}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('データ取得エラー');
            }
            return response.json();
        })
        .then(data => {
            // データ取得成功後、カードを生成
            createProductCards(data);
        })
        .catch(error => {
            console.error('データ取得エラー:', error);
            alert('生産予定データの取得に失敗しました');
        });
}

// 製品カードの生成と配置
function createProductCards(products) {
    // 既存のカードをクリア
    clearProductCards();
    
    // 製品データをループして各ラインにカードを生成
    products.forEach(product => {
        const lineId = product.work_center;
        const lineContainer = document.querySelector(`[data-line-id="${lineId}"]`);
        
        if (lineContainer) {
            // カード要素の作成
            const card = createCardElement(product);
            lineContainer.appendChild(card);
        }
    });
}

// 製品カード要素の作成
function createCardElement(product) {
    const card = document.createElement('div');
    card.className = 'product-card';
    card.dataset.cardId = product.id;
    card.dataset.workCenter = product.work_center;
    
    // カスタムスタイル（背景色など）
    if (product.display_color) {
        card.style.backgroundColor = product.display_color;
    }
    
    // カード内容の作成
    const nameElement = document.createElement('div');
    nameElement.className = 'product-name';
    nameElement.textContent = product.product_name;
    
    const detailsElement = document.createElement('div');
    detailsElement.className = 'product-details';
    detailsElement.innerHTML = `
        <span>品番: ${product.product_number}</span>
        <span>品名: ${product.product_name}</span>
        <span>数量: ${product.production_quantity}</span>
    `;
    
    // カードに要素を追加
    card.appendChild(nameElement);
    card.appendChild(detailsElement);
    
    // 特殊属性があれば表示
    if (product.attributes && product.attributes.length > 0) {
        const attributesElement = document.createElement('div');
        attributesElement.className = 'product-attributes';
        
        product.attributes.forEach(attr => {
            const attrElement = document.createElement('span');
            attrElement.className = `product-attribute ${attr.attribute_type}`;
            
            // 属性タイプに応じて表示内容を変更
            switch (attr.attribute_type) {
                case 'mixing':
                    attrElement.textContent = '↻ 連続撹拌';
                    break;
                case 'rapid_fill':
                    attrElement.textContent = '⚡ 早充依頼';
                    break;
                case 'special_transfer':
                    attrElement.textContent = '⚠️ 特急移庫';
                    break;
                // その他の属性タイプも同様に
                default:
                    attrElement.textContent = attr.attribute_type;
            }
            
            attributesElement.appendChild(attrElement);
        });
        
        card.appendChild(attributesElement);
    }
    
    return card;
}

// 製品カードのクリア
function clearProductCards() {
    const lineContainers = document.querySelectorAll('[data-line-id]');
    lineContainers.forEach(container => {
        // 既存のカードを削除
        const existingCards = container.querySelectorAll('.product-card');
        existingCards.forEach(card => card.remove());
    });
}