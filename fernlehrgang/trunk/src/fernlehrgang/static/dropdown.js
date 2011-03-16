var timeout    = 0;
var closetimer = 0;
var opendd     = null;

function dd_close() {
 opendd.css('display', 'none');
}

function dd_timer() {
 closetimer = window.setTimeout(dd_close, timeout);
}

function dd_canceltimer() {
 if(closetimer) {
 window.clearTimeout(closetimer);
 closetimer = null;
 }
}


$(document).ready(function(){
  $("dl.dropdown").hover(
    function() {
       dd_canceltimer();
       if (opendd != null) { dd_close(); }
          opendd = $("dd", this).css('display', 'block');
    },
    function() {
        dd_timer();
    }
  );
    $(".foldable").hover(
        function() {
           $("dd", this).slideDown('fast');
           $(this).addClass("unfolding");
        }, 
        function() {
           $("dd", this).slideUp('fast');
           $(this).removeClass("unfolding");
        } 
    );
});
