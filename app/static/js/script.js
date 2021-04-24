$(document).ready(function () {

    function ani() {
        $(".popOut").className = "popOut ani";
    }

    $("#new-room").click(function () {
        $(".popOut").css("display", "block");
        ani();
        // $(".popOutBg").style.display = "block";
    });
    $("#close-pop").click(function () {
        $(".popOut").css("display", "none");
        // $(".popOutBg").style.display = "none";
    });
    $(".popOutBg").click(function () {
        $(".popOut").css("display", "none");
        // $(".popOutBg").style.display = "none";
    });

    var $btn_video = $('#btn-video');
    var video_on = 0;
    var local_stream;
    var $local_video = $('#local-video')[0];
    var remote_stream;
    var $remote_video = $('#remote-video')[0];

    $btn_video.on("click", function () {
        if (video_on === 0) {
            $(".video-screen").removeClass("d-none");
            $(".video-screen").addClass("d-block");
            getLocalVideo();
            video_on = 1;
        } else {
            $(".video-screen").removeClass("d-block");
            $(".video-screen").addClass("d-none");
            stopLocalVideo();
            video_on = 0;
        }

    })

    function getLocalVideo() {
        var constraints = {audio: true, video: {width: 247, height: 156}};

        navigator.mediaDevices.getUserMedia(constraints)
            .then(function (mediaStream) {
                local_stream = mediaStream;
                $local_video.srcObject = local_stream;
                $local_video.onloadedmetadata = function (e) {
                    $local_video.play();
                };
            })
            .catch(function (err) {
                console.log(err.name + ": " + err.message);
            }); // always check for errors at the end.
    }

    function stopLocalVideo() {
        if (local_stream.active) {
            local_stream.getTracks()[0].stop(); // stop video
            local_stream.getTracks()[1].stop(); // stop audio
        }

    }

})