from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.template import loader
from .models import Jp6a, Jp6aPDF, Jp6aTroubleQuality, Jp6aTroubleSafety, Jp6aInspectionItem, Jp6aInspectionRecord
from .forms import Jp6aForm
from home.forms import SearchForm
from django.db.models import Q
from datetime import datetime

def list_jp6a(request):
    searchform = SearchForm(request.GET)
    if searchform.is_valid():
        keyword = searchform.cleaned_data['keyword']
        jp6as = Jp6a.objects.using("juten").filter(Q(item_no__contains=keyword)|Q(item_name__contains=keyword))
    else:
        searchform = SearchForm()
        jp6as = Jp6a.objects.using("juten").all()
    context = {
        'title': 'JP6A製品一覧',
        'jp6as': jp6as,
        'searchform': searchform,
    }
    return render(request, 'jp6a/list_jp6a.html', context)


def detail_jp6a(request, item_no):
    try:
        item = Jp6a.objects.using("juten").get(item_no=item_no)
    except Jp6a.DoesNotExist:
        item = None
        
    context = {
        'title': '製品詳細',
        'item': item,
    }
    return render(request, 'jp6a/detail_jp6a.html', context)

def top_jp6a(request):
    context = {
        'title': 'JP6A',
    }
    return render(request, 'jp6a/top_jp6a.html', context)

def trouble_quality_jp6a(request):
    searchform = SearchForm(request.GET)
    if searchform.is_valid():
        keyword = searchform.cleaned_data['keyword']
        trouble_quality = Jp6aTroubleQuality.objects.using("juten").filter(Q(発生日__contains=keyword)|Q(トラブル内容__contains=keyword)|Q(対策__contains=keyword))
    else:
        searchform = SearchForm()    
        trouble_quality = Jp6aTroubleQuality.objects.using("juten").all()
    trouble_quality = sorted(trouble_quality, key=lambda x: x.発生日)    
    context = {
        'title': 'JP6A過去のトラブル<品質>',
        'trouble_quality': trouble_quality,
        'searchform': searchform,
    }
    return render(request, 'jp6a/trouble_quality_jp6a.html', context)

def trouble_safety_jp6a(request):
    searchform = SearchForm(request.GET)
    if searchform.is_valid():
        keyword = searchform.cleaned_data['keyword']
        trouble_safety = Jp6aTroubleSafety.objects.using("juten").filter(Q(発生日__contains=keyword)|Q(トラブル内容__contains=keyword)|Q(対策__contains=keyword))
    else:    
        searchform = SearchForm()   
        trouble_safety = Jp6aTroubleSafety.objects.using("juten").all()
    trouble_safety = sorted(trouble_safety, key=lambda x: x.発生日)     
    context = {
        'title': 'JP6A過去のトラブル<安全>',
        'trouble_safety': trouble_safety,
        'searchform': searchform,
    }
    return render(request, 'jp6a/trouble_safety_jp6a.html', context)

