/*
$.tools.dateinput.localize("de", {
   months: 'Januar,Februar,März,April,Mai,Juni,Juli,August,September,Oktober,November,Dezember',
   shortMonths:  'Jan,Feb,Mar,Apr,May,Jun,Jul,Aug,Sep,Okt,Nov,Dez',
   days:         'Sonntag,Montag,Dienstag,Mittwoch,Donnerstag,Freitag,Samstag',
   shortDays:    'So,Mo,Di,Mi,Do,Fr,Sa'
});

$.tools.dateinput.conf.lang = 'de';
*/

$(document).ready(function() { 

  $('div.subform table').addClass('table table-striped table-bordered table-condensed');
  $('div.subform form table select').attr('disabled', 'disabled');


  $.each($('input.field-date'), function() {
     $(this).dateinput({ 
         format: 'dd.mm.yyyy', 
         selectors: true, 
         yearRange: [-95, 15],
         'firstDay': 1 });
  })


  $('#form-form-field-nr').appendFieldTo('#form-form-field-strasse');
  $('#form-form-field-ort').appendFieldTo('#form-form-field-plz');

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
}); 
