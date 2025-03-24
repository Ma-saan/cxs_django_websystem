# inventory/management/commands/import_inventory_data.py

import csv
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from inventory.models import Material, Product, BOM
from django.conf import settings

class Command(BaseCommand):
    help = '製品、材料、BOMデータをCSVファイルからインポートします'

    def add_arguments(self, parser):
        parser.add_argument('--csv-dir', type=str, 
                        default=os.path.join(settings.BASE_DIR, 'data', 'imports'),
                        help='CSVファイルのあるディレクトリ')
        parser.add_argument('--bom-only', action='store_true', 
                        help='BOMデータのみをインポートします')
    
    def handle(self, *args, **options):
        csv_dir = options['csv_dir']
        bom_only = options.get('bom_only', False)
    
        self.stdout.write(self.style.SUCCESS(f'データインポートを開始します。ディレクトリ: {csv_dir}'))
    
    # ディレクトリの存在を確認
        if not os.path.exists(csv_dir):
            self.stdout.write(self.style.ERROR(f'指定されたディレクトリが存在しません: {csv_dir}'))
            return
        
        try:
            # BOMのみのモードでない場合は材料と製品をインポート
            if not bom_only:
                # 材料データのインポート
                materials_path = os.path.join(csv_dir, 'Materials.csv')
                if os.path.exists(materials_path):
                    self.import_materials(materials_path)
                else:
                    self.stdout.write(self.style.WARNING(f'材料ファイルが見つかりません: {materials_path}'))
            
                # 製品データのインポート
                products_path = os.path.join(csv_dir, 'Products.csv')
                if os.path.exists(products_path):
                    self.import_products(products_path)
                else:
                    self.stdout.write(self.style.WARNING(f'製品ファイルが見つかりません: {products_path}'))
            else:
                self.stdout.write(self.style.SUCCESS('BOMデータのみをインポートします'))
        
        # BOMデータのインポート（常に実行）
            bom_path = os.path.join(csv_dir, 'BOM.csv')
            if os.path.exists(bom_path):
                self.import_bom(bom_path)
            else:
                self.stdout.write(self.style.WARNING(f'BOMファイルが見つかりません: {bom_path}'))
        
            self.stdout.write(self.style.SUCCESS('データインポートが完了しました'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'エラーが発生しました: {str(e)}'))
            
    def import_materials(self, file_path):
        try:
            self.stdout.write(f'材料データをインポート中: {file_path}')
            with open(file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                next(csv_reader)  # ヘッダー行をスキップ
                
                materials_count = 0
                for row in csv_reader:
                    material_id, material_name, unit, _ = row
                    
                    Material.objects.update_or_create(
                        material_id=material_id,
                        defaults={
                            'material_name': material_name,
                            'unit': unit,
                        }
                    )
                    materials_count += 1
                
                self.stdout.write(self.style.SUCCESS(f'{materials_count}件の材料データをインポートしました'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'材料データのインポート中にエラーが発生しました: {e}'))
    
    def import_products(self, file_path):
        try:
            self.stdout.write(f'製品データをインポート中: {file_path}')
            with open(file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                next(csv_reader)  # ヘッダー行をスキップ
                
                products_count = 0
                for row in csv_reader:
                    product_id, product_name, production_line = row
                    
                    Product.objects.update_or_create(
                        product_id=product_id,
                        defaults={
                            'product_name': product_name,
                            'production_line': production_line,
                        }
                    )
                    products_count += 1
                
                self.stdout.write(self.style.SUCCESS(f'{products_count}件の製品データをインポートしました'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'製品データのインポート中にエラーが発生しました: {e}'))

    @transaction.atomic
    def import_bom(self, file_path):
        self.stdout.write(f'BOMデータをインポート中: {file_path}')
        count = 0
        errors = 0
    
        with open(file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            header = next(csv_reader)  # ヘッダー行をスキップ
        
            for row in csv_reader:
                if len(row) >= 7:  # 少なくとも7つの列があることを確認
                    try:
                        relation_id = row[0]
                        product_id = row[1]
                        # product_name = row[2]  # 使用しない
                        material_id = row[3]
                        # material_name = row[4]  # 使用しない
                        quantity = row[5]
                        unit_type = row[6]
                    
                        # 製品と材料オブジェクトを取得
                        try:
                            product = Product.objects.get(product_id=product_id)
                            material = Material.objects.get(material_id=material_id)
                        
                            # 数量を数値に変換（カンマを削除）
                            try:
                                # ここを修正：カンマを削除してから変換
                               quantity_float = float(quantity.replace(',', '')) if quantity else 0
                            except (ValueError, TypeError):
                                self.stdout.write(self.style.WARNING(f'  数量の変換エラー: "{quantity}" - 0を使用します'))
                                quantity_float = 0
                        
                            # BOMデータを作成または更新
                            BOM.objects.update_or_create(
                                relation_id=relation_id,
                                product=product,
                                material=material,
                                defaults={
                                    'quantity_per_unit': quantity_float,
                                    'unit_type': unit_type,
                                }
                        )
                            count += 1
                        
                            if count % 100 == 0:  # 進捗状況を100件ごとに表示
                                self.stdout.write(f'  {count}件のBOMをインポート済み...')
                            
                        except Product.DoesNotExist:
                            self.stdout.write(self.style.WARNING(f'  製品が見つかりません: {product_id}'))
                            errors += 1
                        except Material.DoesNotExist:
                            self.stdout.write(self.style.WARNING(f'  材料が見つかりません: {material_id}'))
                            errors += 1
                
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'  行の処理中にエラー: {str(e)}'))
                        errors += 1
        
            self.stdout.write(self.style.SUCCESS(f'BOMデータのインポート完了: {count}件成功, {errors}件エラー'))