def inspection_page_jp6a(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('item_ids[]')  # 複数のアイテムIDを取得
        result = request.POST.get('result')
        
        for item_id in item_ids:
            if item_id and result:
                item = Jp6aInspectionItem.objects.using("juten").get(pk=item_id)
                inspection_date = datetime.now().date()
                record = Jp6aInspectionRecord(item=item, inspection_date=inspection_date, result=result)
                record.save()
        
        return JsonResponse({'message': '点検結果が保存されました。'})
    else:
        items = Jp6aInspectionItem.objects.using("juten").all()
        #return render(request, 'jp3/inspection_page_jp3.html', {'items': items})
        # 各アイテムの最新の点検日を計算
        latest_inspection_dates = {}
        for item in items:
            latest_inspection_record = Jp6aInspectionRecord.objects.using("juten").filter(item=item)
            if latest_inspection_record.exists():
                latest_inspection_record = latest_inspection_record.latest('inspection_date')
                latest_inspection_dates[item.id] = latest_inspection_record.inspection_date
            else:
                latest_inspection_dates[item.id] = None
        return render(request, 'jp6a/inspection_page_jp6a.html', {'items': items, 'latest_inspection_dates': latest_inspection_dates})    

def inspection_history_jp6a(request):
    items = Jp6aInspectionItem.objects.using("juten").all()
    latest_inspection_dates = {}
    latest_manager_confirmation_dates = {}

    for item in items:
        latest_inspection = Jp6aInspectionRecord.objects.using("juten").filter(item=item).order_by('-inspection_date').first()
        if latest_inspection:
            latest_inspection_dates[item.id] = latest_inspection.inspection_date
            latest_manager_confirmation_dates[item.id] = latest_inspection.manager_confirmation_date
        else:
            latest_inspection_dates[item.id] = None
            latest_manager_confirmation_dates[item.id] = None

    return render(request, 'jp6a/inspection_history_jp6a.html', {'latest_inspection_dates': latest_inspection_dates, 'latest_manager_confirmation_dates': latest_manager_confirmation_dates, 'items': items})

def save_inspection_results(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('item_ids[]')  # 複数のアイテムIDを取得
        result = request.POST.get('result') == 'true'  # 文字列をブール値に変換
        
        for item_id in item_ids:
            if item_id is not None:
                try:
                    item = Jp6aInspectionItem.objects.using("juten").get(pk=item_id)
                    inspection_date = datetime.now().date()
                    record = Jp6aInspectionRecord(item=item, inspection_date=inspection_date, result=result)
                    record.save()
                except Jp6aInspectionItem.DoesNotExist:
                    return JsonResponse({'error': f'IDが {item_id} のアイテムが見つかりません。'}, status=404)
        
        return JsonResponse({'message': '点検結果が保存されました。'})
    else:
        return JsonResponse({'error': 'POSTリクエストが必要です。'}, status=400)

def save_manager_confirmation(request):
    if request.method == 'POST':
        checked_datetime = request.POST.get('checked_datetime')
        checked_datetime = datetime.strptime(checked_datetime, '%Y-%m-%dT%H:%M:%S.%fZ')
        # 点検日時が存在する全てのレコードを取得
        records = Jp6aInspectionRecord.objects.using("juten").filter(inspection_date__isnull=False, manager_confirmation_date__isnull=True)
        for record in records:
            # 各レコードに対して課長確認日時を保存
            record.manager_confirmation_date = checked_datetime
            record.save()
        return JsonResponse({'message': '課長確認が保存されました。'})
    else:
        return JsonResponse({'error': 'POSTリクエストが必要です。'}, status=400)

def inspection_item_list(request):
    items = Jp6aInspectionItem.objects.using("juten").all()
    return render(request, 'jp6a/inspection_item_list.html', {'items': items})

def inspection_date_list(request, item_id):
    item = get_object_or_404(Jp6aInspectionItem.objects.using("juten"), pk=item_id)
    inspection_records = Jp6aInspectionRecord.objects.using("juten").filter(item=item).order_by('-inspection_date')
    dates_with_manager_confirmation = [
        (record.inspection_date, record.manager_confirmation_date)
        for record in inspection_records
    ]

    return render(request, 'jp6a/inspection_date_list.html', {
        'item': item,
        'dates_with_manager_confirmation': dates_with_manager_confirmation
    })

def edit_warning(request, item_id):
    item = get_object_or_404(Jp6a.objects.using("juten"), pk=item_id)

    if request.method == 'POST':
        form = Jp6aForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('jp6a:list_jp6a')  # 保存後は製品一覧ページにリダイレクト
    else:
        form = Jp6aForm(instance=item)

    return render(request, 'jp6a/edit_warning.html', {'form': form, 'item': item})

def view_pdf(request, pdf_id):
    pdf_file = get_object_or_404(Jp6aPDF.objects.using("juten"), pk=pdf_id)
    return render(request, 'jp6a/view_pdf.html', {'pdf_file': pdf_file})