"use strict"

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


    // join room from popup panel
    function join_room(e) {
        var room_name = $('#room').val();
        socket.emit('join room', room_name);
    }

    $('#submit').on('click', join_room.bind(this));


    // socket.on('join room')
    // TODO    https://socket.io/docs/v3/rooms/  Join Room
    // TODO    webrtc https://github.com/pfertyk/webrtc-working-example/blob/72cf0bc456/web/main.js

    /* control webRTC */
    // I got HUGE help from https://pfertyk.me/2020/03/webrtc-a-working-example/

    const TURN_SERVER_URL = 'stun.miwifi.com:3478';
    const TURN_SERVER_USERNAME = 'test';
    const TURN_SERVER_CREDENTIAL = 'test';

    const PC_CONFIG = {
        iceServers: [
            {
                url: 'stun:' + TURN_SERVER_URL
                //username: TURN_SERVER_USERNAME,
                //credential: TURN_SERVER_CREDENTIAL
            }
        ]
    };

    var $btn_video = $('#btn-video');
    var video_on = 0; // show if video is on
    var local_stream;
    var $local_video = $('#local-video')[0];
    var remote_stream;
    var $remote_video = $('#remote-video')[0];
    var pc; // peer_connection
    var state = 'init';

    socket.on('webrtc data', (data) => {
        console.log('webrtc data. data received: ', data);
        handleSignalingData(data);
    });

    socket.on('webrtc joined', (data) => {
        console.log('webrtc joined. data received: ', data);
        createPeerConnection();
    });

    socket.on('webrtc ready', () => {
        console.log('webrtc ready');
        // Connection with signaling server is ready, and so is local stream
        createPeerConnection();
        sendOffer();
    });

    socket.on('full', () => {
        closePeerConnection();
        stopLocalVideo();

        alert('This video chat had started, exiting.')

        // TODO stop streaming && hide video
    })

    let sendData = (data) => {
        socket.emit('webrtc data', {
            "data": data,
            "room_name": $('#chat-title').attr("aria-label")
        });
    };


    $btn_video.on("click", function () {
        if (video_on === 0) {   // start a video sharing
            $(".video-screen").removeClass("d-none");
            $(".video-screen").addClass("d-block");
            video_on = 1;
            getLocalVideo();
        } else {                // close a video sharing
            $(".video-screen").removeClass("d-block");
            $(".video-screen").addClass("d-none");
            video_on = 0;
            closePeerConnection();
            stopLocalVideo();
        }

    })

    function getLocalVideo() {
        var constraints = {
            audio: true, video: {
                width: {min: 320, max: 480},
                height: {min: 240, max: 360},
                require: ["width", "height"]
            }
        };

        navigator.mediaDevices.getUserMedia(constraints)
            .then(function (mediaStream) {
                local_stream = mediaStream;
                $local_video.srcObject = local_stream;
                $local_video.onloadedmetadata = function (e) {
                    $local_video.play();
                };
                socket.emit("webrtc connect", {
                    "room_name": $('#chat-title').attr("aria-label")
                });
                console.log("webrtc connect..");
            })
            .catch(function (err) {
                console.log(err.name + ": " + err.message);
            }); // always check for errors at the end.
    }

    function stopLocalVideo() {
        console.log("stop local video");
        if (local_stream.active) {
            local_stream.getTracks()[0].stop(); // stop video
            local_stream.getTracks()[1].stop(); // stop audio
        }
    }

    /* onicecandidate (called when the remote side sends us an ICE candidate),
       and onaddstream (called after the remote side adds its local media
       stream to its peer connection).
    */

    var createPeerConnection = () => {
        try {
            pc = new RTCPeerConnection(PC_CONFIG);
            pc.onicecandidate = onIceCandidate;
            pc.onaddstream = onAddStream;
            pc.addStream(local_stream);
            console.log('PeerConnection created');
        } catch (error) {
            console.error('PeerConnection failed: ', error);
        }
    };

    function closePeerConnection() {
        console.log('PeerConnection closed');
        if (pc) {
            pc.close();
            pc = null;
        }
    }

    let sendOffer = () => {
        console.log('Send offer');
        pc.createOffer().then(
            setAndSendLocalDescription,
            (error) => {
                console.error('Send offer failed: ', error);
            }
        );
    };

    let sendAnswer = () => {
        console.log('Send answer');
        pc.createAnswer().then(
            setAndSendLocalDescription,
            (error) => {
                console.error('Send answer failed: ', error);
            }
        );
    };

    let setAndSendLocalDescription = (sessionDescription) => {
        pc.setLocalDescription(sessionDescription);
        console.log('Local description set');
        sendData(sessionDescription);
    };

    let onIceCandidate = (event) => {
        if (event.candidate) {
            console.log('ICE candidate');
            sendData({
                type: 'candidate',
                candidate: event.candidate
            });
        }
    };

    let onAddStream = (event) => {
        console.log('Add stream');
        $remote_video.srcObject = event.stream;
    };

    let handleSignalingData = (data) => {
        switch (data.type) {
            case 'offer':
                createPeerConnection();
                pc.setRemoteDescription(new RTCSessionDescription(data));
                sendAnswer();
                break;
            case 'answer':
                pc.setRemoteDescription(new RTCSessionDescription(data));
                break;
            case 'candidate':
                pc.addIceCandidate(new RTCIceCandidate(data.candidate));
                break;
        }
    };


});
