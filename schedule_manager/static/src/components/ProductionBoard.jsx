import React, { useState, useEffect, useRef } from 'react';
import { DndProvider, useDrag, useDrop } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { fetchSchedulesByDate, updateSchedulePosition, updateScheduleAttribute } from '../api/scheduleApi';
import './ProductionBoard.css';

// カラーパレット定義
const COLOR_PALETTE = [
  "#ffff09", "#ffffc4", "#a1ff84", "#00fb00", "#00ffff", "#00c1c1", 
  "#ff8000", "#ffd481", "#8080ff", "#ccccff", "#ff80ff", "#ffdcff", 
  "#cb9696", "#a1e6ff", "#b3b3b3", "#ffffff"
];

const ProductionBoard = ({ selectedDate }) => {
  // 日付フォーマットと状態管理
  const defaultDate = !selectedDate 
    ? new Date() 
    : new Date(
        parseInt(selectedDate.substring(0, 4)),
        parseInt(selectedDate.substring(4, 6)) - 1,
        parseInt(selectedDate.substring(6, 8))
      );
  
  // 状態管理
  const [dates, setDates] = useState({
    left: defaultDate,
    right: new Date(new Date(defaultDate).setDate(defaultDate.getDate() + 1))
  });
  const [scheduleData, setScheduleData] = useState({ left: {}, right: {} });
  const [loading, setLoading] = useState({ left: true, right: true });
  const [activeCard, setActiveCard] = useState(null);
  const [showColorPicker, setShowColorPicker] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const colorPickerRef = useRef(null);
  
  // ライン定義
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
  
  // 特殊属性アイコン定義
  const attributeIcons = {
    mixing: { label: '連続撹拌', icon: '↻' },
    rapid_fill: { label: '早充依頼', icon: '⚡' },
    special_transfer: { label: '特急移庫', icon: '⚠️' },
    icon_6b: { label: '6B', icon: '6B' },
    icon_7c: { label: '7C', icon: '7C' },
    icon_2c: { label: '2C', icon: '2C' }
  };
  
  // 日付フォーマットヘルパー関数
  const formatDateForApi = (date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}${month}${day}`;
  };
  
  const formatDateForDisplay = (date) => {
    const year = date.getFullYear();
    const month = date.getMonth() + 1;
    const day = date.getDate();
    const weekdays = ['日', '月', '火', '水', '木', '金', '土'];
    const weekday = weekdays[date.getDay()];
    return `${year}年${month}月${day}日(${weekday})`;
  };
  
  // データ読み込み
  useEffect(() => {
    loadScheduleData('left', dates.left);
    loadScheduleData('right', dates.right);
    
    // カラーピッカー外クリック時の処理
    const handleClickOutside = (event) => {
      if (colorPickerRef.current && !colorPickerRef.current.contains(event.target)) {
        setShowColorPicker(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);
  
  // スケジュールデータ取得
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
        position: index,
        date: formatDateForApi(dates[toSide])
      });
      
      // フロントエンドの状態も更新
      setScheduleData(prevData => {
        const newData = { ...prevData };
        
        // 移動するカードを見つける
        const card = prevData[fromSide][fromLineId]?.find(item => item.id === cardId);
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
  
  // カードの色変更
  const handleColorChange = async (cardId, side, lineId, newColor) => {
    try {
      // API呼び出し
      await updateScheduleAttribute(cardId, { display_color: newColor });
      
      // UI更新
      setScheduleData(prevData => {
        const newData = { ...prevData };
        const cards = [...newData[side][lineId]];
        const cardIndex = cards.findIndex(card => card.id === cardId);
        
        if (cardIndex !== -1) {
          cards[cardIndex] = { ...cards[cardIndex], display_color: newColor };
          newData[side] = {
            ...newData[side],
            [lineId]: cards
          };
        }
        
        return newData;
      });
      
      setShowColorPicker(false);
    } catch (error) {
      console.error('色変更に失敗:', error);
    }
  };
  
  // 特殊属性の切り替え
  const toggleAttribute = async (cardId, side, lineId, attributeType) => {
    try {
      const card = scheduleData[side][lineId].find(card => card.id === cardId);
      const hasAttribute = card.attributes?.some(attr => attr.attribute_type === attributeType);
      
      // API呼び出し
      await updateScheduleAttribute(cardId, { 
        attribute_action: hasAttribute ? 'remove' : 'add',
        attribute_type: attributeType 
      });
      
      // UI更新
      setScheduleData(prevData => {
        const newData = { ...prevData };
        const cards = [...newData[side][lineId]];
        const cardIndex = cards.findIndex(card => card.id === cardId);
        
        if (cardIndex !== -1) {
          const attributes = [...(cards[cardIndex].attributes || [])];
          
          if (hasAttribute) {
            // 属性を削除
            cards[cardIndex] = { 
              ...cards[cardIndex], 
              attributes: attributes.filter(attr => attr.attribute_type !== attributeType)
            };
          } else {
            // 属性を追加
            cards[cardIndex] = { 
              ...cards[cardIndex], 
              attributes: [...attributes, { id: Date.now(), attribute_type: attributeType, value: 'true' }]
            };
          }
          
          newData[side] = {
            ...newData[side],
            [lineId]: cards
          };
        }
        
        return newData;
      });
    } catch (error) {
      console.error('属性変更に失敗:', error);
    }
  };
  
  // 製品名編集
  const handleProductNameEdit = async (cardId, side, lineId, newName) => {
    try {
      // API呼び出し
      await updateScheduleAttribute(cardId, { product_name: newName });
      
      // UI更新
      setScheduleData(prevData => {
        const newData = { ...prevData };
        const cards = [...newData[side][lineId]];
        const cardIndex = cards.findIndex(card => card.id === cardId);
        
        if (cardIndex !== -1) {
          cards[cardIndex] = { ...cards[cardIndex], product_name: newName };
          newData[side] = {
            ...newData[side],
            [lineId]: cards
          };
        }
        
        return newData;
      });
      
      setShowEditModal(false);
    } catch (error) {
      console.error('製品名編集に失敗:', error);
    }
  };
  
  // 作業者選択
  const handleWorkerSelect = (worker, side) => {
    // 作業者状態を更新
    // この機能は元のアプリでは別のUIで管理されていた可能性があるため、
    // カスタム実装が必要かもしれません
  };
  
  // カラーピッカーモーダル
  const ColorPickerModal = ({ onSelect, onClose }) => (
    <div className="color-picker-modal" ref={colorPickerRef}>
      <div className="color-picker-header">
        <h3>色を選択</h3>
        <button className="close-button" onClick={onClose}>×</button>
      </div>
      <div className="color-grid">
        {COLOR_PALETTE.map(color => (
          <div 
            key={color} 
            className="color-swatch" 
            style={{ backgroundColor: color }}
            onClick={() => onSelect(color)}
          />
        ))}
      </div>
    </div>
  );
  
  // カレンダー選択モーダル (実装省略 - 別機能として実装予定)
  const showCalendarModal = (side) => {
    // カレンダーモーダルの実装
  };
  
  return (
    <DndProvider backend={HTML5Backend}>
      <div className="production-board">
        {/* ヘッダー部分 */}
        <div className="header-controls">
          <div className="left-controls">
            <a href="/schedule_manager/import-csv/" className="btn btn-primary">CSVインポート</a>
            <button className="btn btn-success" onClick={() => alert('DBへの保存処理を実装')}>DB保存</button>
            <button className="btn btn-success" onClick={() => alert('DBからの読込処理を実装')}>DB読込</button>
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
            onWorkerSelect={(worker) => handleWorkerSelect(worker, 'left')}
            onColorChange={handleColorChange}
            onToggleAttribute={toggleAttribute}
            onProductNameEdit={handleProductNameEdit}
            setActiveCard={setActiveCard}
            setShowColorPicker={setShowColorPicker}
            setShowEditModal={setShowEditModal}
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
            onWorkerSelect={(worker) => handleWorkerSelect(worker, 'right')}
            onColorChange={handleColorChange}
            onToggleAttribute={toggleAttribute}
            onProductNameEdit={handleProductNameEdit}
            setActiveCard={setActiveCard}
            setShowColorPicker={setShowColorPicker}
            setShowEditModal={setShowEditModal}
          />
        </div>
        
        {/* モーダル類 */}
        {showColorPicker && activeCard && (
          <ColorPickerModal 
            onSelect={(color) => handleColorChange(
              activeCard.id, 
              activeCard.side, 
              activeCard.lineId, 
              color
            )}
            onClose={() => setShowColorPicker(false)}
          />
        )}
        
        {showEditModal && activeCard && (
          <EditNameModal 
            card={scheduleData[activeCard.side][activeCard.lineId].find(c => c.id === activeCard.id)}
            onSave={(newName) => handleProductNameEdit(
              activeCard.id,
              activeCard.side,
              activeCard.lineId,
              newName
            )}
            onClose={() => setShowEditModal(false)}
          />
        )}
      </div>
    </DndProvider>
  );
};

// 編集モーダル
const EditNameModal = ({ card, onSave, onClose }) => {
  const [name, setName] = useState(card?.product_name || '');
  
  const handleSubmit = (e) => {
    e.preventDefault();
    if (name.trim()) {
      onSave(name.trim());
    }
  };
  
  return (
    <div className="edit-modal">
      <div className="edit-modal-content">
        <div className="edit-modal-header">
          <h3>製品名編集</h3>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="edit-name-input"
            placeholder="製品名を入力"
            autoFocus
          />
          <div className="edit-modal-actions">
            <button type="button" className="btn btn-secondary" onClick={onClose}>キャンセル</button>
            <button type="submit" className="btn btn-primary">保存</button>
          </div>
        </form>
      </div>
    </div>
  );
};

// 日付コンテナコンポーネント
const DateContainer = ({ 
  side, date, formattedDate, lines, scheduleData, loading,
  onDateChange, onMoveCard, workers, onWorkerSelect,
  onColorChange, onToggleAttribute, onProductNameEdit,
  setActiveCard, setShowColorPicker, setShowEditModal
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
              onColorChange={onColorChange}
              onToggleAttribute={onToggleAttribute}
              onProductNameEdit={onProductNameEdit}
              setActiveCard={setActiveCard}
              setShowColorPicker={setShowColorPicker}
              setShowEditModal={setShowEditModal}
            />
          ))}
        </div>
      )}
      
      {/* 担当者表示 */}
      <div className="workers-container">
        {workers.map((worker, index) => (
          <div 
            key={`${side}-worker-${index}`}
            className="worker-button"
            onClick={() => onWorkerSelect(worker)}
          >
            {worker}
          </div>
        ))}
        <div className="worker-button worker-clear">クリア</div>
      </div>
    </div>
  );
};

// ラインコンテナコンポーネント
const LineContainer = ({ 
  side, line, cards, onMoveCard,
  onColorChange, onToggleAttribute, onProductNameEdit,
  setActiveCard, setShowColorPicker, setShowEditModal
}) => {
  // ドロップ処理
  const [{ isOver }, drop] = useDrop({
    accept: 'PRODUCT_CARD',
    drop: (item, monitor) => {
      const didDrop = monitor.didDrop();
      if (didDrop) return;
      
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
            onColorChange={onColorChange}
            onToggleAttribute={onToggleAttribute}
            onProductNameEdit={onProductNameEdit}
            setActiveCard={setActiveCard}
            setShowColorPicker={setShowColorPicker}
            setShowEditModal={setShowEditModal}
          />
        ))}
      </div>
    </div>
  );
};

// 製品カードコンポーネント
const ProductCard = ({ 
  card, index, side, lineId, onMoveCard,
  onColorChange, onToggleAttribute, onProductNameEdit,
  setActiveCard, setShowColorPicker, setShowEditModal
}) => {
  // コンテキストメニュー状態
  const [showContextMenu, setShowContextMenu] = useState(false);
  const [contextMenuPos, setContextMenuPos] = useState({ x: 0, y: 0 });
  
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
  
  // ドロップの定義
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
  
  // 色の明るさに基づくテキスト色の決定
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
  
  // コンテキストメニュー表示
  const handleContextMenu = (e) => {
    e.preventDefault();
    setContextMenuPos({ x: e.clientX, y: e.clientY });
    setShowContextMenu(true);
    setActiveCard({ id: card.id, side, lineId });
  };
  
  // 色変更モーダル表示
  const handleColorChangeClick = () => {
    setActiveCard({ id: card.id, side, lineId });
    setShowColorPicker(true);
    setShowContextMenu(false);
  };
  
  // 名前編集モーダル表示
  const handleNameEditClick = () => {
    setActiveCard({ id: card.id, side, lineId });
    setShowEditModal(true);
    setShowContextMenu(false);
  };
  
  // 特殊属性トグル
  const handleToggleAttribute = (attributeType) => {
    onToggleAttribute(card.id, side, lineId, attributeType);
    setShowContextMenu(false);
  };
  
  // 属性の確認
  const hasAttribute = (attributeType) => {
    return card.attributes?.some(attr => attr.attribute_type === attributeType);
  };
  
  return (
    <>
      <div
        ref={dragDropRef}
        className={`product-card ${isDragging ? 'is-dragging' : ''}`}
        style={{
          backgroundColor: cardColor,
          color: textColor,
          opacity: isDragging ? 0.5 : 1
        }}
        onContextMenu={handleContextMenu}
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
                {attr.attribute_type === 'icon_6b' && '6B'}
                {attr.attribute_type === 'icon_7c' && '7C'}
                {attr.attribute_type === 'icon_2c' && '2C'}
              </span>
            ))}
          </div>
        )}
      </div>
      
      {/* コンテキストメニュー */}
      {showContextMenu && (
        <div 
          className="context-menu" 
          style={{ 
            position: 'fixed', 
            top: contextMenuPos.y, 
            left: contextMenuPos.x 
          }}
        >
          <ul>
            <li onClick={handleColorChangeClick}>色変更</li>
            <li onClick={handleNameEditClick}>名前編集</li>
            <li onClick={() => handleToggleAttribute('mixing')}>
              {hasAttribute('mixing') ? '✓ ' : ''}連続撹拌
            </li>
            <li onClick={() => handleToggleAttribute('rapid_fill')}>
              {hasAttribute('rapid_fill') ? '✓ ' : ''}早充依頼
            </li>
            <li onClick={() => handleToggleAttribute('special_transfer')}>
              {hasAttribute('special_transfer') ? '✓ ' : ''}特急移庫
            </li>
            <li onClick={() => handleToggleAttribute('icon_6b')}>
              {hasAttribute('icon_6b') ? '✓ ' : ''}6B表示
            </li>
            <li onClick={() => handleToggleAttribute('icon_7c')}>
              {hasAttribute('icon_7c') ? '✓ ' : ''}7C表示
            </li>
            <li onClick={() => handleToggleAttribute('icon_2c')}>
              {hasAttribute('icon_2c') ? '✓ ' : ''}2C表示
            </li>
          </ul>
        </div>
      )}
    </>
  );
};

export default ProductionBoard;