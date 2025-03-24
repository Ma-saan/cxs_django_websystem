import csv
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.views import View
from .models import Schedule,ScheduleAppSchedule,WorkLineAssignment
from .forms import ScheduleForm
from schedule_app.models import ScheduleAppSchedule
import datetime
from django.views.decorators.http import require_POST
import json
from django.http import JsonResponse



class UploadView(View):
    def get(self, request):
        return render(request, 'upload.html')

    def post(self, request):
        if 'csv_file' in request.FILES:
            csv_file = request.FILES['csv_file']
            fs = FileSystemStorage()
            file_path = fs.save(csv_file.name, csv_file)
            
            try:
                # CSVファイルを読み込み、データを保存
                schedule_data = self.load_schedule_data(fs.path(file_path))
                for data in schedule_data:
                    Schedule.objects.create(**data)
                fs.delete(file_path)  # アップロードされたファイルを削除
                return render(request, 'upload.html', {'success': 'File uploaded and data saved successfully!'})
            except Exception as e:
                return render(request, 'upload.html', {'error': f'Error processing file: {str(e)}'})
            finally:
                if file_path:
                    fs.delete(file_path)
        return render(request, 'upload.html', {'error': 'No file uploaded!'})

    def load_schedule_data(self, file_path):
        schedule_data = []
        encodings = ['shift_jis', 'cp932', 'euc_jp']
        
        for encoding in encodings:
            try:
                with open(file_path, newline='', encoding=encoding) as csvfile:
                    for _ in range(4):
                        next(csvfile)
                        
                    reader = csv.reader(csvfile)
                    next(reader)
                    
                    for row in reader:
                        if len(row) >= 19 and any(row):
                            schedule_data.append({
                                'manufacturing_filling': row[0].strip(),
                                'production_date': row[2].strip(),
                                'work_center_number': row[3].strip(),
                                'work_center_name': row[4].strip(),
                                'product_number': row[8].strip(),
                                'product_name': row[10].strip(),
                                'production_quantity': row[14].strip(),
                                'personnel': row[16].strip(),
                                'order_number': row[17].strip(),
                                'work_order_status': row[18].strip()
                            })
                    break
            except UnicodeDecodeError:
                if encoding == encodings[-1]:
                    raise UnicodeDecodeError(f"Could not decode file with any of these encodings: {encodings}")
                continue
            except Exception as e:
                raise Exception(f"Error reading CSV file: {str(e)}")
                
        return schedule_data

class ScheduleView(View):
    def get(self, request):
        schedule_data = Schedule.objects.all().values(
            'id', 'order_number',
            'product_name', 'product_number', 'production_date', 
            'production_quantity', 'work_center_name', 'work_center_number', 
            'work_order_status'
        ).order_by('-production_date')
        return render(request, 'schedule.html', {'schedule_data': schedule_data})

    def post(self, request):
        if 'delete' in request.POST:
            selected_rows = request.POST.getlist('selected_rows')
            
            for row_id in selected_rows:
                schedule = Schedule.objects.get(id=row_id)
                schedule.delete()
            
            return redirect('schedule_view')
        return self.get(request)
    
# schedule_app/views.py に追加

# ライン割り当て画面
def line_assignment_view(request):
    # 未割り当ての予定を取得
    unassigned_schedules = ScheduleAppSchedule.objects.filter(
        assignments__isnull=True
    )
    
    # ライン情報を取得（例：固定値または別のモデルから）
    lines = ['Line 1', 'Line 2', 'Line 3']  # 実際のライン名に置き換え
    
    # 日付選択（デフォルトは今日）
    selected_date = request.GET.get('date', datetime.date.today().strftime('%Y-%m-%d'))
    
    # 割り当て済みの予定を取得
    assignments = WorkLineAssignment.objects.filter(
        assigned_date=selected_date
    ).select_related('schedule')
    
    # ライン別に割り当てを整理
    line_assignments = {}
    for line in lines:
        line_assignments[line] = assignments.filter(
            line_number=line
        ).order_by('sequence_number')
    
    context = {
        'unassigned_schedules': unassigned_schedules,
        'lines': lines,
        'line_assignments': line_assignments,
        'selected_date': selected_date,
    }
    return render(request, 'schedule_app/line_assignment.html', context)

# Ajax経由で割り当てを更新
@require_POST
def update_assignment(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = json.loads(request.body)
        schedule_id = data.get('schedule_id')
        line = data.get('line')
        sequence = data.get('sequence')
        date = data.get('date')
        
        try:
            # 既存の割り当てを更新または新規作成
            assignment, created = WorkLineAssignment.objects.update_or_create(
                schedule_id=schedule_id,
                assigned_date=date,
                defaults={
                    'line_number': line,
                    'sequence_number': sequence,
                }
            )
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

# インスタンスを作成
upload_view = UploadView.as_view()
schedule_view = ScheduleView.as_view()