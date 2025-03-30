/**
 * datepicker.js - カレンダーアイコンによる日付選択機能（最終修正版）
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
                $(`#${activeSide}-date`).text(formatDate(date));
                
                // 選択された日付の予定を表示（左側の場合）
                if (activeSide === 'left' && window.selectedDate !== undefined) {
                    console.log('ボードデータ更新用の日付設定:', date);
                    window.selectedDate = date;
                    
                    // 既存の関数を利用（存在する場合）
                    if (typeof window.loadBoardData === 'function') {
                        window.loadBoardData();
                    }
                }
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
        
        // datepickerの表示位置を設定
        $container.css({
            top: (iconPos.top + $(this).outerHeight()) + 'px',
            left: iconPos.left + 'px',
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
});