# inventory/management/commands/update_product_lines.py

from django.core.management.base import BaseCommand
from inventory.models import Product
from django.db.models import Q

class Command(BaseCommand):
    help = '製品の生産ラインを一括更新します'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            help='実際には更新せず、更新対象の製品を表示します',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        
        # 更新ルールを定義
        update_rules = [
            {'filter': Q(product_name__icontains='BIB') & ~Q(production_line='JP4'), 'line': 'JP4'},
            {'filter': (Q(product_name__icontains='1000KGX1') | Q(product_name__icontains='1200KGX1')) & ~Q(production_line='6B'), 'line': '6B'},
            # 他のルールを追加できます
        ]
        
        total_updated = 0
        
        for rule in update_rules:
            products = Product.objects.filter(rule['filter'])
            count = products.count()
            
            if count == 0:
                self.stdout.write(f'「{rule["line"]}」に更新が必要な製品はありません')
                continue
                
            if dry_run:
                self.stdout.write(self.style.WARNING(f'更新対象製品数: {count} → {rule["line"]}'))
                for product in products:
                    current_line = product.production_line or '未設定'
                    self.stdout.write(f'  {product.product_id}: {product.product_name} [{current_line} → {rule["line"]}]')
            else:
                updated = products.update(production_line=rule['line'])
                total_updated += updated
                self.stdout.write(f'{updated}件の製品のラインを「{rule["line"]}」に更新しました')
        
        if dry_run:
            self.stdout.write(self.style.SUCCESS('dry-runモードのため、実際の更新は行いませんでした。'))
        else:
            self.stdout.write(self.style.SUCCESS(f'合計{total_updated}件の製品のラインを更新しました'))