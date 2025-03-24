from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.utils import timezone
from .models import EtcTroubleQuality, EtcTroubleSafety, PDFFile
from jp1.models import Jp1, Jp1TroubleQuality, Jp1TroubleSafety
from jp2.models import Jp2, Jp2TroubleQuality, Jp2TroubleSafety
from jp3.models import Jp3, Jp3TroubleQuality, Jp3TroubleSafety
from jp4.models import Jp4, Jp4TroubleQuality, Jp4TroubleSafety
from jp6a.models import Jp6a, Jp6aTroubleQuality, Jp6aTroubleSafety
from jp6b.models import Jp6b, Jp6bTroubleQuality, Jp6bTroubleSafety
from jp7.models import Jp7, Jp7TroubleQuality, Jp7TroubleSafety
from home.forms import SearchForm
from django.db.models import Q


def list_home(request):
    context = {
        'title': '掛川工場充填課',
    }
    return render(request, 'home/list_home.html', context)

def top_etc(request):
    context = {
        'title': 'その他のライン',
    }
    return render(request, 'home/top_etc.html', context)

def trouble_quality_etc(request):
    searchform = SearchForm(request.GET)
    if searchform.is_valid():
        keyword = searchform.cleaned_data['keyword']
        trouble_quality = EtcTroubleQuality.objects.using("juten").filter(Q(発生日__contains=keyword)|Q(トラブル内容__contains=keyword)|Q(対策__contains=keyword))
    else:
        searchform = SearchForm() 
        trouble_quality = EtcTroubleQuality.objects.using("juten").all()
    trouble_quality = sorted(trouble_quality, key=lambda x: x.発生日)    
    context = {
        'title': 'その他の過去のトラブル<品質>',
        'trouble_quality': trouble_quality,
        'searchform': searchform,
    }
    return render(request, 'home/trouble_quality_etc.html', context)

def trouble_safety_etc(request):
    searchform = SearchForm(request.GET)
    if searchform.is_valid():
        keyword = searchform.cleaned_data['keyword']
        trouble_safety = EtcTroubleSafety.objects.using("juten").filter(Q(発生日__contains=keyword)|Q(トラブル内容__contains=keyword)|Q(対策__contains=keyword))
    else:
        searchform = SearchForm()
        trouble_safety = EtcTroubleSafety.objects.using("juten").all()
    trouble_safety = sorted(trouble_safety, key=lambda x: x.発生日)    
    context = {
        'title': 'その他の過去のトラブル<安全>',
        'trouble_safety': trouble_safety,
        'searchform': searchform,
    }
    return render(request, 'home/trouble_safety_etc.html', context)

def top_all(request):
    context = {
        'title': '全ライン',
    }
    return render(request, 'home/top_all.html', context)

