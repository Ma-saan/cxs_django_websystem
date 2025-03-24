from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.template import loader
from .models import Jp6b, Jp6bPDF, Jp6bTroubleQuality, Jp6bTroubleSafety, Jp6bInspectionItem, Jp6bInspectionRecord
from .forms import Jp6bForm
from home.forms import SearchForm
from django.db.models import Q
from datetime import datetime

def list_jp6b(request):
    searchform = SearchForm(request.GET)
    if searchform.is_valid():
        keyword = searchform.cleaned_data['keyword']
        jp6bs = Jp6b.objects.using("juten").filter(Q(item_no__contains=keyword)|Q(item_name__contains=keyword))
    else:
        searchform = SearchForm()
        jp6bs = Jp6b.objects.using("juten").all()
    context = {
        'title': 'JP6B製品一覧',
        'jp6bs': jp6bs,
        'searchform': searchform,
    }
    return render(request, 'jp6b/list_jp6b.html', context)


def detail_jp6b(request, item_no):
    try:
        item = Jp6b.objects.using("juten").get(item_no=item_no)
    except Jp6b.DoesNotExist:
        item = None
        
    context = {
        'title': '製品詳細',
        'item': item,
    }
    return render(request, 'jp6b/detail_jp6b.html', context)

def top_jp6b(request):
    context = {
        'title': 'JP6B',
    }
    return render(request, 'jp6b/top_jp6b.html', context)

def trouble_quality_jp6b(request):
    searchform = SearchForm(request.GET)
    if searchform.is_valid():
        keyword = searchform.cleaned_data['keyword']
        trouble_quality = Jp6bTroubleQuality.objects.using("juten").filter(Q(発生日__contains=keyword)|Q(トラブル内容__contains=keyword)|Q(対策__contains=keyword))
    else:
        searchform = SearchForm()    
        trouble_quality = Jp6bTroubleQuality.objects.using("juten").all()
    trouble_quality = sorted(trouble_quality, key=lambda x: x.発生日)    
    context = {
        'title': 'JP6B過去のトラブル<品質>',
        'trouble_quality': trouble_quality,
        'searchform': searchform,
    }
    return render(request, 'jp6b/trouble_quality_jp6b.html', context)

def trouble_safety_jp6b(request):
    searchform = SearchForm(request.GET)
    if searchform.is_valid():
        keyword = searchform.cleaned_data['keyword']
        trouble_safety = Jp6bTroubleSafety.objects.using("juten").filter(Q(発生日__contains=keyword)|Q(トラブル内容__contains=keyword)|Q(対策__contains=keyword))
    else:    
        searchform = SearchForm()   
        trouble_safety = Jp6bTroubleSafety.objects.using("juten").all()
    trouble_safety = sorted(trouble_safety, key=lambda x: x.発生日)     
    context = {
        'title': 'JP6B過去のトラブル<安全>',
        'trouble_safety': trouble_safety,
        'searchform': searchform,
    }
    return render(request, 'jp6b/trouble_safety_jp6b.html', context)

