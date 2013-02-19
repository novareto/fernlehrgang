$(document).ready(function() { 

  $('div.subform table').addClass('table table-striped table-bordered table-condensed');
  $('div.subform form table select').attr('disabled', 'disabled');

  $('#field-form-field-nr').appendFieldTo('#field-form-field-strasse');
  $('#field-form-field-ort').appendFieldTo('#field-form-field-plz');

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

  $("select#select_lehrheft").change(function() {
      value = $(this).val();
      if (value == "Bitte Auswahl Treffen") {
          $('form table').hide();
      }
      else {
          $('form table').show();
          $(location).attr('href', base_url + '?lh_id=' + $(this).val());
          $(".G-select").attr('checked', 'checked');
      }
    }
    );
  
  lh_id = $("select#select_lehrheft").val();
  if (lh_id == "Bitte Auswahl Treffen") {
     $('form table').hide();
  }

  $(".G-select").attr('checked', 'checked');
}); 
