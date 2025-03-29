import csv
import os
import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from schedule_manager.models import WorkCenter, ProductSchedule
from datetime import datetime

# ロガーの設定
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = '古い形式のスケジュールデータをインポートします'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='インポートするCSVファイルのパス')
        parser.add_argument('--debug', action='store_true', help='デバッグモードを有効化')
        parser.add_argument('--encoding', type=str, default='utf-8', 
                            help='CSVファイルのエンコーディング (例: utf-8, shift_jis, cp932)')
        parser.add_argument('--dry-run', action='store_true', 
                            help='実際にはデータを保存せず、処理内容のみ確認します')

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        debug_mode = options['debug']
        encoding = options['encoding']
        dry_run = options['dry_run']
        
        if not os.path.exists(csv_file):
            self.stdout.write(self.style.ERROR(f'ファイルが見つかりません: {csv_file}'))
            return
        
        self.stdout.write(f'インポート開始: {csv_file} (エンコーディング: {encoding})')
        if dry_run:
            self.stdout.write(self.style.WARNING('ドライランモード: データベースには保存されません'))
            
        # ワークセンターの事前設定
        work_centers = {
            "200100": self.get_or_create_work_center("200100", "JP1", "#952bff", 1),
            "200201": self.get_or_create_work_center("200201", "2A", "#f21c36", 2),
            "200200": self.get_or_create_work_center("200200", "2B", "#ff68b4", 3),
            "200202": self.get_or_create_work_center("200202", "2C", "#ff68b4", 4), 
            "200300": self.get_or_create_work_center("200300", "JP3", "#44df60", 5),
            "200400": self.get_or_create_work_center("200400", "JP4", "#00c6c6", 6),
            "200601": self.get_or_create_work_center("200601", "6A", "#9b88b9", 7),
            "200602": self.get_or_create_work_center("200602", "6B", "#9b88b9", 8),
            "200603": self.get_or_create_work_center("200603", "6C", "#9b88b9", 9),
            "200700": self.get_or_create_work_center("200700", "7A/7B", "#3c2dff", 10),
            "200800": self.get_or_create_work_center("200800", "その他", "#cccccc", 11),
        }
        
        # レコード処理の統計情報
        stats = {
            'total': 0,
            'success': 0,
            'error': 0,
            'skipped': 0,
            'skipped_records': []  # スキップされたレコードの詳細情報
        }
        
        try:
            with open(csv_file, 'r', encoding=encoding) as file:
                if debug_mode:
                    # ファイルの先頭部分をデバッグ出力
                    file_sample = file.read(1024)
                    self.stdout.write("ファイル先頭サンプル:")
                    self.stdout.write(file_sample)
                    file.seek(0)  # ファイルポインタをリセット
                
                csv_reader = csv.DictReader(file)
                
                # CSVヘッダー情報をデバッグ出力
                if debug_mode:
                    self.stdout.write(f"CSVヘッダー: {csv_reader.fieldnames}")
                
                # 一度に処理するレコード数 (バッチサイズ)
                batch_size = 100
                schedules = []
                
                with transaction.atomic():
                    for i, row in enumerate(csv_reader):
                        stats['total'] += 1
                        row_num = i + 2  # ヘッダー行を考慮して行番号は2から開始
                        
                        try:
                            # 行データをデバッグ出力
                            if debug_mode:
                                self.stdout.write(f"行 {row_num}: {row}")
                            
                            # 空の行をスキップ
                            if not row['生産日'] or row['生産日'] == '0':
                                if debug_mode:
                                    self.stdout.write(self.style.WARNING(f'行 {row_num}: 日付が空またはゼロのためスキップします'))
                                stats['skipped'] += 1
                                stats['skipped_records'].append({
                                    'row': row_num,
                                    'reason': '日付が空またはゼロ',
                                    'data': row.get('製品名', 'N/A')
                                })
                                continue
                                
                            try:
                                # 日付形式のパース
                                date_str = row['生産日']
                                if '/' in date_str:
                                    production_date = datetime.strptime(date_str, '%y/%m/%d').date()
                                    if debug_mode:
                                        self.stdout.write(f'行 {row_num}: 日付 "{date_str}" を "{production_date}" としてパースしました')
                                else:
                                    # 別の形式にも対応（必要に応じて）
                                    self.stdout.write(self.style.WARNING(f'行 {row_num}: 不明な日付形式: {date_str}'))
                                    stats['skipped'] += 1
                                    stats['skipped_records'].append({
                                        'row': row_num,
                                        'reason': f'不明な日付形式: {date_str}',
                                        'data': row.get('製品名', 'N/A')
                                    })
                                    continue
                                    
                            except ValueError as e:
                                self.stdout.write(self.style.WARNING(f'行 {row_num}: 日付パースエラー: {e}, 値: {date_str}'))
                                stats['error'] += 1
                                stats['skipped_records'].append({
                                    'row': row_num,
                                    'reason': f'日付パースエラー: {e}',
                                    'data': row.get('製品名', 'N/A')
                                })
                                continue
                                
                            work_center_id = row['ワーク']
                            if work_center_id not in work_centers:
                                self.stdout.write(self.style.WARNING(f'行 {row_num}: 不明なワークセンター: {work_center_id}'))
                                stats['skipped'] += 1
                                stats['skipped_records'].append({
                                    'row': row_num,
                                    'reason': f'不明なワークセンター: {work_center_id}',
                                    'data': row.get('製品名', 'N/A')
                                })
                                continue
                                
                            # 特殊文字の処理（半角カナなど）
                            product_name = row['製品名']
                            if debug_mode and ('ﾆｭｰﾚﾝｼﾞｸﾘｰﾅｰ' in product_name or 'ｱﾌﾞﾗﾖｺﾞﾚﾖｳ' in product_name):
                                self.stdout.write(self.style.SUCCESS(f'行 {row_num}: 注目製品を検出! "{product_name}"'))
                            
                            # モデルインスタンスを作成
                            schedule = ProductSchedule(
                                production_date=production_date,
                                work_center=work_centers[work_center_id],
                                product_number=row['品番'],
                                product_name=product_name,
                                production_quantity=int(row['生産数']) if row['生産数'] and row['生産数'].isdigit() else 0,
                                grid_row=int(row['縦']) if row['縦'] and row['縦'].isdigit() else 0,
                                grid_column=int(row['横']) if row['横'] and row['横'].isdigit() else 0,
                                display_color=row['色'] or '#FFFFFF',
                                notes=row['その他'] if row['その他'] != '0' else None
                            )
                            
                            if debug_mode:
                                self.stdout.write(f'行 {row_num}: レコード作成: {schedule.product_name} ({schedule.product_number})')
                            
                            # ドライランモードの場合は実際に保存しない
                            if not dry_run:
                                schedules.append(schedule)
                            
                            stats['success'] += 1
                            
                            # バッチサイズに達したらデータベースに一括保存
                            if len(schedules) >= batch_size and not dry_run:
                                self._save_batch(schedules)
                                schedules = []
                                self.stdout.write(f'{stats["success"]}件処理済み...')
                                
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f'行 {row_num} の処理中にエラー: {e}'))
                            logger.exception(f'行 {row_num} 処理エラー: {e}')
                            stats['error'] += 1
                            stats['skipped_records'].append({
                                'row': row_num,
                                'reason': f'処理エラー: {str(e)}',
                                'data': row.get('製品名', 'N/A')
                            })
                            continue
                    
                    # 残りのデータを保存
                    if schedules and not dry_run:
                        self._save_batch(schedules)
                
                # 結果レポート
                self.report_results(stats)
                
        except UnicodeDecodeError as e:
            self.stdout.write(self.style.ERROR(f'ファイルエンコーディングエラー: {e}'))
            self.stdout.write(self.style.WARNING(f'--encoding オプションで正しいエンコーディングを指定してください'))
            logger.exception('ファイルエンコーディングエラー')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'インポート中にエラーが発生しました: {e}'))
            logger.exception('インポート処理エラー')
    
    def _save_batch(self, schedules):
        """スケジュールのバッチを保存"""
        try:
            ProductSchedule.objects.bulk_create(
                schedules, 
                update_conflicts=True,
                unique_fields=['production_date', 'work_center', 'product_number'],
                update_fields=['product_name', 'production_quantity', 'grid_row', 'grid_column', 'display_color', 'notes']
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'バッチ保存中にエラー: {e}'))
            # エラー発生時は1件ずつ保存を試みる
            for schedule in schedules:
                try:
                    # 既存のレコードを検索
                    existing = ProductSchedule.objects.filter(
                        production_date=schedule.production_date,
                        work_center=schedule.work_center,
                        product_number=schedule.product_number
                    ).first()
                    
                    if existing:
                        # 既存レコードを更新
                        existing.product_name = schedule.product_name
                        existing.production_quantity = schedule.production_quantity
                        existing.grid_row = schedule.grid_row
                        existing.grid_column = schedule.grid_column
                        existing.display_color = schedule.display_color
                        existing.notes = schedule.notes
                        existing.save()
                    else:
                        # 新規レコードを作成
                        schedule.save()
                except Exception as individual_error:
                    self.stdout.write(self.style.ERROR(
                        f'レコード保存エラー: {schedule.product_name} ({schedule.product_number}): {individual_error}'
                    ))
    
    def report_results(self, stats):
        """インポート結果のレポートを表示"""
        self.stdout.write(self.style.SUCCESS(
            f'インポート完了: 処理合計 {stats["total"]}件, '
            f'成功 {stats["success"]}件, '
            f'エラー {stats["error"]}件, '
            f'スキップ {stats["skipped"]}件'
        ))
        
        if stats['skipped_records']:
            self.stdout.write(self.style.WARNING('スキップされたレコード:'))
            # 最初の10件だけ表示
            for i, record in enumerate(stats['skipped_records'][:10]):
                self.stdout.write(self.style.WARNING(
                    f'  {i+1}. 行 {record["row"]}: {record["reason"]} - データ: {record["data"]}'
                ))
            
            if len(stats['skipped_records']) > 10:
                self.stdout.write(self.style.WARNING(
                    f'  ...他 {len(stats["skipped_records"]) - 10}件 (詳細はログを参照)'
                ))
    
    def get_or_create_work_center(self, name, display_name, color, order):
        """ワークセンターを取得または作成"""
        work_center, created = WorkCenter.objects.get_or_create(
            name=name,
            defaults={
                'display_name': display_name,
                'color': color,
                'order': order
            }
        )
        if created:
            self.stdout.write(f'新しいワークセンターを作成しました: {display_name}')
        return work_center