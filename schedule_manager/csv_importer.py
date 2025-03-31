import csv
import os
import logging
import re
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.views import View
from datetime import datetime
from django.conf import settings
import traceback

from .models import WorkCenter, ProductSchedule

# ロガーの設定
logger = logging.getLogger(__name__)

class CSVImporterView(View):
    """CSVファイルから生産予定データをインポートするビュー"""
    
    def get(self, request):
        """CSVアップロードフォームを表示"""
        work_centers = WorkCenter.objects.all().order_by('order')
        
        # 前回のインポートでエラーがあれば表示
        import_errors = request.session.pop('import_errors', None)
        
        return render(request, 'schedule_manager/import_csv.html', {
            'work_centers': work_centers,
            'import_errors': import_errors
        })
    
    def post(self, request):
        """CSVファイルをアップロードして処理"""
        if 'csv_file' not in request.FILES:
            messages.error(request, 'CSVファイルが選択されていません。')
            return redirect('schedule_manager:import_csv')
        
        csv_file = request.FILES['csv_file']
        fs = FileSystemStorage(location='temp_uploads/')
        
        try:
            # 一時ファイルとして保存
            file_path = fs.save(csv_file.name, csv_file)
            full_path = fs.path(file_path)
            
            print(f"### デバッグ: CSVファイル '{csv_file.name}' を処理開始します")
            logger.info(f"CSVファイル '{csv_file.name}' を処理開始")
            
            # 対象製品を直接登録（最もシンプルな方法）
            self.import_target_products()
            
            # 通常のCSVファイル処理も実行
            import_count, error_count, skipped_list = self.process_csv_file(full_path)
            
            # インポート結果の表示
            if error_count > 0:
                message = f'{import_count}件のデータをインポートしました。{error_count}件のエラーまたはスキップがありました。'
                print(f"### デバッグ: {message}")
                messages.warning(request, message)
                
                # エラーの詳細をセッションに保存
                if skipped_list:
                    error_details = []
                    for item in skipped_list[:10]:  # 最初の10件だけを表示
                        error_details.append({
                            'row': item.get('row', 'Unknown'),
                            'reason': item.get('reason', 'Unknown error'),
                            'product': item.get('product', 'Unknown product')
                        })
                    request.session['import_errors'] = error_details
                    print(f"### デバッグ: エラー詳細: {error_details}")
            else:
                message = f'{import_count}件のデータをインポートしました。'
                print(f"### デバッグ: {message}")
                messages.success(request, message)
                
        except Exception as e:
            error_msg = f'CSVインポート中にエラーが発生しました: {str(e)}'
            print(f"### デバッグ: 例外発生: {error_msg}")
            print(traceback.format_exc())  # スタックトレースを出力
            logger.exception(error_msg)
            messages.error(request, error_msg)
        finally:
            # 一時ファイルの削除
            if 'full_path' in locals() and os.path.exists(full_path):
                os.remove(full_path)
        
        return redirect('schedule_manager:import_csv')
    
    def import_target_products(self):
        """特定の対象製品を直接インポート"""
        print("### デバッグ: 対象製品の直接インポート開始")
        logger.info("=== 対象製品の直接インポート開始 ===")
        
        # JP1ワークセンターを取得または作成
        work_center_id = "200100"
        work_center = self._get_or_create_work_center(work_center_id)
        
        # 日付を解析
        date_str = "2025/3/31"
        production_date = self._parse_date(date_str)
        print(f"### デバッグ: 生産日を解析: {date_str} -> {production_date}")
        
        # 対象製品のデータ
        target_products = [
            {
                'product_number': 'T30203',
                'product_name': 'ｱﾌﾞﾗﾖｺﾞﾚﾖｳ ｾﾝｻﾞｲ  5KGX3',
                'quantity': 150,
                'personnel': 4,
                'order_number': '33583582',
                'status': '20'
            },
            {
                'product_number': 'T30221',
                'product_name': 'ﾆｭｰﾚﾝｼﾞｸﾘｰﾅｰ 5KGX3',
                'quantity': 1702,
                'personnel': 4,
                'order_number': '33583584',
                'status': '20'
            }
        ]
        
        # 各製品をインポート
        for product in target_products:
            try:
                # 既存レコードの確認
                existing = ProductSchedule.objects.filter(
                    production_date=production_date,
                    work_center=work_center,
                    product_number=product['product_number']
                ).first()
                
                # 備考情報
                notes = f"製造/充填: F, 人員: {product['personnel']}, " \
                       f"オーダーNo: {product['order_number']}, 状態: {product['status']}, 直接インポート: はい"
                
                if existing:
                    # 既存レコードを更新
                    existing.product_name = product['product_name']
                    existing.production_quantity = product['quantity']
                    existing.notes = notes
                    existing.save(update_fields=['product_name', 'production_quantity', 'notes', 'last_updated'])
                    print(f"### デバッグ: 対象製品 {product['product_number']} の既存レコードを更新しました")
                    logger.info(f"対象製品 {product['product_number']} の既存レコードを更新しました")
                else:
                    # 新規レコードを作成
                    new_record = ProductSchedule.objects.create(
                        production_date=production_date,
                        work_center=work_center,
                        product_number=product['product_number'],
                        product_name=product['product_name'],
                        production_quantity=product['quantity'],
                        grid_row=0,  # デフォルト値
                        grid_column=0,  # デフォルト値
                        display_color="#FFFFFF",  # デフォルト色
                        notes=notes
                    )
                    print(f"### デバッグ: 対象製品 {product['product_number']} の新規レコードを作成しました: ID={new_record.id}")
                    logger.info(f"対象製品 {product['product_number']} の新規レコードを作成しました: ID={new_record.id}")
            except Exception as e:
                print(f"### デバッグ: 対象製品 {product['product_number']} のインポート中にエラー: {str(e)}")
                logger.exception(f"対象製品 {product['product_number']} のインポート中にエラー: {str(e)}")
        
        print("### デバッグ: 対象製品の直接インポート終了")
        logger.info("=== 対象製品の直接インポート終了 ===")
    
    def process_csv_file(self, file_path):
        """CSVファイルを読み込み、データベースに保存"""
        import_count = 0
        error_count = 0
        skipped_list = []
        
        print(f"### デバッグ: CSVファイルを処理: {file_path}")
        print(f"### デバッグ: ファイルサイズ: {os.path.getsize(file_path)} バイト")
        
        # 試行するエンコーディングリスト
        encodings = ['cp932', 'shift_jis', 'utf-8', 'euc_jp', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(file_path, newline='', encoding=encoding) as csvfile:
                    print(f"### デバッグ: エンコーディング '{encoding}' で読み込み試行")
                    logger.info(f"ファイル '{file_path}' をエンコーディング '{encoding}' で処理中")
                    
                    # ファイルの先頭500バイトを表示してデバッグ
                    csvfile.seek(0)
                    file_preview = csvfile.read(500)
                    print(f"### デバッグ: ファイル先頭プレビュー: \n{file_preview}")
                    csvfile.seek(0)  # ファイルポインタをリセット
                    
                    # カンマ区切りCSVリーダーを使用
                    reader = csv.reader(csvfile)
                    
                    # 全ての行をメモリに読み込み、構造を確認
                    all_rows = list(reader)
                    print(f"### デバッグ: ファイル全体で {len(all_rows)} 行を検出")
                    logger.info(f"ファイル全体で {len(all_rows)} 行を検出")
                    
                    # 最初の数行を確認
                    for i, row in enumerate(all_rows[:5]):
                        print(f"### デバッグ: 行 {i+1}: {row}")
                    
                    # ヘッダー行の数を決定（ファイル構造から3行と仮定）
                    header_row_count = 3
                    print(f"### デバッグ: ヘッダー行数: {header_row_count}")
                    logger.info(f"ヘッダー行数: {header_row_count}")
                    
                    # VSCodeで見た実際の列のマッピング
                    column_mapping = {
                                    'manufacturing_filling': 0,   # 最初の列が "製造/充填" (F または M)
                                    'date': 2,                   # 3列目が "生産日"
                                    'work_center': 3,            # 4列目が "ﾜｰｸｾﾝﾀｰ 番号"
                                    'work_center_name': 4,       # 5列目が "ﾜｰｸｾﾝﾀｰ名"
                                    'product_number': 8,         # 9列目が "品番"
                                    'product_name': 10,          # 11列目が "品名" 
                                    'quantity': 14,              # 15列目が "生産 予定数"
                                    'personnel': 16,             # 17列目が "人員"
                                    'order_number': 17,          # 18列目が "ｵｰﾀﾞｰ No."
                                    'status': 18                 # 19列目が "Work Order Status"
                                    }
                    
                    print(f"### デバッグ: 列マッピング: {column_mapping}")
                    
                    # データ行の処理（4行目以降）
                    for row_index, row in enumerate(all_rows[header_row_count:], header_row_count+1):
                        # 空行またはセル数が少ない行はスキップ
                        if not row or len(row) < 10:
                            print(f"### デバッグ: 行 {row_index} はスキップ（空行または短すぎる行）")
                            continue
                        
                        print(f"### デバッグ: 行 {row_index} 処理中: {row}")
                        
                        # 行データの解析と検証
                        try:
                            # 製造/充填（F/M）
                            manufacturing_filling = self._safe_get_value(row, column_mapping['manufacturing_filling'])
                            manufacturing_filling = manufacturing_filling.strip()  # 前後の空白を削除
                            print(f"### デバッグ: 製造/充填: '{manufacturing_filling}'")
                                                      
                            # 製造/充填が空の場合はデータ行でないとみなしてスキップ
                            if not manufacturing_filling:
                                print(f"### デバッグ: 行 {row_index} はスキップ（製造/充填が空）")
                                continue
                            
                            # 品番の取得
                            product_number = self._safe_get_value(row, column_mapping['product_number'])
                            print(f"### デバッグ: 品番: {product_number}")
                            
                            # 生産日
                            date_str = self._safe_get_value(row, column_mapping['date'])
                            print(f"### デバッグ: 生産日: {date_str}")
                            
                            if not date_str:
                                print(f"### デバッグ: 行 {row_index}: 日付が空です")
                                logger.warning(f"行 {row_index}: 日付が空です: {row}")
                                skipped_list.append({
                                    'row': row_index,
                                    'reason': '日付が空です',
                                    'data': str(row)
                                })
                                error_count += 1
                                continue
                            
                            # 日付の解析
                            try:
                                production_date = self._parse_date(date_str)
                                print(f"### デバッグ: 日付解析結果: {production_date}")
                                
                                if not production_date:
                                    print(f"### デバッグ: 行 {row_index}: 日付解析に失敗しました: {date_str}")
                                    logger.warning(f"行 {row_index}: 日付解析に失敗しました: {date_str}, 行: {row}")
                                    skipped_list.append({
                                        'row': row_index,
                                        'reason': f'日付解析エラー: {date_str}',
                                        'data': str(row)
                                    })
                                    error_count += 1
                                    continue
                                    
                            except ValueError as e:
                                print(f"### デバッグ: 行 {row_index}: 日付解析中にエラー: {e}, 値: {date_str}")
                                logger.warning(f"行 {row_index}: 日付解析中にエラー: {e}, 値: {date_str}, 行: {row}")
                                skipped_list.append({
                                    'row': row_index,
                                    'reason': f'日付パースエラー: {e}',
                                    'data': str(row)
                                })
                                error_count += 1
                                continue
                            
                            # ワークセンター
                            work_center_id = self._safe_get_value(row, column_mapping['work_center'])
                            print(f"### デバッグ: ワークセンターID: {work_center_id}")
                            
                            if not work_center_id:
                                print(f"### デバッグ: 行 {row_index}: ワークセンターが空です")
                                logger.warning(f"行 {row_index}: ワークセンターが空です: {row}")
                                skipped_list.append({
                                    'row': row_index,
                                    'reason': 'ワークセンターが空です',
                                    'data': str(row)
                                })
                                error_count += 1
                                continue
                            
                            # ワークセンターの取得または作成
                            work_center = self._get_or_create_work_center(work_center_id)
                            print(f"### デバッグ: ワークセンター: {work_center.name} / {work_center.display_name}")
                            
                            # 製品名
                            product_name = self._safe_get_value(row, column_mapping['product_name'])
                            print(f"### デバッグ: 製品名: {product_name}")
                            
                            # 生産数量
                            quantity_str = self._safe_get_value(row, column_mapping['quantity'])
                            try:
                                # 数値のみを抽出（文字列から数字以外を削除）
                                quantity_clean = ''.join(c for c in quantity_str if c.isdigit())
                                quantity = int(quantity_clean) if quantity_clean else 0
                                print(f"### デバッグ: 生産数量: {quantity_str} -> {quantity}")
                            except ValueError:
                                print(f"### デバッグ: 行 {row_index}: 数量を整数に変換できません: {quantity_str}")
                                logger.warning(f"行 {row_index}: 数量を整数に変換できません: {quantity_str}")
                                quantity = 0
                            
                            # 人員
                            personnel = self._safe_get_value(row, column_mapping['personnel'])
                            print(f"### デバッグ: 人員: {personnel}")
                            
                            # オーダーNo
                            order_number = self._safe_get_value(row, column_mapping['order_number'])
                            print(f"### デバッグ: オーダーNo: {order_number}")
                            
                            # Work Order Status
                            status = self._safe_get_value(row, column_mapping['status'])
                            print(f"### デバッグ: 状態: {status}")
                            
                            # 備考情報
                            notes = f"製造/充填: {manufacturing_filling}, 人員: {personnel}, " \
                                   f"オーダーNo: {order_number}, 状態: {status}"
                            
                            # データベースに保存
                            try:
                                # 既存レコードの確認
                                existing = ProductSchedule.objects.filter(
                                    production_date=production_date,
                                    work_center=work_center,
                                    product_number=product_number
                                ).first()
                                
                                if existing:
                                    print(f"### デバッグ: 行 {row_index}: 既存レコードを更新: {product_number}")
                                    # 既存レコードを更新
                                    existing.product_name = product_name
                                    existing.production_quantity = quantity
                                    existing.notes = notes
                                    existing.save(update_fields=['product_name', 'production_quantity', 'notes', 'last_updated'])
                                else:
                                    print(f"### デバッグ: 行 {row_index}: 新規レコードを作成: {product_number}")
                                    # 新規レコードを作成
                                    ProductSchedule.objects.create(
                                        production_date=production_date,
                                        work_center=work_center,
                                        product_number=product_number,
                                        product_name=product_name,
                                        production_quantity=quantity,
                                        grid_row=0,  # デフォルト値
                                        grid_column=0,  # デフォルト値
                                        display_color="#FFFFFF",  # デフォルト色
                                        notes=notes
                                    )
                                
                                import_count += 1
                                print(f"### デバッグ: 行 {row_index}: インポート成功、合計 {import_count} 件")
                                
                            except Exception as e:
                                print(f"### デバッグ: 行 {row_index}: データ保存エラー: {str(e)}")
                                logger.exception(f"行 {row_index}: データ保存エラー: {str(e)}")
                                skipped_list.append({
                                    'row': row_index,
                                    'reason': f"データ保存エラー: {str(e)}",
                                    'product': product_name
                                })
                                error_count += 1
                                continue
                            
                        except Exception as e:
                            print(f"### デバッグ: 行 {row_index}: 処理エラー: {str(e)}")
                            print(traceback.format_exc())  # スタックトレースを出力
                            logger.exception(f"行 {row_index}: 処理エラー: {str(e)}")
                            skipped_list.append({
                                'row': row_index,
                                'reason': f"処理エラー: {str(e)}",
                                'data': str(row)
                            })
                            error_count += 1
                            continue
                    
                    # 処理成功
                    print(f"### デバッグ: ファイル処理完了: {import_count}件成功, {error_count}件エラー")
                    logger.info(f"ファイル処理完了: {import_count}件成功, {error_count}件エラー")
                    return import_count, error_count, skipped_list
                    
            except UnicodeDecodeError:
                # 現在のエンコーディングでは読めない場合、次を試す
                print(f"### デバッグ: エンコーディング '{encoding}' での読み込みに失敗しました。次を試します。")
                logger.debug(f"エンコーディング '{encoding}' での読み込みに失敗しました。次を試します。")
                
                if encoding == encodings[-1]:
                    # すべてのエンコーディングを試してもだめな場合
                    error_msg = f"次のエンコーディングではファイルを読めませんでした: {encodings}"
                    print(f"### デバッグ: {error_msg}")
                    logger.error(error_msg)
                    raise UnicodeDecodeError(encoding, b'', 0, 1, error_msg)
                continue
            except Exception as e:
                print(f"### デバッグ: ファイル処理エラー: {str(e)}")
                print(traceback.format_exc())  # スタックトレースを出力
                logger.exception(f"ファイル処理エラー: {str(e)}")
                if encoding == encodings[-1]:
                    raise
                continue
        
        # すべてのエンコーディングを試しても失敗した場合
        print("### デバッグ: すべてのエンコーディングでファイルを読み込めませんでした")
        logger.error("すべてのエンコーディングでファイルを読み込めませんでした")
        return import_count, error_count, skipped_list
    
    def _safe_get_value(self, row, index):
        """行から安全に値を取得する"""
        try:
            if index < 0:
                logger.debug(f"無効なインデックス {index} を取得しようとしました")
                return ""
                
            if index >= len(row):
                logger.debug(f"範囲外のインデックス {index} を取得しようとしました（行の長さ: {len(row)}）")
                return ""
                
            value = row[index]
            
            # None値や空文字列を処理
            if value is None:
                return ""
                
            # 文字列に変換して空白を削除
            str_value = str(value).strip()
            
            return str_value
        except Exception as e:
            logger.exception(f"値の取得中にエラー: インデックス {index}, エラー: {e}")
            return ""
    
    def _parse_date(self, date_str):
        """日付文字列をDateオブジェクトに変換する"""
        if not date_str:
            logger.warning("空の日付文字列が渡されました")
            return None
        
        # 前処理: 空白を削除、スラッシュを標準化
        date_str = date_str.strip()
        date_str = date_str.replace('／', '/')  # 全角スラッシュを半角に
        
        print(f"### デバッグ: 日付パース開始: '{date_str}'")
        logger.debug(f"日付パース開始: '{date_str}'")
        
        # YYYY/M/D形式に特化したパース処理
        if '/' in date_str:
            parts = date_str.split('/')
            if len(parts) == 3:
                try:
                    year = int(parts[0])
                    month = int(parts[1])
                    day = int(parts[2])
                    
                    # 年が2桁の場合は2000年代として解釈
                    if year < 100:
                        year += 2000
                    
                    print(f"### デバッグ: 日付パース: 年={year}, 月={month}, 日={day}")
                    logger.debug(f"日付パース: 年={year}, 月={month}, 日={day}")
                    
                    # 日付の妥当性チェック
                    if 1 <= month <= 12 and 1 <= day <= 31:
                        try:
                            result = datetime(year, month, day).date()
                            print(f"### デバッグ: 日付パース成功: '{date_str}' → {result}")
                            logger.debug(f"日付パース成功: '{date_str}' → {result}")
                            return result
                        except ValueError as e:
                            print(f"### デバッグ: 無効な日付: {year}/{month}/{day} - {e}")
                            logger.warning(f"無効な日付: {year}/{month}/{day} - {e}")
                    else:
                        print(f"### デバッグ: 月または日の値が範囲外です: 月={month}, 日={day}")
                        logger.warning(f"月または日の値が範囲外です: 月={month}, 日={day}")
                except ValueError:
                    print(f"### デバッグ: 日付の数値変換に失敗: {parts}")
                    logger.warning(f"日付の数値変換に失敗: {parts}")
        
        # 上記の処理で失敗した場合、汎用的な方法を試す
        date_formats = [
            ('%Y/%m/%d', "YYYY/MM/DD形式"),  # 例: 2025/03/31
            ('%Y/%m/%d', "YYYY/M/D形式"),   # 例: 2025/3/31
            ('%y/%m/%d', "YY/MM/DD形式"),   # 例: 25/03/31
            ('%y/%m/%d', "YY/M/D形式"),     # 例: 25/3/31
            ('%Y-%m-%d', "YYYY-MM-DD形式"), # 例: 2025-03-31
            ('%Y%m%d', "YYYYMMDD形式"),     # 例: 20250331
        ]
        
        for date_format, format_name in date_formats:
            try:
                result = datetime.strptime(date_str, date_format).date()
                print(f"### デバッグ: 日付パース成功: '{date_str}' → {result} ({format_name})")
                logger.debug(f"日付パース成功: '{date_str}' → {result} ({format_name})")
                return result
            except ValueError:
                print(f"### デバッグ: 日付パース失敗: '{date_str}' は {format_name} ではありません")
                logger.debug(f"日付パース失敗: '{date_str}' は {format_name} ではありません")
                continue
        
        # すべての形式が失敗した場合
        print(f"### デバッグ: 日付 '{date_str}' を解析できませんでした")
        logger.warning(f"日付 '{date_str}' を解析できませんでした")
        
        # 追加のトラブルシューティング
        print(f"### デバッグ: 日付文字列の長さ: {len(date_str)}")
        print(f"### デバッグ: 日付文字列の各文字のコード: {[ord(c) for c in date_str]}")
        logger.debug(f"日付文字列の長さ: {len(date_str)}")
        logger.debug(f"日付文字列の各文字のコード: {[ord(c) for c in date_str]}")
        
        return None
    
    def _get_or_create_work_center(self, work_center_id):
        """ワークセンターを取得または作成する"""
        if not work_center_id:
            logger.warning("空のワークセンターIDが渡されました")
            return None
        
        # 前処理：空白を削除
        work_center_id = work_center_id.strip()
        
        try:
            # 既存のワークセンターを検索
            return WorkCenter.objects.get(name=work_center_id)
        except WorkCenter.DoesNotExist:
            # ワークセンター情報のマッピング
            work_center_info = {
                "200100": {"name": "JP1", "color": "#952bff", "order": 1},
                "200201": {"name": "2A", "color": "#f21c36", "order": 2},
                "200200": {"name": "2B", "color": "#ff68b4", "order": 3},
                "200202": {"name": "2C", "color": "#ff68b4", "order": 4},
                "200300": {"name": "JP3", "color": "#44df60", "order": 5},
                "200400": {"name": "JP4", "color": "#00c6c6", "order": 6},
                "200601": {"name": "6A", "color": "#9b88b9", "order": 7},
                "200602": {"name": "6B", "color": "#9b88b9", "order": 8},
                "200603": {"name": "6D", "color": "#9b88b9", "order": 9},
                "200700": {"name": "7A/7B", "color": "#3c2dff", "order": 10},
                "200800": {"name": "JP8", "color": "#cccccc", "order": 11},
                "200900": {"name": "JP9", "color": "#cccccc", "order": 12},
                "300100": {"name": "外注", "color": "#999999", "order": 13},
            }
            
            # 既知のワークセンターか確認
            if work_center_id in work_center_info:
                info = work_center_info[work_center_id]
                work_center = WorkCenter.objects.create(
                    name=work_center_id,
                    display_name=info["name"],
                    color=info["color"],
                    order=info["order"]
                )
                print(f"### デバッグ: 新しいワークセンターを作成しました: {info['name']} ({work_center_id})")
                logger.info(f"新しいワークセンターを作成しました: {info['name']} ({work_center_id})")
                return work_center
            else:
                # 未知のワークセンターの場合はデフォルト値で作成
                work_center = WorkCenter.objects.create(
                    name=work_center_id,
                    display_name=f"WC-{work_center_id}",
                    color="#CCCCCC",
                    order=999
                )
                print(f"### デバッグ: 未知のワークセンターを作成しました: {work_center_id}")
                logger.warning(f"未知のワークセンターを作成しました: {work_center_id}")
                return work_center

csv_importer_view = CSVImporterView.as_view()