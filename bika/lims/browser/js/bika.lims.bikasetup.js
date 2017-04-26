/**
 * Controller class for BikaSetup Edit view
 */
function BikaSetupEditView() {

    var that = this;

    var restrict_useraccess = $('#archetypes-fieldname-RestrictWorksheetUsersAccess #RestrictWorksheetUsersAccess');
    var restrict_wsmanagement = $('#archetypes-fieldname-RestrictWorksheetManagement #RestrictWorksheetManagement');

    var rounding_type = $('#archetypes-fieldname-DisplayRounding #DisplayRounding');
    var significant_figures = $('#archetypes-fieldname-SignificantFigures');
    /**
     * Entry-point method for BikaSetupEditView
     */
    that.load = function () {

        // LIMS-2371 Round using Decimal Precision or Significant Digits.
        $(rounding_type).change(function(){
            rounding_type_changed();
        });

        // Controller to avoid introducing no accepted prefix separator.
        $('input[id^="Prefixes-separator-"]').each(function() {
            toSelectionList(this);
        });
        // After modify the selection list, the hidden input should update its own value with the
        // selected value on the list
        $('select[id^="Prefixes-separator-"]').bind('select change', function () {
            var selection = $(this).val();
            var id = $(this).attr('id');
            $('input#'+id).val(selection)
        });

        $(restrict_useraccess).change(function () {

            if ($(this).is(':checked')) {

                // If checked, the checkbox for restrict the management
                // of worksheets must be checked too and readonly
                $(restrict_wsmanagement).prop('checked', true);
                $(restrict_wsmanagement).click(function(e) {
                    e.preventDefault();
                });

            } else {

                // The user must be able to 'un-restrict' the worksheet
                // management
                $(restrict_wsmanagement).unbind("click");

            }
        });

        if ($("select[name=NumberOfRequiredVerifications] option:selected").val() == 1) {
            document.getElementById('archetypes-fieldname-TypeOfmultiVerification').style.display='none';
        }
        $('#NumberOfRequiredVerifications').change(function () {
            if ($(this).val()>1) {
              document.getElementById('archetypes-fieldname-TypeOfmultiVerification').style.display='block';
            } else {
              document.getElementById('archetypes-fieldname-TypeOfmultiVerification').style.display='none';
            }
        });

        $(restrict_useraccess).change();
    };

    function toSelectionList(pointer) {
        /*
        The function generates a selection list to choose the prefix separator. Doing that, we can be
        sure that the user will only be able to select a correct separator.
         */
        var def_value = pointer.value;
        var current_id = pointer.id;
        // Allowed separators
        var allowed_elements = ['','-','_'];
        var selectbox = '<select id="'+current_id+'">'+'</select>';
        $(pointer).after(selectbox);
        $(pointer).hide();
        for(var i = 0; i < allowed_elements.length; i++) {
            var selected = 'selected';
            if (allowed_elements[i] != def_value) {selected = ''}
            var option =  "<option "+selected+" value="+allowed_elements[i]+">"+allowed_elements[i]+"</option>";
            $('select#'+current_id).append(option)
        }
    }

    function rounding_type_changed(){
        var value = $(rounding_type).val();
        if (value == "NONE") {
          $(significant_figures).hide();
        }
        else if (value == "DECIMAL_PRECISION"){
          $(significant_figures).hide();
        }
        else if (value == "SIGNIFICANT_FIGURES"){
          $(significant_figures).show();
        }
    }
    rounding_type_changed();
}
