$(document).ready(function() 
    {
        var v1 = $("#form-widgets-lehrheft_id :selected").val();
        if (v1 == 'Bitte eine Auswahl treffen')
          {
            $('#form-widgets-frage_id').attr('disabled', true);
          }

        $("#form-widgets-lehrheft_id").change(function()
           {
               $('#form-widgets-frage_id').removeAttr('disabled');
               var value = $(this).val();
               $.getJSON(base_url+'/context_fragen', {'lehrheft_id': value}, function(d)
                  {
                      $('#form-widgets-frage_id').html(d.fragen);
                  });
            
           } );
    } 
); 
