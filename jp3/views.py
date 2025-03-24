from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.template import loader
from .models import Jp3, Jp3PDF, Jp3TroubleQuality, Jp3TroubleSafety, Jp3InspectionItem, Jp3InspectionRecord
from .forms import Jp3Form
from home.forms import SearchForm
from django.db.models import Q
from datetime import datetime

def list_jp3(request):
    searchform = SearchForm(request.GET)
    if searchform.is_valid():
        keyword = searchform.cleaned_data['keyword']
        jp3s = Jp3.objects.using("juten").filter(Q(item_no__contains=keyword)|Q(item_name__contains=keyword))
    else:
        searchform = SearchForm()
        jp3s = Jp3.objects.using("juten").all()
    context = {
        'title': 'JP3製品一覧',
        'jp3s': jp3s,
        'searchform': searchform,
    }
    return render(request, 'jp3/list_jp3.html', context)


def detail_jp3(request, item_no):
    try:
        item = Jp3.objects.using("juten").get(item_no=item_no)
        pdf_files = item.pdf_files.all()  # related_name を使用して関連する PDF ファイルを取得
    except Jp3.DoesNotExist:
        item = None
        pdf_files = []
    
    context = {
        'title': '製品詳細',
        'item': item,
        'pdf_files': pdf_files,
    }
    return render(request, 'jp3/detail_jp3.html', context)

def top_jp3(request):
    context = {
        'title': 'JP3',
    }
    return render(request, 'jp3/top_jp3.html', context)

def trouble_quality_jp3(request):
    searchform = SearchForm(request.GET)
    if searchform.is_valid():
        keyword = searchform.cleaned_data['keyword']
        trouble_quality = Jp3TroubleQuality.objects.using("juten").filter(Q(発生日__contains=keyword)|Q(トラブル内容__contains=keyword)|Q(対策__contains=keyword))
    else:
        searchform = SearchForm()    
        trouble_quality = Jp3TroubleQuality.objects.using("juten").all()
    trouble_quality = sorted(trouble_quality, key=lambda x: x.発生日)    
    context = {
        'title': 'JP3過去のトラブル<品質>',
        'trouble_quality': trouble_quality,
        'searchform': searchform,
    }
    return render(request, 'jp3/trouble_quality_jp3.html', context)

def trouble_safety_jp3(request):
    searchform = SearchForm(request.GET)
    if searchform.is_valid():
        keyword = searchform.cleaned_data['keyword']
        trouble_safety = Jp3TroubleSafety.objects.using("juten").filter(Q(発生日__contains=keyword)|Q(トラブル内容__contains=keyword)|Q(対策__contains=keyword))
    else:    
        searchform = SearchForm()   
        trouble_safety = Jp3TroubleSafety.objects.using("juten").all()
    trouble_safety = sorted(trouble_safety, key=lambda x: x.発生日)     
    context = {
        'title': 'JP3過去のトラブル<安全>',
        'trouble_safety': trouble_safety,
        'searchform': searchform,
    }
    return render(request, 'jp3/trouble_safety_jp3.html', context)

