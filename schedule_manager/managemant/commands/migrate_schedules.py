import os
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q
from schedule_app.models import ScheduleAppSchedule
from schedule_manager.models import WorkCenter, ProductSchedule
from datetime import datetime

class Command(BaseCommand):
    help = 'schedule_appからschedule_managerへデータを移行します'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clean', 
            action='store_true', 
            help='移行前に既存のProductScheduleデータをクリアします'
        )
        parser.add_argument(
            '--date', 
            type=str, 
            help='指定した日付のデータのみ移行します (YY/MM/DD形式)'
        )

    def handle(self, *args, **options):
        clean_existing = options.get('clean', False)
        date_filter = options.get('date')
        
        # ワークセンターのマッピング情報を生成
        work_center_mapping = self.ensure_work_centers()
        
        # date_filterがある場合は指定された日付のデータのみを対象にする
        queryset = ScheduleAppSchedule.objects.all()
        if date_filter:
            queryset = queryset.filter(production_date=date_filter)
        
        # クリーンオプションが指定されていたら既存のデータを削除
        if clean_existing:
            if date_filter:
                ProductSchedule.objects.filter(
                    Q(production_date=datetime.strptime(date_filter, '%y/%m/%d').date())
                ).delete()
                self.stdout.write(self.style.WARNING(f'日付 {date_filter} の既存データを削除しました'))
            else:
                ProductSchedule.objects.all().delete()
                self.stdout.write(self.style.WARNING('既存の全予定データを削除しました'))
        
        # 処理カウンター
        total_count = queryset.count()
        migrated_count = 0
        error_count = 0
        skipped_count = 0
        
        with transaction.atomic():
            # バッチサイズを設定（メモリ使用量の管理のため）
            batch_size = 500
            self.stdout.write(f'移行するデータ数: {total_count}')
            
            # データバッチ処理
            for i, schedule in enumerate(queryset.iterator(batch_size)):
                try:
                    # 日付文字列をパース
                    try:
                        if schedule.production_date and '/' in schedule.production_date:
                            date_parts = schedule.production_date.split('/')
                            if len(date_parts) == 3:
                                yy, mm, dd = date_parts
                                # 2桁の年を4桁に変換 (20年代として解釈)
                                yyyy = f"20{yy}" if len(yy) == 2 else yy
                                production_date = datetime.strptime(f"{yyyy}-{mm}-{dd}", "%Y-%m-%d").date()
                            else:
                                raise ValueError(f"不正な日付形式: {schedule.production_date}")
                        else:
                            # 日付がない場合はスキップ
                            skipped_count += 1
                            continue
                    except ValueError:
                        # 日付パースエラー
                        self.stdout.write(self.style.WARNING(f'日付パースエラー: {schedule.production_date}'))
                        error_count += 1
                        continue
                    
                    # ワークセンターの検索
                    work_center = None
                    if schedule.work_center_number in work_center_mapping:
                        work_center = work_center_mapping[schedule.work_center_number]
                    else:
                        # ワークセンターがなければ作成
                        work_center, created = WorkCenter.objects.get_or_create(
                            name=schedule.work_center_number,
                            defaults={
                                'display_name': schedule.work_center_name,
                                'color': '#CCCCCC',  # デフォルト色
                                'order': 999  # デフォルト表示順
                            }
                        )
                        work_center_mapping[schedule.work_center_number] = work_center
                        if created:
                            self.stdout.write(f'新しいワークセンターを作成: {work_center.display_name}')
                    
                    # 生産数量の処理
                    try:
                        quantity = int(schedule.production_quantity) if schedule.production_quantity else 0
                    except ValueError:
                        quantity = 0
                    
                    # 生産予定データの作成/更新
                    if work_center and schedule.product_number and production_date:
                        # まず既存データの確認
                        exists = ProductSchedule.objects.filter(
                            production_date=production_date,
                            work_center=work_center,
                            product_number=schedule.product_number
                        ).exists()
                        
                        if not exists:
                            ProductSchedule.objects.create(
                                production_date=production_date,
                                work_center=work_center,
                                product_number=schedule.product_number,
                                product_name=schedule.product_name,
                                production_quantity=quantity,
                                notes=f"製造/充填: {schedule.manufacturing_filling}, 人員: {schedule.personnel}, "
                                      f"オーダーNo: {schedule.order_number}, 状態: {schedule.work_order_status}"
                            )
                            migrated_count += 1
                        else:
                            skipped_count += 1
                    else:
                        skipped_count += 1
                    
                    # 進捗表示
                    if (i + 1) % 100 == 0 or (i + 1) == total_count:
                        self.stdout.write(f'処理中: {i + 1}/{total_count} ({(i + 1) / total_count * 100:.1f}%)')
                
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'エラー発生: {str(e)}'))
                    error_count += 1
        
        # 結果表示
        self.stdout.write(self.style.SUCCESS(
            f'移行完了: {migrated_count}件成功, {skipped_count}件スキップ, {error_count}件エラー'
        ))
    
    def ensure_work_centers(self):
        """ワークセンターのマッピング辞書を返す"""
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
        return work_centers
    
    def get_or_create_work_center(self, name, display_name, color, order):
        """ワークセンターを取得または作成する"""
        work_center, created = WorkCenter.objects.get_or_create(
            name=name,
            defaults={
                'display_name': display_name,
                'color': color,
                'order': order
            }
        )
        if created:
            self.stdout.write(f'新しいワークセンターを作成: {display_name}')
        return work_center