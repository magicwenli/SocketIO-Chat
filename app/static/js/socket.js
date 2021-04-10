// var socket;
// $(document).ready(function () {
//
//     socket = io.connect('http://' + document.domain + ':' + location.port);
//
//     socket.on('connect',function (){
//         socket.emit('hello',{})
//     });
//     socket.on('hi',function (data){
//         console.log(data.msg);
//     });
//     //
//     // const ENTER_KEY = 13;
//     //
//     // function scrollToBottom() {
//     //     var chat_content = $('.chat-content');
//     //     chat_content.scrollTop(chat_content[0].scrollHeight);
//     // }
//     //
//     // function new_message(e) {
//     //     var $textarea = $('#message-textarea');
//     //     var message_body = $textarea.val().trim();
//     //     if (e.which === ENTER_KEY && ! e.shiftKey && message_body) {
//     //         e.preventDefault();
//     //         socket.emit('new message', message_body);
//     //         $textarea.val('');
//     //     }
//     // }
//     //
//     // $('#message-textarea').on('keydown', new_message.bind(this));
//     //
//     // socket.on('new message', function (data) {
//     //     $('.chat-content').append(data.message_html);
//     //     flask_moment_render_all();
//     //     scrollToBottom()
//     // });
// });


$(document).ready(function () {
    socket = io.connect('http://' + document.domain + ':' + location.port);
    socket.on('connect', function () {
        socket.emit('joined', {});
    });
    socket.on('status', function (data) {
        $('.chat-content').append(data+'-----\n');
        $('.chat-content').scrollTop($('.chat-content')[0].scrollHeight);
    });
    socket.on('message', function (data) {
        $('.chat-content').append(data+'\n');
        $('.chat-content').scrollTop($('.chat-content')[0].scrollHeight);
    });
    $('#message-textarea').keypress(function (e) {
        var code = e.keyCode || e.which;
        if (code == 13) {
            text = $('#message-textarea').val();
            $('#message-textarea').val('');
            socket.emit('text', {msg: text});
        }
    });
});
// TODO 记录在线人数和在线群组数
// https://stackoverflow.com/questions/32134623/socket-io-determine-if-a-user-is-online-or-offline
function leave_room() {
    socket.emit('left', {}, function () {
        socket.disconnect();

        // go back to the login page
        window.location.href = Flask.url_for("chat.home");
    });
}