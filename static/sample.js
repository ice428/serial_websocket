// websocketオブジェクト
var ws = new WebSocket("ws://localhost:8080/ws");

//レスポンスのjsonでブラウザの要素を更新
var get_res = function(response){window.location.href = response;};

//post通信
var ajax_post = function(url, data, func){
    $.ajax({
        url: url,
        data: JSON.stringify(data),
        type: 'post',
        contentType: 'application/json',
        success: func,
        error: function(error) {console.log(error);}
    });
}

//get通信
var ajax_get = function(url, func){
    $.ajax({
        url: url,
        type: 'get',
        success: func,
        error: function(error) {console.log(error);}
    });
}

//option更新
var option_refresh = function(data){
}

//modalを閉じる
var modal_colse = function(){
$('.modal').removeClass("active");
};

//modalを開く
var modal_open = function(){
//$.get("/serial_port_list", function(data){
//    list = JSON.parse(data)
//    options = $.map(list.ports, function(port,i){
//        $option = $('<option>', { value: port, text: port});
//        return $option;
//});
//$("#port_list").html(options);
$('.modal').addClass("active");
//});
};

//ポートを開く
var port_open = function(){
data={
    type:"open",
    port:$('[name=port]').val(),
    baudrate: $('[name=baudrate]').val(),
    databit: $("input[name='databit']:checked").val(),
    stopbit: $("input[name='stopbit']:checked").val(),
    parity:$("input[name='parity']:checked").val()
};
console.log(JSON.stringify(data));
ws.send(JSON.stringify(data));
// modalを閉じる
$('.modal').removeClass("active");
};

//ポートを閉じる
var port_close = function(){
data={
    type:"close"
};
console.log(JSON.stringify(data));
ws.send(JSON.stringify(data));
$("#box_send").prop('disabled', true);
$("#message_send").prop('disabled', true);
$("#port_close").prop('disabled', true);
$("#log_start").prop('disabled', true);
$("#port_open").prop('disabled', false);
};

//メッセージ送信
var message_send = function(){
data={
    type:"send",
    message:$("input[name='message_send']").val()
};
//console.log(JSON.stringify(data))
ws.send(JSON.stringify(data));
$(log_area).append("<font color='#e87a00'>>>> " + $("input[name='message_send']").val() + "</font>\n");

//スクロール
$(log_area).scrollTop(
    $(log_area)[0].scrollHeight - $(log_area).height()
);
};

// websocketメッセージ受信時
var ws_on_message = function(evt){
data=JSON.parse(evt.data);
switch(data["type"]){
case "data":
    $(log_area).append(data["data"]);
    break;
case "status":
    switch(data["status"]){
    case "connected":
        $(log_area).append("<font color='#371eec'>" + data["status"] + "[" + data["condition"] + "]</font>\n");
        $("#box_send").prop('disabled', false);
        $("#message_send").prop('disabled', false);
        $("#port_close").prop('disabled', false);
        $("#log_start").prop('disabled', false);
        $("#port_open").prop('disabled', true);
        break;
    case "disconnected":
        $(log_area).append("<font color='#371eec'>" + data["status"] + "[" + data["device"] + "]</font>\n");
        break;
    }
    break;
case "error":
    $(log_area).append(data["error"] + "\n");
    break;
}
//スクロール
$(log_area).scrollTop(
    $(log_area)[0].scrollHeight - $(log_area).height()
);
}

//起動時スクリプト
window.onload = function(){
//UIセット
$('.modal_close').on('click', modal_colse);
$('.modal_open').on('click', modal_open);
$('#port_open').on('click', port_open);
$('#port_close').on('click', port_close);
$('#message_send').on('click', message_send);

$("#box_send").prop('disabled', true);
$("#message_send").prop('disabled', true);
$("#port_close").prop('disabled', true);
$("#log_start").prop('disabled', true);

log_area = $('.console')

ws.onmessage = ws_on_message
};