def trouble_quality_all(request):
    searchform = SearchForm(request.GET)
    if searchform.is_valid():
        keyword = searchform.cleaned_data['keyword']
        trouble_quality_etc = EtcTroubleQuality.objects.using("juten").filter(Q(発生日__contains=keyword)|Q(トラブル内容__contains=keyword)|Q(対策__contains=keyword))
        trouble_quality_jp1 = Jp1TroubleQuality.objects.using("juten").filter(Q(発生日__contains=keyword)|Q(トラブル内容__contains=keyword)|Q(対策__contains=keyword))
        trouble_quality_jp2 = Jp2TroubleQuality.objects.using("juten").filter(Q(発生日__contains=keyword)|Q(トラブル内容__contains=keyword)|Q(対策__contains=keyword))
        trouble_quality_jp3 = Jp3TroubleQuality.objects.using("juten").filter(Q(発生日__contains=keyword)|Q(トラブル内容__contains=keyword)|Q(対策__contains=keyword))
        trouble_quality_jp4 = Jp4TroubleQuality.objects.using("juten").filter(Q(発生日__contains=keyword)|Q(トラブル内容__contains=keyword)|Q(対策__contains=keyword))
        trouble_quality_jp6a = Jp6aTroubleQuality.objects.using("juten").filter(Q(発生日__contains=keyword)|Q(トラブル内容__contains=keyword)|Q(対策__contains=keyword))
        trouble_quality_jp6b = Jp6bTroubleQuality.objects.using("juten").filter(Q(発生日__contains=keyword)|Q(トラブル内容__contains=keyword)|Q(対策__contains=keyword))
        trouble_quality_jp7 = Jp7TroubleQuality.objects.using("juten").filter(Q(発生日__contains=keyword)|Q(トラブル内容__contains=keyword)|Q(対策__contains=keyword))
    else:
        searchform = SearchForm() 
        trouble_quality_etc = EtcTroubleQuality.objects.using("juten").all()
        trouble_quality_jp1 = Jp1TroubleQuality.objects.using("juten").all()
        trouble_quality_jp2 = Jp2TroubleQuality.objects.using("juten").all()
        trouble_quality_jp3 = Jp3TroubleQuality.objects.using("juten").all()
        trouble_quality_jp4 = Jp4TroubleQuality.objects.using("juten").all()
        trouble_quality_jp6a = Jp6aTroubleQuality.objects.using("juten").all()
        trouble_quality_jp6b = Jp6bTroubleQuality.objects.using("juten").all()
        trouble_quality_jp7 = Jp7TroubleQuality.objects.using("juten").all()

    all_trouble_quality = trouble_quality_jp1.union(trouble_quality_jp2, trouble_quality_jp3, trouble_quality_jp4, trouble_quality_jp6a, trouble_quality_jp6b, trouble_quality_jp7, trouble_quality_etc) 
    trouble_quality = sorted(all_trouble_quality, key=lambda x: x.発生日)

    context = {
        'title': '過去のトラブル<品質>',
        'trouble_quality': trouble_quality,
        'searchform': searchform,
    }
    return render(request, 'home/trouble_quality_all.html', context)

def trouble_safety_all(request):
    searchform = SearchForm(request.GET)
    if searchform.is_valid():
        keyword = searchform.cleaned_data['keyword']
        trouble_safety_etc = EtcTroubleSafety.objects.using("juten").filter(Q(発生日__contains=keyword)|Q(トラブル内容__contains=keyword)|Q(対策__contains=keyword))
        trouble_safety_jp1 = Jp1TroubleSafety.objects.using("juten").filter(Q(発生日__contains=keyword)|Q(トラブル内容__contains=keyword)|Q(対策__contains=keyword))
        trouble_safety_jp2 = Jp2TroubleSafety.objects.using("juten").filter(Q(発生日__contains=keyword)|Q(トラブル内容__contains=keyword)|Q(対策__contains=keyword))
        trouble_safety_jp3 = Jp3TroubleSafety.objects.using("juten").filter(Q(発生日__contains=keyword)|Q(トラブル内容__contains=keyword)|Q(対策__contains=keyword))
        trouble_safety_jp4 = Jp4TroubleSafety.objects.using("juten").filter(Q(発生日__contains=keyword)|Q(トラブル内容__contains=keyword)|Q(対策__contains=keyword))
        trouble_safety_jp6a = Jp6aTroubleSafety.objects.using("juten").filter(Q(発生日__contains=keyword)|Q(トラブル内容__contains=keyword)|Q(対策__contains=keyword))
        trouble_safety_jp6b = Jp6bTroubleSafety.objects.using("juten").filter(Q(発生日__contains=keyword)|Q(トラブル内容__contains=keyword)|Q(対策__contains=keyword))
        trouble_safety_jp7 = Jp7TroubleSafety.objects.using("juten").filter(Q(発生日__contains=keyword)|Q(トラブル内容__contains=keyword)|Q(対策__contains=keyword))
    else:
        searchform = SearchForm()
        trouble_safety_etc = EtcTroubleSafety.objects.using("juten").all()
        trouble_safety_jp1 = Jp1TroubleSafety.objects.using("juten").all()
        trouble_safety_jp2 = Jp2TroubleSafety.objects.using("juten").all()
        trouble_safety_jp3 = Jp3TroubleSafety.objects.using("juten").all()
        trouble_safety_jp4 = Jp4TroubleSafety.objects.using("juten").all()
        trouble_safety_jp6a = Jp6aTroubleSafety.objects.using("juten").all()
        trouble_safety_jp6b = Jp6bTroubleSafety.objects.using("juten").all()
        trouble_safety_jp7 = Jp7TroubleSafety.objects.using("juten").all()

    all_trouble_safety = trouble_safety_jp1.union(trouble_safety_jp2, trouble_safety_jp3, trouble_safety_jp4, trouble_safety_jp6a, trouble_safety_jp6b, trouble_safety_jp7, trouble_safety_etc) 
    trouble_safety = sorted(all_trouble_safety, key=lambda x: x.発生日)

    context = {
        'title': '過去のトラブル<安全>',
        'trouble_safety': trouble_safety,
        'searchform': searchform,
    }
    return render(request, 'home/trouble_safety_all.html', context)