def inspection_page_jp6b(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('item_ids[]')  # 複数のアイテムIDを取得
        result = request.POST.get('result')
        
        for item_id in item_ids:
            if item_id and result:
                item = Jp6bInspectionItem.objects.using("juten").get(pk=item_id)
                inspection_date = datetime.now().date()
                record = Jp6bInspectionRecord(item=item, inspection_date=inspection_date, result=result)
                record.save()
        
        return JsonResponse({'message': '点検結果が保存されました。'})
    else:
        items = Jp6bInspectionItem.objects.using("juten").all()
        # 各アイテムの最新の点検日を計算
        latest_inspection_dates = {}
        for item in items:
            latest_inspection_record = Jp6bInspectionRecord.objects.using("juten").filter(item=item)
            if latest_inspection_record.exists():
                latest_inspection_record = latest_inspection_record.latest('inspection_date')
                latest_inspection_dates[item.id] = latest_inspection_record.inspection_date
            else:
                latest_inspection_dates[item.id] = None
        return render(request, 'jp6b/inspection_page_jp6b.html', {'items': items, 'latest_inspection_dates': latest_inspection_dates})    

def inspection_history_jp6b(request):
    items = Jp6bInspectionItem.objects.using("juten").all()
    latest_inspection_dates = {}
    latest_manager_confirmation_dates = {}

    for item in items:
        latest_inspection = Jp6bInspectionRecord.objects.using("juten").filter(item=item).order_by('-inspection_date').first()
        if latest_inspection:
            latest_inspection_dates[item.id] = latest_inspection.inspection_date
            latest_manager_confirmation_dates[item.id] = latest_inspection.manager_confirmation_date
        else:
            latest_inspection_dates[item.id] = None
            latest_manager_confirmation_dates[item.id] = None

    return render(request, 'jp6b/inspection_history_jp6b.html', {'latest_inspection_dates': latest_inspection_dates, 'latest_manager_confirmation_dates': latest_manager_confirmation_dates, 'items': items})

def save_inspection_results(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('item_ids[]')  # 複数のアイテムIDを取得
        result = request.POST.get('result') == 'true'  # 文字列をブール値に変換
        
        for item_id in item_ids:
            if item_id is not None:
                try:
                    item = Jp6bInspectionItem.objects.using("juten").get(pk=item_id)
                    inspection_date = datetime.now().date()
                    record = Jp6bInspectionRecord(item=item, inspection_date=inspection_date, result=result)
                    record.save()
                except Jp6bInspectionItem.DoesNotExist:
                    return JsonResponse({'error': f'IDが {item_id} のアイテムが見つかりません。'}, status=404)
        
        return JsonResponse({'message': '点検結果が保存されました。'})
    else:
        return JsonResponse({'error': 'POSTリクエストが必要です。'}, status=400)

def save_manager_confirmation(request):
    if request.method == 'POST':
        checked_datetime = request.POST.get('checked_datetime')
        checked_datetime = datetime.strptime(checked_datetime, '%Y-%m-%dT%H:%M:%S.%fZ')
        # 点検日時が存在する全てのレコードを取得
        records = Jp6bInspectionRecord.objects.using("juten").filter(inspection_date__isnull=False, manager_confirmation_date__isnull=True)
        for record in records:
            # 各レコードに対して課長確認日時を保存
            record.manager_confirmation_date = checked_datetime
            record.save()
        return JsonResponse({'message': '課長確認が保存されました。'})
    else:
        return JsonResponse({'error': 'POSTリクエストが必要です。'}, status=400)

def inspection_item_list(request):
    items = Jp6bInspectionItem.objects.using("juten").all()
    return render(request, 'jp6b/inspection_item_list.html', {'items': items})

def inspection_date_list(request, item_id):
    item = get_object_or_404(Jp6bInspectionItem.objects.using("juten"), pk=item_id)
    inspection_records = Jp6bInspectionRecord.objects.using("juten").filter(item=item).order_by('-inspection_date')
    dates_with_manager_confirmation = [
        (record.inspection_date, record.manager_confirmation_date)
        for record in inspection_records
    ]

    return render(request, 'jp6b/inspection_date_list.html', {
        'item': item,
        'dates_with_manager_confirmation': dates_with_manager_confirmation
    })

def edit_warning(request, item_id):
    item = get_object_or_404(Jp6b.objects.using("juten"), pk=item_id)

    if request.method == 'POST':
        form = Jp6bForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('jp6b:list_jp6b')  # 保存後は製品一覧ページにリダイレクト
    else:
        form = Jp6bForm(instance=item)

    return render(request, 'jp6b/edit_warning.html', {'form': form, 'item': item})

def view_pdf(request, pdf_id):
    pdf_file = get_object_or_404(Jp6bPDF.objects.using("juten"), pk=pdf_id)
    return render(request, 'jp6b/view_pdf.html', {'pdf_file': pdf_file})