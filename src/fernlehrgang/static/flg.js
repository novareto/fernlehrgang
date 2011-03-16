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


$(document).ready(function() 
  { 

  $('#form-form-field-nr').appendFieldTo('#form-form-field-strasse');
  $('#form-form-field-ort').appendFieldTo('#form-form-field-plz');

  $(".myTable").tablesorter( {widgets: ['zebra'], }); 
  $("#accordion").tabs("#accordion div.pane", {tabs: 'h2', effect: 'slide', initialIndex: null});

  var v1 = $("#form-field-lehrheft_id :selected").val();
  if (v1 == 'Bitte eine Auswahl treffen')
      {
        $('#form-field-frage_id').attr('disabled', true);
      }
  $("#form-field-lehrheft_id").change(function()
     {
         $('#form-field-frage_id').removeAttr('disabled');
         var value = $(this).val();
         $.getJSON(base_url+'/context_fragen', {'lehrheft_id': value}, function(d)
            {
                $('#form-field-frage_id').html(d.fragen);
            });
      
  });

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
} 
); 