def list_all(request):
    searchform = SearchForm(request.GET)
    if searchform.is_valid():
        keyword = searchform.cleaned_data['keyword']
        jp1s = Jp1.objects.using("juten").filter(Q(item_no__contains=keyword)|Q(item_name__contains=keyword))
        jp2s = Jp2.objects.using("juten").filter(Q(item_no__contains=keyword)|Q(item_name__contains=keyword))
        jp3s = Jp3.objects.using("juten").filter(Q(item_no__contains=keyword)|Q(item_name__contains=keyword))
        jp4s = Jp4.objects.using("juten").filter(Q(item_no__contains=keyword)|Q(item_name__contains=keyword))
        jp6as = Jp6a.objects.using("juten").filter(Q(item_no__contains=keyword)|Q(item_name__contains=keyword))
        jp6bs = Jp6b.objects.using("juten").filter(Q(item_no__contains=keyword)|Q(item_name__contains=keyword))
        jp7s = Jp7.objects.using("juten").filter(Q(item_no__contains=keyword)|Q(item_name__contains=keyword))
    else:
        searchform = SearchForm()
        jp1s = Jp1.objects.using("juten").all()
        jp2s = Jp2.objects.using("juten").all()
        jp3s = Jp3.objects.using("juten").all()
        jp4s = Jp4.objects.using("juten").all()
        jp6as = Jp6a.objects.using("juten").all()
        jp6bs = Jp6b.objects.using("juten").all()
        jp7s = Jp7.objects.using("juten").all()

    data = {
        'jp1s': jp1s,
        'jp2s': jp2s,
        'jp3s': jp3s,
        'jp4s': jp4s,
        'jp6as': jp6as,
        'jp6bs': jp6bs,
        'jp7s': jp7s,
    } 
    context = {
        'title': '製品一覧',
        'data': data,
        'searchform': searchform,
    }
    return render(request, 'home/list_all.html', context)


def detail_all(request, item_no):
    try:
        item = Jp1.objects.using("juten").get(item_no=item_no)
    except Jp1.DoesNotExist:
        item = None
        try:
            item = Jp2.objects.using("juten").get(item_no=item_no)
        except Jp2.DoesNotExist:
            item = None
            try:
                item = Jp3.objects.using("juten").get(item_no=item_no)
            except Jp3.DoesNotExist:
                item = None
                try:
                    item = Jp4.objects.using("juten").get(item_no=item_no)
                except Jp4.DoesNotExist:
                    item = None
                    try:
                        item = Jp6a.objects.using("juten").get(item_no=item_no)
                    except Jp6a.DoesNotExist:
                        item = None
                        try:
                            item = Jp6b.objects.using("juten").get(item_no=item_no)
                        except Jp6b.DoesNotExist:
                            item = None
                            try:
                                item = Jp7.objects.using("juten").get(item_no=item_no)
                            except Jp7.DoesNotExist:
                                item = None                   
    context = {
        'title': '製品詳細',
        'item': item,
    }
    return render(request, 'home/detail_all.html', context)

def pdf_list(request):
    pdf_files = PDFFile.objects.using("juten").all()
    return render(request, 'home/pdf_list.html', {'pdf_files': pdf_files})

def view_pdf(request, pdf_id):
    pdf_file = get_object_or_404(PDFFile.objects.using("juten"), pk=pdf_id)
    return render(request, 'home/view_pdf.html', {'pdf_file': pdf_file})

