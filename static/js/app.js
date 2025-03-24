// CSRF対策
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN"
axios.defaults.xsrfCookieName = "csrftoken"

document.addEventListener('DOMContentLoaded', function () {
    // サーバーから色マッピングを取得
    axios.get('/mr/color_mapping/')
        .then(response => {
            const colorMapping = response.data; // サーバーから取得した色マッピング
            initializeCalendar(colorMapping);  // カレンダーを初期化
        })
        .catch(error => {
            console.error("色のマッピング取得エラー", error);
        });
});

function initializeCalendar(colorMapping) {
    const modal = document.getElementById("eventModal");
    const closeModalButton = document.getElementById("closeModal");
    const editEventNameInput = document.getElementById("editEventName");
    const editPersonInput = document.getElementById("editPerson");
    const editRoomNameSelect = document.getElementById("editRoomName");
    const editStartDateInput = document.getElementById("editStartDate");
    const editEndDateInput = document.getElementById("editEndDate");
    const saveEditButton = document.getElementById("saveEditButton");
    const deleteEventButton = document.getElementById("deleteEventButton");
    const cancelButton = document.getElementById("cancelButton");

    let currentEvent;

    closeModalButton.onclick = function() {
        modal.style.display = "none";
    };

    saveEditButton.onclick = function() {
        const updatedEventName = editEventNameInput.value.trim();
        const updatedPerson = editPersonInput.value.trim();
        const updatedRoomName = editRoomNameSelect.value;

        // 色マッピングから会議室の色を取得
        const updatedEventColor = colorMapping[updatedRoomName] || "#990000";

        // 開始日時と終了日時を取得
        const updatedStartDate = new Date(editStartDateInput.value);
        const updatedEndDate = new Date(editEndDateInput.value);

        axios.post("/mr/update/", {
            event_id: currentEvent.id,
            event_name: updatedEventName,
            person: updatedPerson,
            room_name: updatedRoomName,
            start_date: updatedStartDate.getTime(),  // サーバーに送信するためミリ秒単位で送る
            end_date: updatedEndDate.getTime(),
        })
        .then(() => {
            // イベントのタイトル、色、開始日時、終了日時を更新
            //currentEvent.setProp('title', ${updatedEventName}-${updatedPerson}(${updatedRoomName}));
            currentEvent.setProp('title', `${updatedEventName}-${updatedPerson}(${updatedRoomName})`);
            currentEvent.setProp('backgroundColor', updatedEventColor);
            currentEvent.setProp('borderColor', updatedEventColor);

            // イベントの開始日時と終了日時を更新
            currentEvent.setDates(updatedStartDate, updatedEndDate);
            modal.style.display = "none";
        })
        .catch(() => {
            alert("更新に失敗しました。もう一度お試しください。");
        });
    };

    deleteEventButton.onclick = function() {
        axios.post("/mr/delete/", {
            event_id: currentEvent.id,
        })
        .then(() => {
            currentEvent.remove();
            modal.style.display = "none";
        })
        .catch(() => {
            alert("削除に失敗しました。もう一度お試しください。");
        });
    };

    cancelButton.onclick = function() {
        modal.style.display = "none";
    };

    const calendarEl = document.getElementById('calendar');
    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'timeGridWeek',
        nowIndicator: true,
        locale: 'ja',
        contentHeight: "auto",
        allDaySlot: false,
        slotDuration: '00:30:00',
        slotLabelInterval: '01:00',
        businessHours: {
            daysOfWeek: [1, 2, 3, 4, 5],
            startTime: '08:30',
            endTime: '17:00'
        },
        views: {
            timeGridWeek: {
                slotMinTime: '07:00:00',
                slotMaxTime: '19:00:00'
            }
        },
        buttonText: {
            today: '今週'
        },
        selectable: true,
        select: function (info) {
            const eventStart = info.start;
            const eventEnd = info.end;
            const eventName = prompt("会議名を入力してください");
            const person = prompt("担当者を入力してください");
            let roomName = prompt("会議室名を選択してください (会議室1→1, 会議室2→2, 会議室3→3, 応接室→応接室, 社用車→車)", "");
            if (eventName) {
                if (roomName === "1") {
                    roomName = "会議室1";
                } else if (roomName === "2") {
                    roomName = "会議室2";
                } else if (roomName === "3") {
                    roomName = "会議室3";
                } else if (roomName === "車") {
                    roomName = "社用車";
                }
                const eventColor = colorMapping[roomName] || "#990000";
                axios.post("/mr/add/", {
                    start_date: eventStart.valueOf(),
                    end_date: eventEnd.valueOf(),
                    event_name: eventName,
                    person: person,
                    room_name: roomName,
                })
                .then((response) => {
                    const newEventId = response.data.id;
                    if (!newEventId) {
                        alert("イベントの登録に成功しましたが、IDの取得に失敗しました。");
                        return;
                    }
                    calendar.addEvent({
                        id: newEventId,
                        title: eventName + (person ? "-" + person : "") + (roomName ? "(" + roomName + ")" : ""),
                        start: eventStart,
                        end: eventEnd,
                        color: eventColor,
                        allDay: false,
                    });
                })
                .catch((error) => {
                    alert("登録に失敗しました");
                    console.error(error);
                });
            }
        },
        events: function (info, successCallback, failureCallback) {
            axios.post("/mr/list/", {
                start_date: info.start.valueOf(),
                end_date: info.end.valueOf(),
            })
            .then((response) => {
                successCallback(response.data);
            })
            .catch(() => {
                alert("表示に失敗");
            });
        },
        eventClick: function (info) {
            currentEvent = info.event;
            const titleParts = currentEvent.title.split("-");
            const eventName = titleParts[0];
            const personAndRoom = titleParts[1];
            const person = personAndRoom.slice(0, personAndRoom.lastIndexOf("("));
            const roomName = personAndRoom.slice(personAndRoom.lastIndexOf("(") + 1, personAndRoom.lastIndexOf(")"));

            editEventNameInput.value = eventName;
            editPersonInput.value = person;
            editRoomNameSelect.value = roomName;

            // 日時をISO文字列に変換し、input要素のvalueに設定
            const formatDateTimeLocal = (date) => {
                const tzOffset = date.getTimezoneOffset() * 60000; // ミリ秒単位のオフセット
                const localISOTime = (new Date(date - tzOffset)).toISOString().slice(0, 16);
                return localISOTime;
            };

            // 開始日時と終了日時を設定
            const startDate = formatDateTimeLocal(new Date(currentEvent.start));
            const endDate = formatDateTimeLocal(new Date(currentEvent.end));

            editStartDateInput.value = startDate;
            editEndDateInput.value = endDate;

            modal.style.display = "block";
        },
    });
    calendar.render();
}