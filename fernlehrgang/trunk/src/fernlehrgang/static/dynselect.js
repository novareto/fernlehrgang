$(document).ready(function() 
    {
        $("#form-widgets-lehrheft_id").change(function()
           {
               var value = $(this).val();
               $.getJSON('context_fragen', {'lehrheft_id': value}, function(d)
                  {
                      $('#form-widgets-frage_id').html(d.fragen);
                  });
            
           } );
    } 
); 
