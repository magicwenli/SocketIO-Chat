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
    var local_stream;
    var $local_video = $('#local-video')[0];
    var remote_stream;
    var $remote_video = $('#remote-video')[0];

    $btn_video.on("click", function () {
        $(".video-screen").removeClass("d-none");
        $(".video-screen").addClass("d-block");
        getLocalVideo();
    })

    function getLocalVideo() {
        var constraints = {audio: true, video: {width: 247, height: 156}};

        navigator.mediaDevices.getUserMedia(constraints)
            .then(function (mediaStream) {
                $local_video.srcObject = mediaStream;
                $local_video.onloadedmetadata = function (e) {
                    $local_video.play();
                };
            })
            .catch(function (err) {
                console.log(err.name + ": " + err.message);
            }); // always check for errors at the end.
    }

})