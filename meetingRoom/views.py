import json
from .models import Event
from .forms import EventForm
from .forms import CalendarForm
from django.http import Http404,HttpResponse,JsonResponse
from django.template import loader
from django.middleware.csrf import get_token
from datetime import datetime, timezone, timedelta

def get_room_color_mapping():
    return {
        "会議室1": "#5a993d",
        "会議室2": "#3d6b99",
        "会議室3": "#993d7a",
        "応接室": "#995c3d",
        "社用車": "#9932cc",
    }

def determine_event_color(room_name):
    color_mapping = get_room_color_mapping()
    return color_mapping.get(room_name, "#990000")  # 見つからない場合はデフォルトの色を使用

def get_color_mapping(request):
    return JsonResponse(get_room_color_mapping())

def index(request):
    #カレンダー画面

    get_token(request)

    template = loader.get_template("meetingRoom/index.html")
    return HttpResponse(template.render())

def add_event(request):
    #イベント登録

    if request.method == "GET":
        raise Http404()

    try:
        # JSONの解析
        datas = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': '無効なJSONデータ'}, status=400)
    # バリデーション
    eventForm = EventForm(datas)
    if not eventForm.is_valid():
        # バリデーションエラー
        return JsonResponse({'error': 'バリデーションエラー'}, status=400)

    # リクエストの取得
    start_date = datas["start_date"]
    end_date = datas["end_date"]
    event_name = datas["event_name"]
    person = datas["person"]
    room_name = datas["room_name"]

    if not all([start_date, end_date, event_name, person, room_name]):
        return JsonResponse({'error': '必要なフィールドが不足しています'}, status=400)

    # タイムゾーン設定及びミリ秒からdatetime形に変換
    tokyo_tz = timezone(timedelta(hours=9))
    formatted_start_date = datetime.fromtimestamp(start_date/1000,tz=tokyo_tz)
    formatted_end_date   = datetime.fromtimestamp(end_date/1000,tz=tokyo_tz)

    # 登録処理
    event = Event(
        event_name=str(event_name),
        person=str(person),
        room_name=str(room_name),
        start_date=formatted_start_date,
        end_date=formatted_end_date,
    )
    event.save(using='meetingroom')

    event_data = {
        'id': event.id,
        'title': f"{event.event_name}-{event.person}({event.room_name})",
        'start': int(event.start_date.timestamp()) * 1000,
        'end': int(event.end_date.timestamp()) * 1000,
        'color': determine_event_color(event.room_name),
    }
    return JsonResponse(event_data)

def get_events(request):
    #イベントの取得

    if request.method == "GET":
        raise Http404()

    # JSONの解析
    datas = json.loads(request.body)

    # バリデーション
    calendarForm = CalendarForm(datas)
    if calendarForm.is_valid() == False:
        raise Http404()

    # リクエストの取得
    start_date = datas["start_date"]
    end_date = datas["end_date"]

    # タイムゾーン設定及びミリ秒からdatetime形に変換
    tokyo_tz = timezone(timedelta(hours=9))
    formatted_start_date = datetime.fromtimestamp(start_date/1000,tz=tokyo_tz)
    formatted_end_date   = datetime.fromtimestamp(end_date/1000,tz=tokyo_tz)

    # FullCalendarの表示範囲のみ表示
    events = Event.objects.using('meetingroom').filter(
        start_date__lt=formatted_end_date, end_date__gt=formatted_start_date
    )
    # fullcalendarのため配列で返却
    list = []
    for event in events:
        start = int(event.start_date.timestamp())*1000
        end = int(event.end_date.timestamp())*1000
        event_color = determine_event_color(event.room_name)

        list.append(
            {
                "id":event.id,
                "title": event.event_name + "-" + event.person + "(" + event.room_name + ")",
                "start": start,
                "end": end,
                "color": event_color,
            }
        )
    return JsonResponse(list, safe=False)

def delete_events(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # リクエストボディをJSONとして解析
            print(data)
            event_id = data.get('event_id')
            event = Event.objects.using('meetingroom').get(id=event_id)
            event.delete(using='meetingroom')  # データベースからイベントを削除

            # 削除成功のレスポンスを返す
            return JsonResponse({'message': 'イベントを削除しました'})
        except Event.DoesNotExist:
            # データベースにイベントが見つからない場合
            return JsonResponse({'error': 'イベントが見つかりませんでした'}, status=404)
        except Exception as e:
            # その他の例外処理（例：データベースエラー）
            return JsonResponse({'error': str(e)}, status=400)
    else:
        # 無効なリクエストメソッドのエラーレスポンスを返す
        return JsonResponse({'error': '無効なリクエストメソッドです'}, status=405)

def update_event(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        event_id = data.get('event_id')
        try:
            event = Event.objects.using('meetingroom').get(id=event_id)

            event.event_name = data.get('event_name', event.event_name)
            event.person = data.get('person', event.person)
            event.room_name = data.get('room_name', event.room_name)
            start_date = data.get("start_date")
            end_date = data.get("end_date")
            if start_date is not None:
                tokyo_tz = timezone(timedelta(hours=9))
                event.start_date = datetime.fromtimestamp(start_date / 1000, tz=tokyo_tz)
            if end_date is not None:
                tokyo_tz = timezone(timedelta(hours=9))
                event.end_date = datetime.fromtimestamp(end_date / 1000, tz=tokyo_tz)

            event.save()

            return JsonResponse({'message': 'イベントを更新しました'})
        except Event.DoesNotExist:
            return JsonResponse({'error': 'イベントが見つかりませんでした'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': '無効なリクエストメソッドです'}, status=405)