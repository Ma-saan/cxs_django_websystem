import csv
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from schedule_manager.models import WorkCenter, ProductSchedule
from datetime import datetime

class Command(BaseCommand):
    help = '古い形式のスケジュールデータをインポートします'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='インポートするCSVファイルのパス')

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        
        if not os.path.exists(csv_file):
            self.stdout.write(self.style.ERROR(f'ファイルが見つかりません: {csv_file}'))
            return
            
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
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                
                # 一度に処理するレコード数 (バッチサイズ)
                batch_size = 100
                schedules = []
                count = 0
                
                with transaction.atomic():
                    for row in csv_reader:
                        if not row['生産日'] or row['生産日'] == '0':
                            continue
                            
                        try:
                            # 日付形式のパース
                            date_str = row['生産日']
                            if '/' in date_str:
                                production_date = datetime.strptime(date_str, '%y/%m/%d').date()
                            else:
                                # 別の形式にも対応（必要に応じて）
                                self.stdout.write(self.style.WARNING(f'不明な日付形式: {date_str}'))
                                continue
                                
                            work_center_id = row['ワーク']
                            if work_center_id not in work_centers:
                                self.stdout.write(self.style.WARNING(f'不明なワークセンター: {work_center_id}'))
                                continue
                                
                            # モデルインスタンスを作成
                            schedule = ProductSchedule(
                                production_date=production_date,
                                work_center=work_centers[work_center_id],
                                product_number=row['品番'],
                                product_name=row['製品名'],
                                production_quantity=int(row['生産数']) if row['生産数'] and row['生産数'].isdigit() else 0,
                                grid_row=int(row['縦']) if row['縦'] and row['縦'].isdigit() else 0,
                                grid_column=int(row['横']) if row['横'] and row['横'].isdigit() else 0,
                                display_color=row['色'] or '#FFFFFF',
                                notes=row['その他'] if row['その他'] != '0' else None
                            )
                            
                            schedules.append(schedule)
                            count += 1
                            
                            # バッチサイズに達したらデータベースに一括保存
                            if len(schedules) >= batch_size:
                                ProductSchedule.objects.bulk_create(
                                    schedules, 
                                    update_conflicts=True,
                                    unique_fields=['production_date', 'work_center', 'product_number'],
                                    update_fields=['product_name', 'production_quantity', 'grid_row', 'grid_column', 'display_color', 'notes']
                                )
                                schedules = []
                                self.stdout.write(f'{count}件処理済み...')
                                
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f'行の処理中にエラー: {e}'))
                    
                    # 残りのデータを保存
                    if schedules:
                        ProductSchedule.objects.bulk_create(
                            schedules, 
                            update_conflicts=True,
                            unique_fields=['production_date', 'work_center', 'product_number'],
                            update_fields=['product_name', 'production_quantity', 'grid_row', 'grid_column', 'display_color', 'notes']
                        )
                
                self.stdout.write(self.style.SUCCESS(f'インポート完了: {count}件の予定をインポートしました。'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'インポート中にエラーが発生しました: {e}'))
    
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