// ProductionBoard.jsx
import React, { useState, useEffect } from 'react';
import { DndProvider, useDrag, useDrop } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { fetchSchedulesByDate, updateSchedulePosition } from '../api/scheduleApi';

/**
 * 生産予定ボード - メインコンポーネント
 */
const ProductionBoard = ({ selectedDate }) => {
  // selectedDate が指定されていない場合のデフォルト値
  const defaultDate = !selectedDate 
    ? new Date() 
    : new Date(
        parseInt(selectedDate.substring(0, 4)),
        parseInt(selectedDate.substring(4, 6)) - 1,
        parseInt(selectedDate.substring(6, 8))
      );
  
  // 日付データ (左右の日付)
  const [dates, setDates] = useState({
    left: defaultDate,
    right: new Date(new Date(defaultDate).setDate(defaultDate.getDate() + 1))
  });
  // スケジュールデータ
  const [scheduleData, setScheduleData] = useState({
    left: {},
    right: {}
  });
  
  // ローディング状態
  const [loading, setLoading] = useState({
    left: true,
    right: true
  });
  
  // ライン定義 (順番も定義)
  const lines = [
    { id: '200100', name: 'JP1', color: '#952bff' },
    { id: '200201', name: '2A', color: '#f21c36' },
    { id: '200200', name: '2B', color: '#ff68b4' },
    { id: '200202', name: '2C', color: '#ff68b4' },
    { id: '200300', name: 'JP3', color: '#44df60' },
    { id: '200400', name: 'JP4', color: '#00c6c6' },
    { id: '200601', name: '6A', color: '#9b88b9' },
    { id: '200602', name: '6B', color: '#9b88b9' },
    { id: '200700', name: '7A', color: '#3c2dff' },
    { id: '200701', name: '7B', color: '#3c9dff' },
  ];
  
  // 作業者リスト
  const workers = ['磯部', '高橋', '大橋', '大平', '成岡', '塩澤', '坂田', '西井'];
  
  // 日付をYYYYMMDD形式に変換するヘルパー関数
  const formatDateForApi = (date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}${month}${day}`;
  };
  
  // 日付を表示用にフォーマット
  const formatDateForDisplay = (date) => {
    const year = date.getFullYear();
    const month = date.getMonth() + 1;
    const day = date.getDate();
    const weekdays = ['日', '月', '火', '水', '木', '金', '土'];
    const weekday = weekdays[date.getDay()];
    return `${year}年${month}月${day}日(${weekday})`;
  };
  
  // 初期データの読み込み
  useEffect(() => {
    loadScheduleData('left', dates.left);
    loadScheduleData('right', dates.right);
  }, []);
  
  // スケジュールデータを取得
  const loadScheduleData = async (side, date) => {
    try {
      setLoading(prevState => ({ ...prevState, [side]: true }));
      const formattedDate = formatDateForApi(date);
      const data = await fetchSchedulesByDate(formattedDate);
      
      // ライン別にデータをグループ化
      const groupedData = {};
      lines.forEach(line => {
        groupedData[line.id] = data.filter(item => item.work_center === line.id)
          .sort((a, b) => (a.grid_row - b.grid_row || a.grid_column - b.grid_column));
      });
      
      setScheduleData(prevState => ({
        ...prevState,
        [side]: groupedData
      }));
    } catch (error) {
      console.error(`${side}側のデータ取得エラー:`, error);
    } finally {
      setLoading(prevState => ({ ...prevState, [side]: false }));
    }
  };
  
  // 日付変更ハンドラー
  const handleDateChange = (side, newDate) => {
    setDates(prevDates => ({
      ...prevDates,
      [side]: newDate
    }));
    loadScheduleData(side, newDate);
  };
  
  // カードの移動処理
  const moveCard = async (cardId, fromSide, fromLineId, toSide, toLineId, index) => {
    try {
      // APIを呼び出してバックエンドを更新
      await updateSchedulePosition(cardId, {
        side: toSide,
        lineId: toLineId,
        position: index
      });
      
      // フロントエンドの状態も更新
      setScheduleData(prevData => {
        // コピーを作成して変更を加える（イミュータブルに）
        const newData = { ...prevData };
        
        // 移動するカードを見つける
        const card = prevData[fromSide][fromLineId].find(item => item.id === cardId);
        if (!card) return prevData;
        
        // 元の場所からカードを削除
        newData[fromSide] = {
          ...newData[fromSide],
          [fromLineId]: newData[fromSide][fromLineId].filter(item => item.id !== cardId)
        };
        
        // 移動先にカードを追加
        if (!newData[toSide][toLineId]) {
          newData[toSide][toLineId] = [];
        }
        
        // カードのライン情報を更新
        const updatedCard = {
          ...card,
          work_center: toLineId,
          grid_row: index,
          production_date: formatDateForApi(dates[toSide])
        };
        
        // 移動先の配列に挿入
        const newLineCards = [...newData[toSide][toLineId]];
        newLineCards.splice(index, 0, updatedCard);
        
        // インデックスを更新
        newLineCards.forEach((card, idx) => {
          card.grid_row = idx;
        });
        
        newData[toSide] = {
          ...newData[toSide],
          [toLineId]: newLineCards
        };
        
        return newData;
      });
    } catch (error) {
      console.error('カードの移動に失敗:', error);
    }
  };
  
  // カレンダー選択用モーダル表示
  const showCalendarModal = (side) => {
    // カレンダーモーダルの実装（省略）
  };
  
  return (
    <DndProvider backend={HTML5Backend}>
      <div className="production-board">
        {/* ヘッダー部分 */}
        <div className="header-controls">
          <div className="left-controls">
            <button className="btn btn-primary">CSVインポート</button>
            <button className="btn btn-success">DB保存</button>
            <button className="btn btn-success">DB読込</button>
          </div>
        </div>
        
        {/* メインコンテンツ - 左右2画面 */}
        <div className="board-container">
          {/* 左側 */}
          <DateContainer 
            side="left"
            date={dates.left}
            formattedDate={formatDateForDisplay(dates.left)}
            lines={lines}
            scheduleData={scheduleData.left}
            loading={loading.left}
            onDateChange={() => showCalendarModal('left')}
            onMoveCard={moveCard}
            workers={workers}
          />
          
          {/* 右側 */}
          <DateContainer 
            side="right"
            date={dates.right}
            formattedDate={formatDateForDisplay(dates.right)}
            lines={lines}
            scheduleData={scheduleData.right}
            loading={loading.right}
            onDateChange={() => showCalendarModal('right')}
            onMoveCard={moveCard}
            workers={workers}
          />
        </div>
      </div>
    </DndProvider>
  );
};

/**
 * 日付コンテナ - 1日分の予定を表示
 */
const DateContainer = ({ 
  side, date, formattedDate, lines, scheduleData, loading, onDateChange, onMoveCard, workers 
}) => {
  return (
    <div className="date-container">
      <div className="date-header">
        <h2>{formattedDate}</h2>
        <button className="btn btn-calendar" onClick={onDateChange}>
          カレンダー
        </button>
      </div>
      
      {loading ? (
        <div className="loading-spinner">読み込み中...</div>
      ) : (
        <div className="lines-container">
          {lines.map(line => (
            <LineContainer
              key={`${side}-${line.id}`}
              side={side}
              line={line}
              cards={scheduleData[line.id] || []}
              onMoveCard={onMoveCard}
            />
          ))}
        </div>
      )}
      
      {/* 担当者表示 */}
      <div className="workers-container">
        {workers.map((worker, index) => (
          <div key={`${side}-worker-${index}`} className="worker-button">
            {worker}
          </div>
        ))}
      </div>
    </div>
  );
};

/**
 * ラインコンテナ - 1ラインのカードをまとめて表示
 */
const LineContainer = ({ side, line, cards, onMoveCard }) => {
  // ドロップ処理の定義
  const [{ isOver }, drop] = useDrop({
    accept: 'PRODUCT_CARD',
    drop: (item, monitor) => {
      const didDrop = monitor.didDrop();
      if (didDrop) return;
      
      // ドロップ位置に応じて、カードの位置を計算
      onMoveCard(
        item.id,
        item.side,
        item.lineId,
        side,
        line.id,
        cards.length // 最後に追加
      );
    },
    collect: (monitor) => ({
      isOver: monitor.isOver({ shallow: true }),
    }),
  });
  
  return (
    <div 
      ref={drop}
      className={`line-container ${isOver ? 'is-over' : ''}`}
      style={{ 
        backgroundColor: isOver ? '#f0f0f0' : 'white',
        borderColor: line.color
      }}
    >
      <div className="line-header" style={{ backgroundColor: line.color }}>
        {line.name}
      </div>
      <div className="cards-container">
        {cards.map((card, index) => (
          <ProductCard
            key={card.id}
            card={card}
            index={index}
            side={side}
            lineId={line.id}
            onMoveCard={onMoveCard}
          />
        ))}
      </div>
    </div>
  );
};

/**
 * 製品カード - ドラッグ可能な個別の製品
 */
const ProductCard = ({ card, index, side, lineId, onMoveCard }) => {
  // ドラッグの定義
  const [{ isDragging }, drag] = useDrag({
    type: 'PRODUCT_CARD',
    item: { 
      id: card.id,
      side,
      lineId,
      index
    },
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  });
  
  // ドロップの定義（同じライン内での並び替え用）
  const [, drop] = useDrop({
    accept: 'PRODUCT_CARD',
    hover: (item, monitor) => {
      if (!drag) return;
      if (item.id === card.id) return;
      
      // 同じラインの場合は並び替え
      if (item.side === side && item.lineId === lineId) {
        onMoveCard(
          item.id,
          item.side,
          item.lineId,
          side,
          lineId,
          index
        );
        item.index = index;
      }
    }
  });
  
  // カード表示の色を決定（明るさに応じてテキスト色を調整）
  const getBrightness = (hexColor) => {
    const rgb = parseInt(hexColor.substr(1), 16);
    const r = (rgb >> 16) & 0xff;
    const g = (rgb >> 8) & 0xff;
    const b = (rgb >> 0) & 0xff;
    return (r * 299 + g * 587 + b * 114) / 1000;
  };
  
  const cardColor = card.display_color || '#ffffff';
  const textColor = getBrightness(cardColor) > 128 ? '#000000' : '#ffffff';
  
  // ドラッグ参照とドロップ参照を結合
  const dragDropRef = (el) => {
    drag(el);
    drop(el);
  };
  
  return (
    <div
      ref={dragDropRef}
      className={`product-card ${isDragging ? 'is-dragging' : ''}`}
      style={{
        backgroundColor: cardColor,
        color: textColor,
        opacity: isDragging ? 0.5 : 1
      }}
    >
      <div className="product-name">{card.product_name}</div>
      <div className="product-details">
        <span className="product-number">{card.product_number}</span>
        <span className="product-quantity">数量: {card.production_quantity}</span>
      </div>
      {card.attributes && card.attributes.length > 0 && (
        <div className="product-attributes">
          {card.attributes.map(attr => (
            <span key={attr.id} className={`attribute-${attr.attribute_type}`}>
              {attr.attribute_type === 'mixing' && '↻ 連続撹拌'}
              {attr.attribute_type === 'rapid_fill' && '⚡ 早充依頼'}
              {attr.attribute_type === 'special_transfer' && '⚠️ 特急移庫'}
            </span>
          ))}
        </div>
      )}
    </div>
  );
};

export default ProductionBoard;