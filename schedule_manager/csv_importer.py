import csv
import os
import logging
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
            
            logger.info(f"CSVファイル '{csv_file.name}' を処理開始")
            
            # CSVファイル処理
            import_count, error_count, skipped_list = self.process_csv_file(full_path)
            
            # インポート結果の表示
            if error_count > 0:
                message = f'{import_count}件のデータをインポートしました。{error_count}件のエラーまたはスキップがありました。'
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
            else:
                message = f'{import_count}件のデータをインポートしました。'
                messages.success(request, message)
                
        except Exception as e:
            error_msg = f'CSVインポート中にエラーが発生しました: {str(e)}'
            logger.exception(error_msg)
            messages.error(request, error_msg)
        finally:
            # 一時ファイルの削除
            if 'full_path' in locals() and os.path.exists(full_path):
                os.remove(full_path)
        
        return redirect('schedule_manager:import_csv')
    
    def process_csv_file(self, file_path):
        """CSVファイルを読み込み、データベースに保存"""
        import_count = 0
        error_count = 0
        skipped_list = []
        
        # 試行するエンコーディングリスト
        encodings = ['utf-8', 'shift_jis', 'cp932', 'euc_jp']
        
        for encoding in encodings:
            try:
                with open(file_path, newline='', encoding=encoding) as csvfile:
                    logger.info(f"ファイル '{file_path}' をエンコーディング '{encoding}' で処理中")
                    
                    # ファイルの先頭部分をデバッグログに出力
                    file_sample = csvfile.read(2048)
                    logger.debug(f"ファイルのサンプル内容:\n{file_sample}")
                    csvfile.seek(0)  # ファイルポインタをリセット
                    
                    # タブ区切りファイルとして読み込む
                    reader = csv.reader(csvfile, delimiter='\t')
                    
                    # 最初の数行を読み取り、ファイル構造を分析
                    header_rows = []
                    for _ in range(5):  # 最初の5行を読み込む
                        try:
                            row = next(reader)
                            header_rows.append(row)
                        except StopIteration:
                            break
                    
                    logger.info("ヘッダー行解析:")
                    for i, row in enumerate(header_rows):
                        logger.info(f"行 {i+1}: {row}")
                    
                    # ヘッダー行の数を決定（通常は3行）
                    header_row_count = 3
                    
                    # ファイルをリセットして再読み込み
                    csvfile.seek(0)
                    reader = csv.reader(csvfile, delimiter='\t')
                    
                    # ヘッダー行をスキップ
                    for _ in range(header_row_count):
                        next(reader)
                    
                    # 列ヘッダー行を取得して列のインデックスを特定
                    column_headers = next(reader)
                    logger.info(f"列ヘッダー: {column_headers}")
                    
                    # 列インデックスのマッピング
                    column_indices = self._get_column_indices(column_headers)
                    logger.info(f"列インデックス: {column_indices}")
                    
                    # 行ごとに処理
                    row_count = 0
                    for row_index, row in enumerate(reader, header_row_count + 2):
                        row_count += 1
                        
                        if row_count % 100 == 0:
                            logger.info(f"{row_count}行処理済み")
                        
                        # 空行のスキップ
                        if not row or (len(row) == 1 and not row[0].strip()):
                            continue
                        
                        # 行データの解析と検証
                        try:
                            # 製造/充填
                            manufacturing_filling = self._safe_get_value(row, column_indices['manufacturing_filling'])
                            
                            # 生産日
                            date_str = self._safe_get_value(row, column_indices['date'])
                            if not date_str:
                                logger.warning(f"行 {row_index}: 日付が空です")
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
                                if not production_date:
                                    raise ValueError(f"日付解析エラー: {date_str}")
                            except ValueError as e:
                                logger.warning(f"行 {row_index}: {e}")
                                skipped_list.append({
                                    'row': row_index,
                                    'reason': f'日付解析エラー: {date_str}',
                                    'data': str(row)
                                })
                                error_count += 1
                                continue
                            
                            # ワークセンター
                            work_center_id = self._safe_get_value(row, column_indices['work_center'])
                            if not work_center_id:
                                logger.warning(f"行 {row_index}: ワークセンターが空です")
                                skipped_list.append({
                                    'row': row_index,
                                    'reason': 'ワークセンターが空です',
                                    'data': str(row)
                                })
                                error_count += 1
                                continue
                            
                            # ワークセンターの取得または作成
                            work_center = self._get_or_create_work_center(work_center_id)
                            
                            # 品番
                            product_number = self._safe_get_value(row, column_indices['product_number'])
                            
                            # 製品名
                            product_name = self._safe_get_value(row, column_indices['product_name'])
                            
                            # 特に注目する製品かどうか
                            target_products = ['ﾆｭｰﾚﾝｼﾞｸﾘｰﾅｰ', 'ｱﾌﾞﾗﾖｺﾞﾚﾖｳ']
                            target_numbers = ['T30221', 'T30203']
                            
                            is_target = False
                            for target in target_products:
                                if target in product_name:
                                    is_target = True
                                    break
                            
                            if product_number in target_numbers:
                                is_target = True
                            
                            # 対象製品の詳細出力
                            if is_target:
                                logger.info(f"==== 対象製品検出 ==== 行 {row_index}")
                                logger.info(f"製品名: {product_name}")
                                logger.info(f"品番: {product_number}")
                                logger.info(f"日付: {date_str}")
                                logger.info(f"ワークセンター: {work_center_id}")
                                logger.info(f"行データ: {row}")
                                logger.info("==== 対象製品データ終了 ====")
                            
                            # 生産数量
                            quantity_str = self._safe_get_value(row, column_indices['quantity'])
                            try:
                                quantity = int(quantity_str) if quantity_str else 0
                            except ValueError:
                                logger.warning(f"行 {row_index}: 数量を整数に変換できません: {quantity_str}")
                                quantity = 0
                            
                            # 人員
                            personnel = self._safe_get_value(row, column_indices['personnel'])
                            
                            # オーダーNo
                            order_number = self._safe_get_value(row, column_indices['order_number'])
                            
                            # Work Order Status
                            status = self._safe_get_value(row, column_indices['status'])
                            
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
                                    # 既存レコードを更新
                                    existing.product_name = product_name
                                    existing.production_quantity = quantity
                                    existing.notes = notes
                                    existing.save(update_fields=['product_name', 'production_quantity', 'notes', 'last_updated'])
                                    
                                    if is_target:
                                        logger.info(f"行 {row_index}: 対象製品の既存レコードを更新しました: {product_name} ({product_number})")
                                else:
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
                                    
                                    if is_target:
                                        logger.info(f"行 {row_index}: 対象製品の新規レコードを作成しました: {product_name} ({product_number})")
                                
                                import_count += 1
                                
                            except Exception as e:
                                logger.exception(f"行 {row_index}: データ保存エラー: {str(e)}")
                                skipped_list.append({
                                    'row': row_index,
                                    'reason': f"データ保存エラー: {str(e)}",
                                    'product': product_name
                                })
                                error_count += 1
                                continue
                            
                        except Exception as e:
                            logger.exception(f"行 {row_index}: 処理エラー: {str(e)}")
                            skipped_list.append({
                                'row': row_index,
                                'reason': f"処理エラー: {str(e)}",
                                'data': str(row)
                            })
                            error_count += 1
                            continue
                    
                    # 処理成功
                    logger.info(f"ファイル処理完了: {import_count}件成功, {error_count}件エラー")
                    return import_count, error_count, skipped_list
                    
            except UnicodeDecodeError:
                # 現在のエンコーディングでは読めない場合、次を試す
                logger.debug(f"エンコーディング '{encoding}' での読み込みに失敗しました。次を試します。")
                
                if encoding == encodings[-1]:
                    # すべてのエンコーディングを試してもだめな場合
                    error_msg = f"次のエンコーディングではファイルを読めませんでした: {encodings}"
                    logger.error(error_msg)
                    raise UnicodeDecodeError(encoding, b'', 0, 1, error_msg)
                continue
            except Exception as e:
                logger.exception(f"ファイル処理エラー: {str(e)}")
                if encoding == encodings[-1]:
                    raise
                continue
        
        # すべてのエンコーディングを試しても失敗した場合
        logger.error("すべてのエンコーディングでファイルを読み込めませんでした")
        return import_count, error_count, skipped_list
    
    def _get_column_indices(self, headers):
        """列ヘッダーから列インデックスを特定する"""
        indices = {
            'manufacturing_filling': -1,  # 製造/充填
            'date': -1,                   # 生産日
            'work_center': -1,            # ﾜｰｸｾﾝﾀｰ 番号
            'work_center_name': -1,       # ﾜｰｸｾﾝﾀｰ名
            'product_number': -1,         # 品番
            'product_name': -1,           # 品名
            'quantity': -1,               # 生産 予定数
            'personnel': -1,              # 人員
            'order_number': -1,           # ｵｰﾀﾞｰ No.
            'status': -1                  # Work Order Status
        }
        
        # 各列を特定
        for i, header in enumerate(headers):
            header_lower = header.lower() if header else ""
            
            if "充填" in header_lower or "製造" in header_lower:
                indices['manufacturing_filling'] = i
            elif "生産日" in header_lower:
                indices['date'] = i
            elif "ﾜｰｸｾﾝﾀｰ" in header_lower and "番号" in header_lower:
                indices['work_center'] = i
            elif "ﾜｰｸｾﾝﾀｰ名" in header_lower:
                indices['work_center_name'] = i
            elif "品番" in header_lower:
                indices['product_number'] = i
            elif "品名" in header_lower:
                indices['product_name'] = i
            elif "予定数" in header_lower or "生産数" in header_lower:
                indices['quantity'] = i
            elif "人員" in header_lower:
                indices['personnel'] = i
            elif "ｵｰﾀﾞｰ" in header_lower or "オーダー" in header_lower:
                indices['order_number'] = i
            elif "status" in header_lower or "ステータス" in header_lower:
                indices['status'] = i
        
        # 見つからなかった場合は一般的な位置を使用
        if indices['manufacturing_filling'] == -1:
            indices['manufacturing_filling'] = 0
        
        if indices['date'] == -1:
            indices['date'] = 1
        
        if indices['work_center'] == -1:
            indices['work_center'] = 2
        
        if indices['work_center_name'] == -1:
            indices['work_center_name'] = 3
        
        if indices['product_number'] == -1:
            indices['product_number'] = 4
        
        if indices['product_name'] == -1:
            indices['product_name'] = 5
        
        if indices['quantity'] == -1:
            indices['quantity'] = 6
        
        if indices['personnel'] == -1:
            indices['personnel'] = 7
        
        if indices['order_number'] == -1:
            indices['order_number'] = 8
        
        if indices['status'] == -1:
            indices['status'] = 9
        
        return indices
    
    def _safe_get_value(self, row, index):
        """行から安全に値を取得する"""
        try:
            return row[index].strip() if index >= 0 and index < len(row) else ""
        except IndexError:
            return ""
    
    def _parse_date(self, date_str):
        """日付文字列をDateオブジェクトに変換する"""
        if not date_str:
            return None
        
        # さまざまな日付形式に対応
        date_formats = [
            '%Y/%m/%d',  # 例: 2025/3/31
            '%Y/%m/%d',  # 例: 2025/03/31
            '%y/%m/%d',  # 例: 25/3/31
            '%y/%m/%d',  # 例: 25/03/31
            '%Y-%m-%d',  # 例: 2025-03-31
            '%Y%m%d',    # 例: 20250331
        ]
        
        for date_format in date_formats:
            try:
                return datetime.strptime(date_str, date_format).date()
            except ValueError:
                continue
        
        # すべての形式が失敗した場合
        logger.warning(f"日付 '{date_str}' を解析できませんでした")
        return None
    
    def _get_or_create_work_center(self, work_center_id):
        """ワークセンターを取得または作成する"""
        if not work_center_id:
            return None
        
        try:
            # 既存のワークセンターを検索
            return WorkCenter.objects.get(name=work_center_id)
        except WorkCenter.DoesNotExist:
            # ワークセンター情報のマッピング
            work_center_info = {
                "200100": {"name": "JP1", "color": "#952bff"},
                "200201": {"name": "2A", "color": "#f21c36"},
                "200200": {"name": "2B", "color": "#ff68b4"},
                "200202": {"name": "2C", "color": "#ff68b4"},
                "200300": {"name": "JP3", "color": "#44df60"},
                "200400": {"name": "JP4", "color": "#00c6c6"},
                "200601": {"name": "6A", "color": "#9b88b9"},
                "200602": {"name": "6B", "color": "#9b88b9"},
                "200603": {"name": "6D", "color": "#9b88b9"},
                "200700": {"name": "7A/7B", "color": "#3c2dff"},
                "200800": {"name": "JP8", "color": "#cccccc"},
                "200900": {"name": "JP9", "color": "#cccccc"},
                "300100": {"name": "外注", "color": "#999999"},
            }
            
            # 既知のワークセンターか確認
            if work_center_id in work_center_info:
                info = work_center_info[work_center_id]
                work_center = WorkCenter.objects.create(
                    name=work_center_id,
                    display_name=info["name"],
                    color=info["color"],
                    order=list(work_center_info.keys()).index(work_center_id) + 1
                )
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
                logger.info(f"未知のワークセンターを作成しました: {work_center_id}")
                return work_center

csv_importer_view = CSVImporterView.as_view()