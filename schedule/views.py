from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Value, CharField
from django.http import JsonResponse, HttpResponse
from .models import Schedule
from jp1.models import Jp1
from jp2.models import Jp2 
from jp3.models import Jp3 
from jp4.models import Jp4 
from jp6a.models import Jp6a 
from jp6b.models import Jp6b 
from jp7.models import Jp7 
import json
import logging

def schedule(request, specified_date):
    try:
        split_num = [specified_date[x:x+2] for x in range(0, len(specified_date), 2)]
        specified_date2 = "/".join(split_num)
        specified_date3 = specified_date
        # 指定された日付のデータを取得し、縦の値でソート
        products = Schedule.objects.using('production_schedule').filter(生産日=specified_date2).order_by('縦')

        # データ整形
        schedule_data = {'columns': []}
        for product in products:
            row = str(product.縦)
            col = str(product.横)
            if row == "0" and col == "0":
                continue  # 座標が0,0の場合はスキップ

            # 横の値が10以上の場合は-10してから使用
            col = str(int(col) - 10) if int(col) >= 10 else col
           
            if row not in schedule_data:
                schedule_data[row] = {}
            schedule_data[row][col] = {
                "product_name": product.製品名,
                "color": product.色,
                "product_number": product.品番,
                "specified_date3": product.生産日,
            }

            # カラム情報を追加
            if col not in schedule_data['columns']:
                schedule_data['columns'].append(col)

        # カラム情報をソート
        schedule_data['columns'].sort(key=int)

        # JSON形式に変換してJavaScriptに渡す
        schedule_data_json = json.dumps(schedule_data)
        
        # JSON形式に変換したデータにspecified_date3を追加する
        schedule_data_json_with_specified_date3 = add_specified_date3_to_json(schedule_data_json)

        # テンプレートにデータを渡す
        return render(request, 'schedule/schedule.html', {'specified_date2': specified_date2, 'specified_date3': specified_date3, 'schedule_data': schedule_data, 'schedule_data_json': schedule_data_json_with_specified_date3})
    except ValueError:
        # 日付の解析に失敗した場合はエラーをハンドリング
        return render(request, 'error.html', {'error_message': 'Invalid date format'})
    
def product_detail(request, product_number, specified_date3):
    # 品番に基づいて製品を取得
    split_num = [specified_date3[x:x+2] for x in range(0, len(specified_date3), 2)]
    specified_date3 = "/".join(split_num)
    
    product_schedule = get_object_or_404(Schedule.objects.using('production_schedule'), 生産日=str(specified_date3), 品番=product_number)
    try:
        product_jp1 = Jp1.objects.using("juten").get(item_no=product_number)
    except:
        product_jp1 = None
    try:
        product_jp2 = Jp2.objects.using("juten").get(item_no=product_number)
    except:
        product_jp2 = None
    try:
        product_jp3 = Jp3.objects.using("juten").get(item_no=product_number)
    except:
        product_jp3 = None
    try:
        product_jp4 = Jp4.objects.using("juten").get(item_no=product_number)
    except:
        product_jp4 = None
    try:
        product_jp6a = Jp6a.objects.using("juten").get(item_no=product_number)
    except:
        product_jp6a = None
    try:
        product_jp6b = Jp6b.objects.using("juten").get(item_no=product_number)
    except:
        product_jp6b = None
    try:
        product_jp7 = Jp7.objects.using("juten").get(item_no=product_number)
    except:
        product_jp7 = None
    
    # テンプレートにデータを渡す
    return render(request, 'schedule/product_detail.html', {
        'product_schedule': product_schedule,
        'product_jp1': product_jp1,
        'product_jp2': product_jp2,
        'product_jp3': product_jp3,
        'product_jp4': product_jp4,
        'product_jp6a': product_jp6a,
        'product_jp6b': product_jp6b,
        'product_jp7': product_jp7,
        })
    
def add_specified_date3_to_json(schedule_data_json):
    # JSON形式の文字列をPythonの辞書に変換
    schedule_data = json.loads(schedule_data_json)
    
    # 各セルのデータにspecified_date3を追加
    for row_key, row_data in schedule_data.items():
        for col_index, cell_data in enumerate(row_data):
            if isinstance(cell_data, dict):  # セルデータが辞書かどうかを確認
                cell_data['specified_date3'] = cell_data.get("specified_date3", "")  # ここに適切な値を設定する

    # 変更を加えた辞書をJSON形式に変換して返す
    return json.dumps(schedule_data)

def get_schedule_data(request):
    # リクエストから日付を取得
    date = request.GET.get('date')

    # 日付が指定されていなければエラーを返します
    if not date:
        return JsonResponse({'error': 'Date parameter is required'}, status=400)

    # 指定された日付でデータを取得
    split_num = [date[x:x+2] for x in range(0, len(date), 2)]
    date2 = "/".join(split_num)
    products = Schedule.objects.using('production_schedule').filter(生産日=date2).order_by('縦')

    # データを整形して辞書に格納
    schedule_data = {'columns': []}
    for product in products:
        row = str(product.縦)
        col = str(product.横)
        
        if row == "0" and col == "0":
            continue  # 座標が0,0の場合はスキップ
        
        col = str(int(col) - 10) if int(col) >= 10 else col
        
        if row not in schedule_data:
            schedule_data[row] = {}
        schedule_data[row][col] = {
            "product_name": product.製品名,
            "color": product.色,
            "product_number": product.品番,
            "specified_date3": product.生産日,
        }

        # カラム情報を追加
        if col not in schedule_data['columns']:
            schedule_data['columns'].append(col)

    # カラム情報をソート
    schedule_data['columns'].sort(key=int)
    #sorted_data = sorted(schedule_data.item(), key=lambda x: (int(x[0]),int(min(x[1].keys()))))
    # 整形したデータをJSON形式で返す
    return JsonResponse(schedule_data)

def redirect_to_detail(request, item_no):
    try:
        if Jp1.objects.using("juten").filter(item_no=item_no).exists():
            return redirect('jp1:detail_jp1', item_no=item_no)
        elif Jp2.objects.using("juten").filter(item_no=item_no).exists():
            return redirect('jp2:detail_jp2', item_no=item_no)
        elif Jp3.objects.using("juten").filter(item_no=item_no).exists():
            return redirect('jp3:detail_jp3', item_no=item_no)
        elif Jp4.objects.using("juten").filter(item_no=item_no).exists():
            return redirect('jp4:detail_jp4', item_no=item_no)
        elif Jp6a.objects.using("juten").filter(item_no=item_no).exists():
            return redirect('jp6a:detail_jp6a', item_no=item_no)
        elif Jp6b.objects.using("juten").filter(item_no=item_no).exists():
            return redirect('jp6b:detail_jp6b', item_no=item_no)
        elif Jp7.objects.using("juten").filter(item_no=item_no).exists():
            return redirect('jp7:detail_jp7', item_no=item_no)
        else:
            return redirect('schedule:item_not_found')
    except Exception as e:
        print(f"Error: {e}")
        return HttpResponse("該当する製品がDBに登録されていない可能性があります。", status=404)