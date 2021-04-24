$(document).ready(function () {

    /* control room choose panel popup */
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

})