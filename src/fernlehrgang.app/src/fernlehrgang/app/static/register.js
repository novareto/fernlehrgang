$(document).ready(function() { 
    var fernlehrgang_id = $("#form-field-fernlehrgang_id :selected").val();
    if (fernlehrgang_id === '') {
        $('#field-form-field-status, #field-form-field-un_klasse, #field-form-field-branche, #field-form-field-gespraech').hide()
        $(':submit').hide();
    }
    $('#form-field-fernlehrgang_id').change(function() {
        lg_id = $(this).val();
        inew = lg_id.indexOf(",");
        if (inew === -1) {
            $('input#form-action-registrieren').show();
            $('input#form-action-reg-change').hide();
            $('#field-form-field-status, #field-form-field-un_klasse, #field-form-field-branche, #field-form-field-gespraech').show();
            $('#form-field-status > option[value="A1"]').attr('selected', 'selected');
            $('#form-field-un_klasse > option[value="G3"]').attr('selected', 'selected');
            $('#form-field-gespraech > option[value="0"]').attr('selected', 'selected');
            $('#form-field-branche > option[value="nein"]').attr('selected', 'selected');
        }

        else if (inew > 0) {
            $('input#form-action-reg-change').show();
            $('input#form-action-registrieren').hide();
            base_url = $('head base').attr('href');
            $.getJSON(base_url+'/get_kursteilnehmer', {'ktn_id': lg_id}, function(d) {
                $('#field-form-field-status, #field-form-field-un_klasse, #field-form-field-branche, #field-form-field-gespraech').show()
                $('#form-field-status > option[value=' + d.status + ']').attr('selected','selected')
                $('#form-field-un_klasse> option[value=' + d.un_klasse + ']').attr('selected','selected')
                $('#form-field-branche > option[value=' + d.branche + ']').attr('selected','selected')
                $('#form-field-gespraech > option[value=' + d.gespraech + ']').attr('selected','selected')
            })};
        if (!lg_id) {
            $('#field-form-field-status, #field-form-field-un_klasse, #field-form-field-branche, #field-form-field-gespraech').hide()
            $(':submit').hide();
        }
    })

})
