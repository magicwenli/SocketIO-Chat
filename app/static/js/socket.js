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
        var room_name=$('#chat-title').text();
        var msg = {body:$textarea.val().trim(),room_name:room_name};
        if (e.which === ENTER_KEY && !e.shiftKey && msg) {
            e.preventDefault();
            socket.emit('new message', msg);
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

    socket.on('joined_room',function (data){
        $(".popOut").css("display", "none");
        $('#chat-title').text(data.room_name)
        $('.chat-content').html('')
        var msg_url='/chatroom/'+data.room_name
        $.ajax({
            type: 'GET',
            url: msg_url,
            success:function (message){
                $('.chat-content').html(message)
            },
            error: function (error){
                $('.chat-content').html('Can not get message from server')
            }
        });
    })

    function join_room(e) {
        var room_name = $('#room').val();
        socket.emit('join room',room_name);
    }

    $('#submit').on('click',join_room.bind(this));



    // socket.on('join room')
    // TODO    https://socket.io/docs/v3/rooms/  Join Room
});
