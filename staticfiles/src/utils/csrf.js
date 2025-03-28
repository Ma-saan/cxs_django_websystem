/**
 * Django CSRFトークン取得用ユーティリティ
 */

// CSRFトークンを取得
export const getCsrfToken = () => {
    // Djangoが設定したCSRFトークンクッキーから値を取得
    const name = 'csrftoken';
    let cookieValue = null;
    
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        // クッキー名がcsrftokenで始まる場合
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    
    return cookieValue;
  };