var socket;
$(document).ready(function () {

    socket = io();

    var ENTER_KEY = 13;
    var $textarea = $('#message-textarea');
    var $emitbtn = $('#emitbtn');


    function scrollToBottom() {
        var chat_content = $('.chat-content');
        chat_content.scrollTop(chat_content[0].scrollHeight);
    }

    function new_message(e) {
        var room_name = $('#chat-title').attr("aria-label");
        var msg = {body: $textarea.val().trim(), room_name: room_name};
        if ((e.which === ENTER_KEY && !e.shiftKey) || (e.which === 1) && msg) {
            e.preventDefault();
            socket.emit('new message', msg);
            $textarea.val('');
        }
    }

    scrollToBottom();

    $textarea.on('keydown', new_message.bind(this));
    $emitbtn.on('click', new_message.bind(this));


    socket.on('new message', function (data) {
        let room_name = $('#chat-title').attr("aria-label");
        if (data.room_name === room_name) {
            $('.chat-content').append(data.message_html);
            flask_moment_render_all();
            scrollToBottom()
        }

    });

    // get and set userinfo html at sidebar
    socket.on('users info', function (data) {
        $('#users-amount').text(data.amount);
        $('#users-list').html(data.users);
        $('#rooms-amount').text(data.rooms_amount);
        $('#rooms-list').html(data.rooms);

    });

    socket.on('joined_room', function (data) {
        $(".popOut").css("display", "none");

        enter_room(data.room_name);
    })

    function enter_room(room_name) {
        $('#chat-title').text(room_name);
        $('#chat-title').attr("aria-label", room_name)
        $('.chat-content').html('');
        var msg_url = '/chatroom/' + room_name;

        $.ajax({
            type: 'GET',
            url: msg_url,
            success: function (message) {
                $('.chat-content').html(message)
            },
            error: function (error) {
                $('.chat-content').html('Can not get message from server')
            }
        });
        scrollToBottom();
    }

    function join_room(e) {
        var room_name = $('#room').val();
        socket.emit('join room', room_name);
    }

    $('#submit').on('click', join_room.bind(this));


    // socket.on('join room')
    // TODO    https://socket.io/docs/v3/rooms/  Join Room
    // TODO    webrtc https://github.com/pfertyk/webrtc-working-example/blob/72cf0bc456/web/main.js
});