def inspection_page_jp3(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('item_ids[]')  # 複数のアイテムIDを取得
        result = request.POST.get('result')
        
        for item_id in item_ids:
            if item_id and result:
                item = Jp3InspectionItem.objects.using("juten").get(pk=item_id)
                inspection_date = datetime.now().date()
                record = Jp3InspectionRecord(item=item, inspection_date=inspection_date, result=result)
                record.save()
        
        return JsonResponse({'message': '点検結果が保存されました。'})
    else:
        items = Jp3InspectionItem.objects.using("juten").all()
        #return render(request, 'jp3/inspection_page_jp3.html', {'items': items})
        # 各アイテムの最新の点検日を計算
        latest_inspection_dates = {}
        for item in items:
            latest_inspection_record = Jp3InspectionRecord.objects.using("juten").filter(item=item)
            if latest_inspection_record.exists():
                latest_inspection_record = latest_inspection_record.latest('inspection_date')
                latest_inspection_dates[item.id] = latest_inspection_record.inspection_date
            else:
                latest_inspection_dates[item.id] = None
        return render(request, 'jp3/inspection_page_jp3.html', {'items': items, 'latest_inspection_dates': latest_inspection_dates})    

def inspection_history_jp3(request):
    items = Jp3InspectionItem.objects.using("juten").all()
    latest_inspection_dates = {}
    latest_manager_confirmation_dates = {}

    for item in items:
        latest_inspection = Jp3InspectionRecord.objects.using("juten").filter(item=item).order_by('-inspection_date').first()
        if latest_inspection:
            latest_inspection_dates[item.id] = latest_inspection.inspection_date
            latest_manager_confirmation_dates[item.id] = latest_inspection.manager_confirmation_date
        else:
            latest_inspection_dates[item.id] = None
            latest_manager_confirmation_dates[item.id] = None

    return render(request, 'jp3/inspection_history_jp3.html', {'latest_inspection_dates': latest_inspection_dates, 'latest_manager_confirmation_dates': latest_manager_confirmation_dates, 'items': items})

def save_inspection_results(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('item_ids[]')  # 複数のアイテムIDを取得
        result = request.POST.get('result') == 'true'  # 文字列をブール値に変換
        
        for item_id in item_ids:
            if item_id is not None:
                try:
                    item = Jp3InspectionItem.objects.using("juten").get(pk=item_id)
                    inspection_date = datetime.now().date()
                    record = Jp3InspectionRecord(item=item, inspection_date=inspection_date, result=result)
                    record.save()
                except Jp3InspectionItem.DoesNotExist:
                    return JsonResponse({'error': f'IDが {item_id} のアイテムが見つかりません。'}, status=404)
        
        return JsonResponse({'message': '点検結果が保存されました。'})
    else:
        return JsonResponse({'error': 'POSTリクエストが必要です。'}, status=400)

def save_manager_confirmation(request):
    if request.method == 'POST':
        checked_datetime = request.POST.get('checked_datetime')
        checked_datetime = datetime.strptime(checked_datetime, '%Y-%m-%dT%H:%M:%S.%fZ')
        # 点検日時が存在する全てのレコードを取得
        records = Jp3InspectionRecord.objects.using("juten").filter(inspection_date__isnull=False, manager_confirmation_date__isnull=True)
        for record in records:
            # 各レコードに対して課長確認日時を保存
            record.manager_confirmation_date = checked_datetime
            record.save()
        return JsonResponse({'message': '課長確認が保存されました。'})
    else:
        return JsonResponse({'error': 'POSTリクエストが必要です。'}, status=400)

def inspection_item_list(request):
    items = Jp3InspectionItem.objects.using("juten").all()
    return render(request, 'jp3/inspection_item_list.html', {'items': items})

def inspection_date_list(request, item_id):
    item = get_object_or_404(Jp3InspectionItem.objects.using("juten"), pk=item_id)
    inspection_records = Jp3InspectionRecord.objects.using("juten").filter(item=item).order_by('-inspection_date')
    dates_with_manager_confirmation = [
        (record.inspection_date, record.manager_confirmation_date)
        for record in inspection_records
    ]

    return render(request, 'jp3/inspection_date_list.html', {
        'item': item,
        'dates_with_manager_confirmation': dates_with_manager_confirmation
    })

def edit_warning(request, item_id):
    item = get_object_or_404(Jp3.objects.using("juten"), pk=item_id)

    if request.method == 'POST':
        form = Jp3Form(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('jp3:list_jp3')  # 保存後は製品一覧ページにリダイレクト
        else:
            # バリデーションエラーがある場合はエラーメッセージを表示するかログに記録する
            print(form.errors)
    else:
        form = Jp3Form(instance=item)

    return render(request, 'jp3/edit_warning.html', {'form': form, 'item': item})

def view_pdf(request, pdf_id):
    pdf_file = get_object_or_404(Jp3PDF.objects.using("juten"), pk=pdf_id)
    return render(request, 'jp3/view_pdf.html', {'pdf_file': pdf_file})