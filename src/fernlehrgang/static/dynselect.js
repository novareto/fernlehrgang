$(document).ready(function() 
    {
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
            
           } );
    } 
); 
