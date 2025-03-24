from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.template import loader
from .models import Jp7, Jp7PDF, Jp7TroubleQuality, Jp7TroubleSafety, Jp7aInspectionItem, Jp7aInspectionRecord, Jp7bInspectionItem, Jp7bInspectionRecord, Jp7cInspectionItem, Jp7cInspectionRecord
from .forms import Jp7Form
from home.forms import SearchForm
from django.db.models import Q
from datetime import datetime

def list_jp7(request):
    searchform = SearchForm(request.GET)
    if searchform.is_valid():
        keyword = searchform.cleaned_data['keyword']
        jp7s = Jp7.objects.using("juten").filter(Q(item_no__contains=keyword)|Q(item_name__contains=keyword))
    else:
        searchform = SearchForm()
        jp7s = Jp7.objects.using("juten").all()
    context = {
        'title': 'JP7製品一覧',
        'jp7s': jp7s,
        'searchform': searchform,
    }
    return render(request, 'jp7/list_jp7.html', context)


def detail_jp7(request, item_no):
    try:
        item = Jp7.objects.using("juten").get(item_no=item_no)
    except Jp7.DoesNotExist:
        item = None
        
    context = {
        'title': '製品詳細',
        'item': item,
    }
    return render(request, 'jp7/detail_jp7.html', context)

def top_jp7(request):
    context = {
        'title': 'JP7',
    }
    return render(request, 'jp7/top_jp7.html', context)

def trouble_quality_jp7(request):
    searchform = SearchForm(request.GET)
    if searchform.is_valid():
        keyword = searchform.cleaned_data['keyword']
        trouble_quality = Jp7TroubleQuality.objects.using("juten").filter(Q(発生日__contains=keyword)|Q(トラブル内容__contains=keyword)|Q(対策__contains=keyword))
    else:
        searchform = SearchForm()    
        trouble_quality = Jp7TroubleQuality.objects.using("juten").all()
    trouble_quality = sorted(trouble_quality, key=lambda x: x.発生日)    
    context = {
        'title': 'JP7過去のトラブル<品質>',
        'trouble_quality': trouble_quality,
        'searchform': searchform,
    }
    return render(request, 'jp7/trouble_quality_jp7.html', context)

def trouble_safety_jp7(request):
    searchform = SearchForm(request.GET)
    if searchform.is_valid():
        keyword = searchform.cleaned_data['keyword']
        trouble_safety = Jp7TroubleSafety.objects.using("juten").filter(Q(発生日__contains=keyword)|Q(トラブル内容__contains=keyword)|Q(対策__contains=keyword))
    else:    
        searchform = SearchForm()   
        trouble_safety = Jp7TroubleSafety.objects.using("juten").all()
    trouble_safety = sorted(trouble_safety, key=lambda x: x.発生日)    
    context = {
        'title': 'JP7過去のトラブル<安全>',
        'trouble_safety': trouble_safety,
        'searchform': searchform,
    }
    return render(request, 'jp7/trouble_safety_jp7.html', context)

def inspection_page_jp7(request):
    context = {
        'title': 'JP7保守点検',
    }
    return render(request, 'jp7/inspection_page_jp7.html', context)

