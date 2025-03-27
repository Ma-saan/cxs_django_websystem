import csv
import os
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.views import View
from datetime import datetime

from .models import WorkCenter, ProductSchedule

class CSVImporterView(View):
    """CSVファイルから生産予定データをインポートするビュー"""
    
    def get(self, request):
        """CSVアップロードフォームを表示"""
        work_centers = WorkCenter.objects.all().order_by('order')
        return render(request, 'schedule_manager/import_csv.html', {
            'work_centers': work_centers
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
            
            # CSVファイル処理
            import_count, error_count = self.process_csv_file(full_path)
            
            if error_count > 0:
                message = f'{import_count}件のデータをインポートしました。{error_count}件のエラーがありました。'
                messages.warning(request, message)
            else:
                message = f'{import_count}件のデータをインポートしました。'
                messages.success(request, message)
                
        except Exception as e:
            messages.error(request, f'CSVインポート中にエラーが発生しました: {str(e)}')
        finally:
            # 一時ファイルの削除
            if 'full_path' in locals() and os.path.exists(full_path):
                os.remove(full_path)
        
        return redirect('schedule_manager:import_csv')
    
    def process_csv_file(self, file_path):
        """CSVファイルを読み込み、データベースに保存"""
        import_count = 0
        error_count = 0
        
        # 異なる文字コードに対応するための試行リスト
        encodings = ['utf-8', 'shift_jis', 'cp932', 'euc_jp']
        
        for encoding in encodings:
            try:
                with open(file_path, newline='', encoding=encoding) as csvfile:
                    # ヘッダー行をスキップ (既存のCSV形式に合わせて調整)
                    for _ in range(4):  # 最初の4行をスキップ
                        next(csvfile)
                    
                    reader = csv.reader(csvfile)
                    next(reader)  # ヘッダー行をスキップ
                    
                    for row in reader:
                        if len(row) >= 19 and any(row):  # 行に十分なデータがあり、かつ空行でない
                            try:
                                # CSVデータのマッピング
                                manufacturing_filling = row[0].strip()
                                production_date_str = row[2].strip()
                                work_center_number = row[3].strip()
                                work_center_name = row[4].strip()
                                product_number = row[8].strip()
                                product_name = row[10].strip()
                                production_quantity = row[14].strip()
                                personnel = row[16].strip()
                                order_number = row[17].strip()
                                work_order_status = row[18].strip()
                                
                                # CSVに含まれる日付形式の変換 (YY/MM/DD → YYYY-MM-DD)
                                if production_date_str:
                                    try:
                                        if '/' in production_date_str:
                                            date_parts = production_date_str.split('/')
                                            if len(date_parts) == 3:
                                                yy, mm, dd = date_parts
                                                # 2桁の年を4桁に変換 (20年代として解釈)
                                                yyyy = f"20{yy}" if len(yy) == 2 else yy
                                                production_date = datetime.strptime(f"{yyyy}-{mm}-{dd}", "%Y-%m-%d").date()
                                            else:
                                                raise ValueError(f"Invalid date format: {production_date_str}")
                                        else:
                                            # その他の形式の日付を処理
                                            raise ValueError(f"Unsupported date format: {production_date_str}")
                                    except ValueError as e:
                                        error_count += 1
                                        continue
                                else:
                                    continue  # 日付がない行はスキップ
                                
                                # 対応するワークセンターの特定
                                work_center = None
                                if work_center_number:
                                    try:
                                        work_center = WorkCenter.objects.get(name=work_center_number)
                                    except WorkCenter.DoesNotExist:
                                        # 既存のワークセンターがない場合は作成
                                        work_center = WorkCenter.objects.create(
                                            name=work_center_number,
                                            display_name=work_center_name,
                                            color="#CCCCCC",  # デフォルト色
                                            order=999  # デフォルト表示順
                                        )
                                
                                # 数量を整数に変換
                                try:
                                    quantity = int(production_quantity) if production_quantity else 0
                                except ValueError:
                                    quantity = 0
                                
                                # 生産予定データの保存または更新
                                if work_center and product_number and production_date:
                                    ProductSchedule.objects.update_or_create(
                                        production_date=production_date,
                                        work_center=work_center,
                                        product_number=product_number,
                                        defaults={
                                            'product_name': product_name,
                                            'production_quantity': quantity,
                                            'notes': f"製造/充填: {manufacturing_filling}, 人員: {personnel}, "
                                                    f"オーダーNo: {order_number}, 状態: {work_order_status}"
                                        }
                                    )
                                    import_count += 1
                                
                            except Exception as e:
                                error_count += 1
                                print(f"行処理エラー: {str(e)}")
                                continue
                    
                    # 処理に成功したらループ終了
                    break
                    
            except UnicodeDecodeError:
                # 現在のエンコーディングでは読めない場合、次を試す
                if encoding == encodings[-1]:
                    # すべてのエンコーディングを試してもだめな場合
                    raise UnicodeDecodeError(f"次のエンコーディングではファイルを読めませんでした: {encodings}")
                continue
                
        return import_count, error_count

csv_importer_view = CSVImporterView.as_view()