var socket;
$(document).ready(function () {

    socket = io();

    var ENTER_KEY = 13;

    function scrollToBottom() {
        var chat_content = $('.chat-content');
        chat_content.scrollTop(chat_content[0].scrollHeight);
    }

    function new_message(e) {
        var $textarea = $('#message-textarea');
        var message_body = $textarea.val().trim();
        if (e.which === ENTER_KEY && !e.shiftKey && message_body) {
            e.preventDefault();
            socket.emit('new message', message_body);
            $textarea.val('');
        }
    }
    scrollToBottom();

    $('#message-textarea').on('keydown', new_message.bind(this));

    socket.on('new message', function (data) {
        $('.chat-content').append(data.message_html);
        flask_moment_render_all();
        scrollToBottom()
    });

    socket.on('users info',function (data){
        $('#online-user').text(data.count);
        $('#user-list').html(data.users);
    });

    // socket.on('join room')
    // TODO    https://socket.io/docs/v3/rooms/  Join Room
});
