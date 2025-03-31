/**
 * datepicker.js - カレンダーアイコンによる日付選択機能（修正版）
 */
$(document).ready(function() {
    console.log('datepicker.js: 初期化開始');
    
    // 日本語化設定
    $.datepicker.regional['ja'] = {
        closeText: '閉じる',
        prevText: '前月',
        nextText: '次月',
        currentText: '今日',
        monthNames: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'],
        monthNamesShort: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'],
        dayNames: ['日曜日', '月曜日', '火曜日', '水曜日', '木曜日', '金曜日', '土曜日'],
        dayNamesShort: ['日', '月', '火', '水', '木', '金', '土'],
        dayNamesMin: ['日', '月', '火', '水', '木', '金', '土'],
        weekHeader: '週',
        dateFormat: 'yy/mm/dd',
        firstDay: 0,
        isRTL: false,
        showMonthAfterYear: true,
        yearSuffix: '年'
    };
    $.datepicker.setDefaults($.datepicker.regional['ja']);
    console.log('datepicker.js: 日本語化設定完了');
    
    // 外部datepickerコンテナを作成
    $('body').append('<div id="external-datepicker-container"></div>');
    
    const $container = $('#external-datepicker-container');
    $container.css({
        position: 'absolute',
        zIndex: 9999,
        display: 'none',
        backgroundColor: 'white',
        boxShadow: '0 3px 8px rgba(0,0,0,0.3)',
        borderRadius: '4px'
    });
    
    // 共有datepickerの初期化
    $container.datepicker({
        onSelect: function(dateText) {
            console.log('日付選択:', dateText);
            const date = $(this).datepicker('getDate');
            
            // アクティブな側（左/右）を判断
            const activeSide = $container.data('active-side');
            if (activeSide) {
                // 日付表示を更新
                $(`#${activeSide}-date`).text(formatDate(date));
                
                // カスタムイベントを発行
                $(document).trigger('datepicker:dateSelected', {
                    date: date,
                    side: activeSide,
                    dateText: dateText
                });
                
                console.log(`${activeSide}ボードの日付を ${formatDate(date)} に設定`);
            }
            
            // 選択後に閉じる
            $container.hide();
        }
    });
    
    // カレンダーアイコンクリックイベント
    $('.calendar-icon').on('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        // クリックされたアイコンが左か右かを判断
        const side = $(this).attr('id').startsWith('left') ? 'left' : 'right';
        console.log(`${side}カレンダーアイコンがクリックされました`);
        
        // アイコンの位置を取得
        const iconPos = $(this).offset();
        const iconWidth = $(this).outerWidth();
        const iconHeight = $(this).outerHeight();
        
        // ウィンドウサイズを取得
        const windowWidth = $(window).width();
        const windowHeight = $(window).height();
        
        // datepickerの幅と高さ（おおよその値）
        const datepickerWidth = 300;
        const datepickerHeight = 300;
        
        // X位置の計算 - ウィンドウからはみ出ないように調整
        let leftPos = iconPos.left;
        if (leftPos + datepickerWidth > windowWidth) {
            leftPos = Math.max(0, windowWidth - datepickerWidth - 10);
        }
        
        // Y位置の計算 - アイコンの下に表示、はみ出す場合は上に表示
        let topPos = iconPos.top + iconHeight;
        if (topPos + datepickerHeight > windowHeight) {
            topPos = Math.max(0, iconPos.top - datepickerHeight);
        }
        
        // datepickerの表示位置を設定
        $container.css({
            top: topPos + 'px',
            left: leftPos + 'px',
            display: 'block'
        });
        
        // アクティブサイドを記録
        $container.data('active-side', side);
        
        // 画面タップでdatepickerを閉じる
        $(document).one('click', function() {
            $container.hide();
        });
        
        // datepicker内のクリックはバブリングさせない
        $container.on('click', function(e) {
            e.stopPropagation();
        });
    });
    
    console.log('datepicker.js: 初期化完了');
    
    // 日付フォーマット (表示用)
    function formatDate(date) {
        const year = date.getFullYear();
        const month = date.getMonth() + 1;
        const day = date.getDate();
        const weekdays = ['日', '月', '火', '水', '木', '金', '土'];
        const weekday = weekdays[date.getDay()];
        return `${year}年${month}月${day}日(${weekday})`;
    }
    
    // 初期日付の自動設定（例：今日）
    function setInitialDate() {
        // 保存された日付があればそれを使用、なければ今日の日付
        const today = new Date();
        
        // 左ボードは今日
        $('#left-date').text(formatDate(today));
        $(document).trigger('datepicker:dateSelected', {
            date: today,
            side: 'left'
        });
        
        // 右ボードは明日
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);
        $('#right-date').text(formatDate(tomorrow));
        $(document).trigger('datepicker:dateSelected', {
            date: tomorrow,
            side: 'right'
        });
    }
    
    // ページ読み込み完了後に初期日付を設定
    $(window).on('load', function() {
        setTimeout(setInitialDate, 500); // 少し遅延して他のコンポーネントの初期化が完了してから
    });
});