def inspection_page_jp7a(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('item_ids[]')  # 複数のアイテムIDを取得
        result = request.POST.get('result')
        
        for item_id in item_ids:
            if item_id and result:
                item = Jp7aInspectionItem.objects.using("juten").get(pk=item_id)
                inspection_date = datetime.now().date()
                record = Jp7aInspectionRecord(item=item, inspection_date=inspection_date, result=result)
                record.save()
        
        return JsonResponse({'message': '点検結果が保存されました。'})
    else:
        items = Jp7aInspectionItem.objects.using("juten").all()
        #return render(request, 'jp3/inspection_page_jp3.html', {'items': items})
        # 各アイテムの最新の点検日を計算
        latest_inspection_dates = {}
        for item in items:
            latest_inspection_record = Jp7aInspectionRecord.objects.using("juten").filter(item=item)
            if latest_inspection_record.exists():
                latest_inspection_record = latest_inspection_record.latest('inspection_date')
                latest_inspection_dates[item.id] = latest_inspection_record.inspection_date
            else:
                latest_inspection_dates[item.id] = None
        return render(request, 'jp7/inspection_page_jp7a.html', {'items': items, 'latest_inspection_dates': latest_inspection_dates})    

def inspection_history_jp7a(request):
    items = Jp7aInspectionItem.objects.using("juten").all()
    latest_inspection_dates = {}
    latest_manager_confirmation_dates = {}

    for item in items:
        latest_inspection = Jp7aInspectionRecord.objects.using("juten").filter(item=item).order_by('-inspection_date').first()
        if latest_inspection:
            latest_inspection_dates[item.id] = latest_inspection.inspection_date
            latest_manager_confirmation_dates[item.id] = latest_inspection.manager_confirmation_date
        else:
            latest_inspection_dates[item.id] = None
            latest_manager_confirmation_dates[item.id] = None

    return render(request, 'jp7/inspection_history_jp7a.html', {'latest_inspection_dates': latest_inspection_dates, 'latest_manager_confirmation_dates': latest_manager_confirmation_dates, 'items': items})

def save_inspection_results_a(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('item_ids[]')  # 複数のアイテムIDを取得
        result = request.POST.get('result') == 'true'  # 文字列をブール値に変換
        
        for item_id in item_ids:
            if item_id is not None:
                try:
                    item = Jp7aInspectionItem.objects.using("juten").get(pk=item_id)
                    inspection_date = datetime.now().date()
                    record = Jp7aInspectionRecord(item=item, inspection_date=inspection_date, result=result)
                    record.save()
                except Jp7aInspectionItem.DoesNotExist:
                    return JsonResponse({'error': f'IDが {item_id} のアイテムが見つかりません。'}, status=404)
        
        return JsonResponse({'message': '点検結果が保存されました。'})
    else:
        return JsonResponse({'error': 'POSTリクエストが必要です。'}, status=400)

def save_manager_confirmation_a(request):
    if request.method == 'POST':
        checked_datetime = request.POST.get('checked_datetime')
        checked_datetime = datetime.strptime(checked_datetime, '%Y-%m-%dT%H:%M:%S.%fZ')
        # 点検日時が存在する全てのレコードを取得
        records = Jp7aInspectionRecord.objects.using("juten").filter(inspection_date__isnull=False, manager_confirmation_date__isnull=True)
        for record in records:
            # 各レコードに対して課長確認日時を保存
            record.manager_confirmation_date = checked_datetime
            record.save()
        return JsonResponse({'message': '課長確認が保存されました。'})
    else:
        return JsonResponse({'error': 'POSTリクエストが必要です。'}, status=400)

def inspection_page_jp7b(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('item_ids[]')  # 複数のアイテムIDを取得
        result = request.POST.get('result')
        
        for item_id in item_ids:
            if item_id and result:
                item = Jp7bInspectionItem.objects.using("juten").get(pk=item_id)
                inspection_date = datetime.now().date()
                record = Jp7bInspectionRecord(item=item, inspection_date=inspection_date, result=result)
                record.save()
        
        return JsonResponse({'message': '点検結果が保存されました。'})
    else:
        items = Jp7bInspectionItem.objects.using("juten").all()
        #return render(request, 'jp3/inspection_page_jp3.html', {'items': items})
        # 各アイテムの最新の点検日を計算
        latest_inspection_dates = {}
        for item in items:
            latest_inspection_record = Jp7bInspectionRecord.objects.using("juten").filter(item=item)
            if latest_inspection_record.exists():
                latest_inspection_record = latest_inspection_record.latest('inspection_date')
                latest_inspection_dates[item.id] = latest_inspection_record.inspection_date
            else:
                latest_inspection_dates[item.id] = None
        return render(request, 'jp7/inspection_page_jp7b.html', {'items': items, 'latest_inspection_dates': latest_inspection_dates})    

def inspection_history_jp7b(request):
    items = Jp7bInspectionItem.objects.using("juten").all()
    latest_inspection_dates = {}
    latest_manager_confirmation_dates = {}

    for item in items:
        latest_inspection = Jp7bInspectionRecord.objects.using("juten").filter(item=item).order_by('-inspection_date').first()
        if latest_inspection:
            latest_inspection_dates[item.id] = latest_inspection.inspection_date
            latest_manager_confirmation_dates[item.id] = latest_inspection.manager_confirmation_date
        else:
            latest_inspection_dates[item.id] = None
            latest_manager_confirmation_dates[item.id] = None

    return render(request, 'jp7/inspection_history_jp7b.html', {'latest_inspection_dates': latest_inspection_dates, 'latest_manager_confirmation_dates': latest_manager_confirmation_dates, 'items': items})

def save_inspection_results_b(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('item_ids[]')  # 複数のアイテムIDを取得
        result = request.POST.get('result') == 'true'  # 文字列をブール値に変換
        
        for item_id in item_ids:
            if item_id is not None:
                try:
                    item = Jp7bInspectionItem.objects.using("juten").get(pk=item_id)
                    inspection_date = datetime.now().date()
                    record = Jp7bInspectionRecord(item=item, inspection_date=inspection_date, result=result)
                    record.save()
                except Jp7bInspectionItem.DoesNotExist:
                    return JsonResponse({'error': f'IDが {item_id} のアイテムが見つかりません。'}, status=404)
        
        return JsonResponse({'message': '点検結果が保存されました。'})
    else:
        return JsonResponse({'error': 'POSTリクエストが必要です。'}, status=400)

def save_manager_confirmation_b(request):
    if request.method == 'POST':
        checked_datetime = request.POST.get('checked_datetime')
        checked_datetime = datetime.strptime(checked_datetime, '%Y-%m-%dT%H:%M:%S.%fZ')
        # 点検日時が存在する全てのレコードを取得
        records = Jp7bInspectionRecord.objects.using("juten").filter(inspection_date__isnull=False, manager_confirmation_date__isnull=True)
        for record in records:
            # 各レコードに対して課長確認日時を保存
            record.manager_confirmation_date = checked_datetime
            record.save()
        return JsonResponse({'message': '課長確認が保存されました。'})
    else:
        return JsonResponse({'error': 'POSTリクエストが必要です。'}, status=400)

def inspection_page_jp7c(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('item_ids[]')  # 複数のアイテムIDを取得
        result = request.POST.get('result')
        
        for item_id in item_ids:
            if item_id and result:
                item = Jp7cInspectionItem.objects.using("juten").get(pk=item_id)
                inspection_date = datetime.now().date()
                record = Jp7cInspectionRecord(item=item, inspection_date=inspection_date, result=result)
                record.save()
        
        return JsonResponse({'message': '点検結果が保存されました。'})
    else:
        items = Jp7cInspectionItem.objects.using("juten").all()
        #return render(request, 'jp3/inspection_page_jp3.html', {'items': items})
        # 各アイテムの最新の点検日を計算
        latest_inspection_dates = {}
        for item in items:
            latest_inspection_record = Jp7cInspectionRecord.objects.using("juten").filter(item=item)
            if latest_inspection_record.exists():
                latest_inspection_record = latest_inspection_record.latest('inspection_date')
                latest_inspection_dates[item.id] = latest_inspection_record.inspection_date
            else:
                latest_inspection_dates[item.id] = None
        return render(request, 'jp7/inspection_page_jp7c.html', {'items': items, 'latest_inspection_dates': latest_inspection_dates})    

def inspection_history_jp7c(request):
    items = Jp7cInspectionItem.objects.using("juten").all()
    latest_inspection_dates = {}
    latest_manager_confirmation_dates = {}

    for item in items:
        latest_inspection = Jp7cInspectionRecord.objects.using("juten").filter(item=item).order_by('-inspection_date').first()
        if latest_inspection:
            latest_inspection_dates[item.id] = latest_inspection.inspection_date
            latest_manager_confirmation_dates[item.id] = latest_inspection.manager_confirmation_date
        else:
            latest_inspection_dates[item.id] = None
            latest_manager_confirmation_dates[item.id] = None

    return render(request, 'jp7/inspection_history_jp7c.html', {'latest_inspection_dates': latest_inspection_dates, 'latest_manager_confirmation_dates': latest_manager_confirmation_dates, 'items': items})

def save_inspection_results_c(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('item_ids[]')  # 複数のアイテムIDを取得
        result = request.POST.get('result') == 'true'  # 文字列をブール値に変換
        
        for item_id in item_ids:
            if item_id is not None:
                try:
                    item = Jp7cInspectionItem.objects.using("juten").get(pk=item_id)
                    inspection_date = datetime.now().date()
                    record = Jp7cInspectionRecord(item=item, inspection_date=inspection_date, result=result)
                    record.save()
                except Jp7cInspectionItem.DoesNotExist:
                    return JsonResponse({'error': f'IDが {item_id} のアイテムが見つかりません。'}, status=404)
        
        return JsonResponse({'message': '点検結果が保存されました。'})
    else:
        return JsonResponse({'error': 'POSTリクエストが必要です。'}, status=400)

def save_manager_confirmation_c(request):
    if request.method == 'POST':
        checked_datetime = request.POST.get('checked_datetime')
        checked_datetime = datetime.strptime(checked_datetime, '%Y-%m-%dT%H:%M:%S.%fZ')
        # 点検日時が存在する全てのレコードを取得
        records = Jp7cInspectionRecord.objects.using("juten").filter(inspection_date__isnull=False, manager_confirmation_date__isnull=True)
        for record in records:
            # 各レコードに対して課長確認日時を保存
            record.manager_confirmation_date = checked_datetime
            record.save()
        return JsonResponse({'message': '課長確認が保存されました。'})
    else:
        return JsonResponse({'error': 'POSTリクエストが必要です。'}, status=400)

def inspection_item_list_a(request):
    items = Jp7aInspectionItem.objects.using("juten").all()
    return render(request, 'jp7/inspection_item_list_a.html', {'items': items})

def inspection_date_list_a(request, item_id):
    item = get_object_or_404(Jp7aInspectionItem.objects.using("juten"), pk=item_id)
    inspection_records = Jp7aInspectionRecord.objects.using("juten").filter(item=item).order_by('-inspection_date')
    dates_with_manager_confirmation = [
        (record.inspection_date, record.manager_confirmation_date)
        for record in inspection_records
    ]

    return render(request, 'jp7/inspection_date_list_a.html', {
        'item': item,
        'dates_with_manager_confirmation': dates_with_manager_confirmation
    })

def inspection_item_list_b(request):
    items = Jp7bInspectionItem.objects.using("juten").all()
    return render(request, 'jp7/inspection_item_list_b.html', {'items': items})

def inspection_date_list_b(request, item_id):
    item = get_object_or_404(Jp7bInspectionItem.objects.using("juten"), pk=item_id)
    inspection_records = Jp7bInspectionRecord.objects.using("juten").filter(item=item).order_by('-inspection_date')
    dates_with_manager_confirmation = [
        (record.inspection_date, record.manager_confirmation_date)
        for record in inspection_records
    ]

    return render(request, 'jp7/inspection_date_list_b.html', {
        'item': item,
        'dates_with_manager_confirmation': dates_with_manager_confirmation
    })

def inspection_item_list_c(request):
    items = Jp7cInspectionItem.objects.using("juten").all()
    return render(request, 'jp7/inspection_item_list_c.html', {'items': items})

def inspection_date_list_c(request, item_id):
    item = get_object_or_404(Jp7cInspectionItem.objects.using("juten"), pk=item_id)
    inspection_records = Jp7cInspectionRecord.objects.using("juten").filter(item=item).order_by('-inspection_date')
    dates_with_manager_confirmation = [
        (record.inspection_date, record.manager_confirmation_date)
        for record in inspection_records
    ]

    return render(request, 'jp7/inspection_date_list_c.html', {
        'item': item,
        'dates_with_manager_confirmation': dates_with_manager_confirmation
    })

def edit_warning(request, item_id):
    item = get_object_or_404(Jp7.objects.using("juten"), pk=item_id)

    if request.method == 'POST':
        form = Jp7Form(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('jp7:list_jp7')  # 保存後は製品一覧ページにリダイレクト
    else:
        form = Jp7Form(instance=item)

    return render(request, 'jp7/edit_warning.html', {'form': form, 'item': item})

def view_pdf(request, pdf_id):
    pdf_file = get_object_or_404(Jp7PDF.objects.using("juten"), pk=pdf_id)
    return render(request, 'jp7/view_pdf.html', {'pdf_file': pdf_file})