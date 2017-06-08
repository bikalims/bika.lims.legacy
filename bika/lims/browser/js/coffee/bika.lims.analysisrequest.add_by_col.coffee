### Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../ -c bika.lims.analysisrequest.add_by_col.coffee
###

### Controller class for AnalysisRequestAddView - column layout.
#
# The form elements are not submitted.  Instead, their values are inserted
# into bika.lims.ar_add.state, and this variable is submitted as a json
# string.
#
#
# Regarding checkboxes: JQuery recommends using .prop() instead of .attr(),
# but selenium/xpath cannot discover the state of such inputs.  I use
# .attr("checked",true) and .removeAttr("checked") to set their values,
# although .prop("checked") is still the correct way to check state of
# a particular element from JS.
###

window.AnalysisRequestAddByCol = ->
  # Form management, and utility functions //////////////////////////////////

  ### form_init - load time form config
  # state_set - should be used when setting fields in the state var
  # filter_combogrid - filter an existing dropdown (referencewidget)
  # filter_by_client - Grab the client UID and filter all applicable dropdowns
  # get_arnum(element) - convenience to compensate for different form layouts.
  ###


  form_init = ->
    ### load-time form configuration
    #
    # - Create empty state var
    # - fix generated elements
    # - clear existing values (on page reload)
    # - filter fields based on the selected Client
    ###

    # Remove the '.blurrable' class to avoid this inline field validation error:
    # inline_validation.js:51 Uncaught TypeError: Cannot read property 'lastIndexOf' of undefined
    $(".blurrable").removeClass("blurrable")

    # Create empty state var
    # We include initialisation for a couple of special fields that
    # do not directly tie to specific form controls
    bika.lims.ar_add = {}
    bika.lims.ar_add.state = {}
    nr_ars = parseInt($('input[id="ar_count"]').val(), 10)
    console.debug "Initializing for #{nr_ars} ARs"
    arnum = 0

    while arnum < nr_ars
      bika.lims.ar_add.state[arnum] = 'Analyses': []
      arnum++

    # Remove "required" attribute; we will manage this manually, later.
    elements = $('input[type!=\'hidden\']').not('[disabled]')
    i = elements.length - 1
    while i >= 0
      element = elements[i]
      $(element).removeAttr 'required'
      i--

    # All Archetypes generated elements are given an ID <fieldname>, and
    # this means there are duplicated IDs in the form.  I will change
    # their IDs to <fieldname>_<arnum> to prevent this.
    $.each $('[id^=\'archetypes-fieldname\']'), (i, div) ->
      arnum = $(div).parents('[arnum]').attr('arnum')
      fieldname = $(div).parents('[fieldname]').attr('fieldname')
      e = undefined
      console.debug "Renaming field #{fieldname} for AR #{arnum}"

      # first rename the HTML elements
      if $(div).hasClass('ArchetypesSelectionWidget')
        e = $(div).find('select')[0]
        $(e).attr 'id', fieldname + '-' + arnum
        $(e).attr 'name', fieldname + '-' + arnum

      else if $(div).hasClass('ArchetypesReferenceWidget')
        e = $(div).find('[type="text"]')[0]
        $(e).attr 'id', $(e).attr('id') + '-' + arnum
        $(e).attr 'name', $(e).attr('name') + '-' + arnum
        e = $(div).find('[id$="_uid"]')[0]
        $(e).attr 'id', fieldname + '-' + arnum + '_uid'
        $(e).attr 'name', fieldname + '-' + arnum + '_uid'
        e = $(div).find('[id$="-listing"]')
        if e.length > 0
          $(e).attr 'id', fieldname + '-' + arnum + '-listing'

      else if $(div).hasClass('ArchetypesStringWidget') or $(div).hasClass('ArchetypesDateTimeWidget')
        e = $(div).find('[type="text"]')[0]
        $(e).attr 'id', $(e).attr('id') + '-' + arnum
        $(e).attr 'name', $(e).attr('name') + '-' + arnum

      else if $(div).hasClass('ArchetypesBooleanWidget')
        e = $(div).find('[type="checkbox"]')[0]
        $(e).attr 'id', $(e).attr('id') + '-' + arnum
        $(e).attr 'name', $(e).attr('name') + '-' + arnum + ':boolean'
        e = $(div).find('[type="hidden"]')[0]
        $(e).attr 'name', $(e).attr('name') + '-' + arnum + ':boolean:default'

      else if $(div).hasClass('RejectionWidget')
        # checkbox
        e = $(div).find('input[id="RejectionReasons.checkbox"]')[0]
        $(e).attr 'id', fieldname + '.checkbox-' + arnum
        $(e).attr 'name', fieldname + '.checkbox-' + arnum
        # multiple selection
        e = $(div).find('select[id="RejectionReasons.multiselection"]')[0]
        $(e).attr 'id', fieldname + '.multiselection-' + arnum
        $(e).attr 'name', fieldname + '.multiselection-' + arnum
        # Other checkbox
        e = $(div).find('input[id="RejectionReasons.checkbox.other"]')[0]
        $(e).attr 'id', fieldname + '.checkbox.other-' + arnum
        $(e).attr 'name', fieldname + '.checkbox.other-' + arnum
        # Other input
        e = $(div).find('input[id="RejectionReasons.textfield.other"]')[0]
        $(e).attr 'id', fieldname + '.textfield.other-' + arnum
        $(e).attr 'name', fieldname + '.textfield.other-' + arnum

      else if $(div).hasClass('ArchetypesTextAreaWidget')
        e = $(div).find('textarea')[0]
        $(e).attr 'id', fieldname + '-' + arnum
        $(e).attr 'name', fieldname + '-' + arnum

      else if $(div).hasClass('ArchetypesDecimalWidget')
        e = $(div).find('input')[0]
        $(e).attr 'id', fieldname + '-' + arnum
        $(e).attr 'name', fieldname + '-' + arnum

      else
        console.warn "Could not rename #{fieldname} for AR #{arnum}!"

      # then change the ID of the containing div itself
      $(div).attr 'id', 'archetypes-fieldname-' + fieldname + '-' + arnum
      return

    # clear existing values (on page reload).
    # XXX: Where is this #singleservice element?
    $('#singleservice').val ''
    $('#singleservice').attr 'uid', 'new'
    $('#singleservice').attr 'title', ''
    $('#singleservice').parents('[uid]').attr 'uid', 'new'
    $('#singleservice').parents('[keyword]').attr 'keyword', ''
    $('#singleservice').parents('[title]').attr 'title', ''
    $('input[type=\'checkbox\']').removeAttr 'checked'
    $('.min,.max,.error').val ''

    # filter fields based on the selected Client
    # we need a little delay here to be sure the elements have finished
    # initialising before we attempt to filter them
    setTimeout (->
      nr_ars = parseInt($('#ar_count').val(), 10)
      arnum = 0
      while arnum < nr_ars
        filter_by_client arnum
        arnum++
      return
    ), 250

    ###* If client only has one contect, and the analysis request comes from
      * a client, then Auto-complete first Contact field.
      * If client only has one contect, and the analysis request comes from
      * a batch, then Auto-complete all Contact field.
    ###

    uid = $($('tr[fieldname=\'Client\'] input')[0]).attr('uid')
    request_data =
      catalog_name: 'portal_catalog'
      portal_type: 'Contact'
      getParentUID: uid
      inactive_state: 'active'

    window.bika.lims.jsonapi_read request_data, (data) ->
      ###* If the analysis request comes from a client
      # window.location.pathname.split('batches') should not be splitted
      # in 2 parts
      ###

      if data.success and data.total_objects == 1 and window.location.pathname.split('batches').length < 2
        contact = data.objects[0]
        $('input#Contact-0').attr('uid', contact['UID']).val(contact['Title']).attr('uid_check', contact['UID']).attr 'val_check', contact['UID']
        $('#Contact-0_uid').val contact['UID']
        state_set 0, 'Contact', contact['UID']
        cc_contacts_set 0

      else if data.success and data.total_objects == 1 and window.location.pathname.split('batches').length == 2
        nr_ars = parseInt($('#ar_count').val(), 10)
        contact = data.objects[0]
        $('input[id^="Contact-"]').attr('uid', contact['UID']).val(contact['Title']).attr('uid_check', contact['UID']).attr 'val_check', contact['UID']
        $('[id^="Contact-"][id$="_uid"]').val contact['UID']
        i = 0
        while i < nr_ars
          state_set i, 'Contact', contact['UID']
          cc_contacts_set i
          i++

      return
    return


  state_set = (arnum, fieldname, value) ->
    console.info "state_set::#{fieldname} -> #{value}"

    ### Use this function to set values in the state variable.
    ###

    arnum_i = parseInt(arnum, 10)
    if fieldname and value != undefined
      # console.log("arnum=" + arnum + ", fieldname=" + fieldname + ", value=" + value)
      bika.lims.ar_add.state[arnum_i][fieldname] = value
    return


  from_sampling_round = ->
    # Checking if the request comes from a sampling round
    sPageURL = decodeURIComponent(window.location.search.substring(1))
    sURLVariables = sPageURL.split('&')
    sParameterName = undefined
    i = 0
    while i < sURLVariables.length
      sParameterName = sURLVariables[i].split('=')
      if sParameterName[0] == 'samplinground'
        # If the request comes from a sampling round, we have to set up the form with the sampling round info
        samplinground_UID = sParameterName[1]
        setupSamplingRoundInfo samplinground_UID
      i++
    return


  setupSamplingRoundInfo = (samplinground_UID) ->
    ###*
    # This function sets up the sampling round information such as the sampling round to use and the
    # different analysis request templates needed.
    # :samplinground_uid: a string with the sampling round uid
    ###

    request_data =
      catalog_name: 'portal_catalog'
      portal_type: 'SamplingRound'
      UID: samplinground_UID
      include_fields: [
        'Title'
        'UID'
        'analysisRequestTemplates'
        'samplingRoundSamplingDate'
      ]

    window.bika.lims.jsonapi_read request_data, (data) ->
      if data.objects.length > 0
        spec = data.objects[0]
        # Selecting the sampling round
        sr = $('input[id^="SamplingRound-"]')
        # Filling out and halting the sampling round fields
        sr.attr('uid', spec['UID']).val(spec['Title']).attr('uid_check', spec['UID']).attr('val_check', spec['Title']).attr 'disabled', 'disabled'
        $('[id^="SamplingRound-"][id$="_uid"]').val spec['UID']
        # Filling out and halting the analysis request templates fields
        ar_templates = $('input[id^="Template-"]:visible')
        ar_templates.each (index, element) ->
          $(element).attr('uid', spec['analysisRequestTemplates'][index][1]).val(spec['analysisRequestTemplates'][index][0]).attr('uid_check', spec['analysisRequestTemplates'][index][1]).attr('val_check', spec['analysisRequestTemplates'][index][1]).attr 'disabled', 'disabled'
          $('input#Template-' + index + '_uid').val spec['analysisRequestTemplates'][index][1]
          template_set index
          return
        # Writing the sampling date
        $('input[id^="SamplingDate-"]:visible').val spec['samplingRoundSamplingDate']
        # Hiding all fields which depends on the sampling round
        to_disable = [
          'Specification'
          'SamplePoint'
          'ReportDryMatter'
          'Sample'
          'Batch'
          'SubGroup'
          'SamplingDate'
          'Composite'
          'Profiles'
          'DefaultContainerType'
          'AdHoc'
        ]
        i = 0
        while to_disable.length > i
          $('tr[fieldname="' + to_disable[i] + '"]').hide()
          i++
        sampleTypes = $('input[id^="SampleType-"]')
        sampleTypes.each (index, element) ->
          # We have to hide the field
          if $(element).attr('uid')
            $(element).attr 'disabled', 'disabled'
          return
        # Hiding prices
        $('table.add tfoot').hide()
        # Hiding not needed services
        $('th.collapsed').hide()
        # Disabling service checkboxes
        setTimeout (->
          # Some function enables the services checkboxes with a lot of delay caused by AJAX, so we
          # need this setTimeout
          $('input[selector^="bika_analysisservices"]').attr 'disabled', true
          $('input[selector^="ar."][type="checkbox"]').attr 'disabled', true
          $('input.min, input.max, input.error').attr 'disabled', true
          return
        ), 1000
      return
    return


  filter_combogrid = (element, filterkey, filtervalue, querytype) ->
    ### Apply or modify a query filter for a reference widget.
    #
    #  This will set the options, then re-create the combogrid widget
    #  with the new filter key/value.
    #
    #  querytype can be 'base_query' or 'search_query'.
    ###

    if !$(element).is(':visible')
      return
    if !querytype
      querytype = 'base_query'
    query = $.parseJSON($(element).attr(querytype))
    query[filterkey] = filtervalue
    $(element).attr querytype, $.toJSON(query)
    options = $.parseJSON($(element).attr('combogrid_options'))
    options.url = window.location.href.split('/ar_add')[0] + '/' + options.url
    options.url = options.url + '?_authenticator=' + $('input[name=\'_authenticator\']').val()
    options.url = options.url + '&catalog_name=' + $(element).attr('catalog_name')
    if querytype == 'base_query'
      options.url = options.url + '&base_query=' + $.toJSON(query)
      options.url = options.url + '&search_query=' + $(element).attr('search_query')
    else
      options.url = options.url + '&base_query=' + $(element).attr('base_query')
      options.url = options.url + '&search_query=' + $.toJSON(query)
    options.url = options.url + '&colModel=' + $.toJSON($.parseJSON($(element).attr('combogrid_options')).colModel)
    options.url = options.url + '&search_fields=' + $.toJSON($.parseJSON($(element).attr('combogrid_options'))['search_fields'])
    options.url = options.url + '&discard_empty=' + $.toJSON($.parseJSON($(element).attr('combogrid_options'))['discard_empty'])
    options.force_all = 'false'
    $(element).combogrid options
    $(element).attr 'search_query', '{}'
    return


  filter_by_client = (arnum) ->
    ###**
    # Filter all Reference fields that reference Client items
    #
    # Some reference fields can select Lab or Client items.  In these
    # cases, the 'getParentUID' or 'getClientUID' index is used
    # to filter against Lab and Client folders.
    ###

    element = undefined
    uids = undefined
    uid = $($('tr[fieldname=\'Client\'] td[arnum=\'' + arnum + '\'] input')[0]).attr('uid')
    element = $('tr[fieldname=Contact] td[arnum=' + arnum + '] input')[0]
    filter_combogrid element, 'getParentUID', uid
    element = $('tr[fieldname=CCContact] td[arnum=' + arnum + '] input')[0]
    filter_combogrid element, 'getParentUID', uid
    element = $('tr[fieldname=InvoiceContact] td[arnum=' + arnum + '] input')[0]
    filter_combogrid element, 'getParentUID', uid
    uids = [
      uid
      $('#bika_setup').attr('bika_samplepoints_uid')
    ]
    element = $('tr[fieldname=SamplePoint] td[arnum=' + arnum + '] input')[0]
    filter_combogrid element, 'getClientUID', uids
    uids = [
      uid
      $('#bika_setup').attr('bika_artemplates_uid')
    ]
    element = $('tr[fieldname=Template] td[arnum=' + arnum + '] input')[0]
    filter_combogrid element, 'getClientUID', uids
    uids = [
      uid
      $('#bika_setup').attr('bika_analysisprofiles_uid')
    ]
    element = $('tr[fieldname=Profiles] td[arnum=' + arnum + '] input')[0]
    filter_combogrid element, 'getClientUID', uids
    uids = [
      uid
      $('#bika_setup').attr('bika_analysisspecs_uid')
    ]
    element = $('tr[fieldname=Specification] td[arnum=' + arnum + '] input')[0]
    filter_combogrid element, 'getClientUID', uids
    return


  hashes_to_hash = (hashlist, key) ->
    ### Convert a list of hashes to a hash, by one of their keys.
    #
    # This will return a single hash: the key that will be used must
    # of course exist in all hashes in hashlist.
    ###

    ret = {}
    i = 0
    while i < hashlist.length
      ret[hashlist[i][key]] = hashlist[i]
      i++
    ret


  hash_to_hashes = (hash) ->
    ### Convert a single hash into a list of hashes
    #
    # Basically, this just returns the keys, unmodified.
    ###

    ret = []
    $.each hash, (i, v) ->
      ret.push v
      return
    ret


  get_arnum = (element) ->
    # Should be able to deduce the arnum of any form element
    arnum = undefined
    # Most AR schema field widgets have [arnum=<arnum>] on their parent TD
    arnum = $(element).parents('[arnum]').attr('arnum')
    if arnum
      return arnum
    # analysisservice checkboxes have an ar.<arnum> class on the parent TD
    td = $(element).parents('[class*=\'ar\\.\']')
    if td.length > 0
      arnum = $(td).attr('class').split('ar.')[1].split()[0]
      if arnum
        return arnum
    console.error 'No arnum found for element ' + element
    return


  destroy = (arr, val) ->
    i = 0
    while i < arr.length
      if arr[i] == val
        arr.splice i, 1
      i++
    arr

  # Generic handlers for more than one field  ///////////////////////////////

  ###
   checkbox_change - applies to all except analysis services
   checkbox_change_handler
   referencewidget_change - applies to all except #singleservice
   referencewidget_change_handler
   select_element_change - select elements are a bit different
   select_element_change_handler
   textinput_change - all except referencwidget text elements
   textinput_change_handler
  ###

  checkbox_change_handler = (element) ->
    arnum = get_arnum(element)
    fieldname = $(element).parents('[fieldname]').attr('fieldname')
    value = $(element).prop('checked')
    state_set arnum, fieldname, value
    return


  checkbox_change = ->
    ### Generic state-setter for AR field checkboxes
    # The checkboxes used to select analyses are handled separately.
    ###

    $('tr[fieldname] input[type="checkbox"]').not('[class^="rejectionwidget-checkbox"]').live('change copy', ->
      checkbox_change_handler this
      return
    ).each (i, e) ->
      # trigger copy on form load
      $(e).trigger 'copy'
      return
    return


  referencewidget_change_handler = (element, item) ->
    arnum = get_arnum(element)
    fieldname = $(element).parents('[fieldname]').attr('fieldname')
    multiValued = $(element).attr('multiValued') == '1'
    value = item.UID
    if multiValued
      # modify existing values
      uid_element = $(element).siblings('input[name*=\'_uid\']')
      existing_values = $(uid_element).val()
      if existing_values.search(value) == -1
        value = existing_values + ',' + value
      else
        value = existing_values
    state_set arnum, fieldname, value
    return


  referencewidget_change = ->

    ### Generic state-setter for AR field referencewidgets
    ###

    $('tr[fieldname] input.referencewidget').live 'selected', (event, item) ->
      referencewidget_change_handler this, item
      return
    # we must create a fake 'item' for this handler
    $('tr[fieldname] input.referencewidget').live 'copy', (event) ->
      item = UID: $(this).attr('uid')
      referencewidget_change_handler this, item
      return
    return


  rejectionwidget_change_handler = (element, item) ->
    # It goes to the upper element of the widget and gets all the values
    # to be stored in the state variable
    td = $(element).closest('td')
    # Init variables
    ch_val = false
    multi_val = []
    other_ch_val = false
    other_val = ''
    option = undefined
    # Getting each value deppending on the checkbox status
    ch_val = $(td).find('.rejectionwidget-checkbox').prop('checked')
    if ch_val
      # Getting the selected options and adding them to the list
      selected_options = $(td).find('.rejectionwidget-multiselect').find('option')
      i = 0
      while selected_options.length > i
        option = selected_options[i]
        if option.selected
          multi_val.push $(option).val()
        i++
      other_ch_val = $(td).find('.rejectionwidget-checkbox-other').prop('checked')
      if other_ch_val
        other_val = $(td).find('.rejectionwidget-input-other').val()
    # Gathering all values and writting them to the "global" variable state
    rej_widget_state =
      checkbox: ch_val
      selected: multi_val
      checkbox_other: other_ch_val
      other: other_val
    fieldname = $(element).parents('[fieldname]').attr('fieldname')
    arnum = get_arnum(element)
    state_set arnum, fieldname, rej_widget_state
    return


  rejectionwidget_change = ->
    # Deals with the changes in rejection widgets and register the values to
    # the state variable as a dictionary.
    $('tr[fieldname] input.rejectionwidget-checkbox,' + 'tr[fieldname] select.rejectionwidget-multiselect,' + 'tr[fieldname] input.rejectionwidget-checkbox-other,' + 'tr[fieldname] input.rejectionwidget-input-other').live 'change copy select', (event, item) ->
      rejectionwidget_change_handler this, item
      return
    return


  select_element_change_handler = (element) ->
    arnum = get_arnum(element)
    fieldname = $(element).parents('[fieldname]').attr('fieldname')
    value = $(element).val()
    state_set arnum, fieldname, value
    return


  select_element_change = ->
    ### Generic state-setter for SELECT inputs
    ###

    $('tr[fieldname] select').not('[class^="rejectionwidget-multiselect"]').live('change copy', (event, item) ->
      select_element_change_handler this
      return
    ).each (i, e) ->
      # trigger copy on form load
      $(e).trigger 'copy'
      return
    return


  textinput_change_handler = (element) ->
    arnum = get_arnum(element)
    fieldname = $(element).parents('[fieldname]').attr('fieldname')
    value = $(element).val()
    state_set arnum, fieldname, value
    return


  textinput_change = ->
    ### Generic state-setter for TEXT inputs
    ###

    $('tr[fieldname] input[type="text"]').not('[class^="rejectionwidget-input"]').not('#singleservice').not('.referencewidget').live('change copy', ->
      textinput_change_handler this
      return
    ).each (i, e) ->
      if $(e).val()
        # trigger copy on form load
        $(e).trigger 'copy'
      return


  textarea_change_handler = (element) ->
    arnum = get_arnum(element)
    fieldname = $(element).parents('[fieldname]').attr('fieldname')
    value = $(element).val()
    state_set arnum, fieldname, value
    return


  textarea_change = ->
    ### Generic state-setter for TEXTAREA fields
    ###

    $('tr[fieldname] textarea').on('change copy', ->
      textarea_change_handler this
      return
    ).each (i, e) ->
      if $(e).val()
        # trigger copy on form load
        $(e).trigger 'copy'
      return
    return
    return


  copybutton_selected = ->
    $('img.copybutton').live 'click', ->
      nr_ars = parseInt($('input[id="ar_count"]').val(), 10)
      tr = $(this).parents('tr')[0]
      fieldname = $(tr).attr('fieldname')
      td1 = $(tr).find('td[arnum="0"]')[0]
      e = undefined
      td = undefined
      html = undefined

      # ReferenceWidget cannot be simply copied, the combogrid dropdown widgets
      # don't cooperate and the multiValued div must be copied.
      if $(td1).find('.ArchetypesReferenceWidget').length > 0
        val1 = $(td1).find('input[type="text"]').val()
        uid1 = $(td1).find('input[type="text"]').attr('uid')
        multi_div = $('#' + fieldname + '-0-listing')
        arnum = 1
        while arnum < nr_ars
          td = $(tr).find('td[arnum="' + arnum + '"]')[0]
          e = $(td).find('input[type="text"]')
          # First we copy the attributes of the text input:
          $(e).val val1
          $(e).attr 'uid', uid1
          # then the hidden *_uid shadow field
          $(td).find('input[id$="_uid"]').val uid1
          # then the multiValued div
          multi_divX = multi_div.clone(true)
          $(multi_divX).attr 'id', fieldname + '-' + arnum + '-listing'
          $('#' + fieldname + '-' + arnum + '-listing').replaceWith multi_divX
          $(e).trigger 'copy'
          arnum++
      else if $(td1).find('.RejectionWidget').length > 0
        checkbox = $(td1).find('.rejectionwidget-checkbox').prop('checked')
        arnum = 1
        while arnum < nr_ars
          td = $(tr).find('td[arnum="' + arnum + '"]')[0]
          e = $(td).find('.rejectionwidget-checkbox')[0]
          if checkbox
            $(e).attr 'checked', true
          else
            $(e).removeAttr 'checked'
          $(e).trigger 'copy'
          arnum++
        checkbox_other = $(td1).find('.rejectionwidget-checkbox-other').prop('checked')
        arnum = 1
        while arnum < nr_ars
          td = $(tr).find('td[arnum="' + arnum + '"]')[0]
          e = $(td).find('.rejectionwidget-checkbox-other')[0]
          if checkbox_other
            $(e).attr 'checked', true
          else
            $(e).removeAttr 'checked'
          $(e).trigger 'copy'
          arnum++
        input_other = $(td1).find('.rejectionwidget-input-other').val()
        arnum = 1
        while arnum < nr_ars
          td = $(tr).find('td[arnum="' + arnum + '"]')[0]
          e = $(td).find('.rejectionwidget-input-other')[0]
          $(e).val input_other
          $(e).trigger 'copy'
          arnum++
        select_options = $(td1).find('.rejectionwidget-multiselect').find('option')
        i = 0
        while select_options.length > i
          option = select_options[i]
          value = $(option).val()
          selected = option.selected
          arnum = 1
          while arnum < nr_ars
            td = $(tr).find('td[arnum="' + arnum + '"]')[0]
            e = $(td).find('.rejectionwidget-multiselect option[value="' + value + '"]')
            $(e).attr 'selected', selected
            $(td).find('select.rejectionwidget-multiselect').trigger 'copy'
            arnum++
          i++
      else if $(td1).find('select').length > 0
        input = $(td1).find('select').val()
        arnum = 1
        while arnum < nr_ars
          td = $(tr).find('td[arnum="' + arnum + '"]')[0]
          e = $(td).find('select')[0]
          $(e).val input
          $(e).trigger 'copy'
          arnum++
      else if $(td1).find('input[type="text"]').length > 0
        val1 = $(td1).find('input').val()
        arnum = 1
        while arnum < nr_ars
          td = $(tr).find('td[arnum="' + arnum + '"]')[0]
          e = $(td).find('input')[0]
          $(e).val val1
          $(e).trigger 'copy'
          arnum++
      else if $(td1).find('textarea').length > 0
        val1 = $(td1).find('textarea').val()
        arnum = 1
        while arnum < nr_ars
          td = $(tr).find('td[arnum="' + arnum + '"]')[0]
          e = $(td).find('textarea')[0]
          $(e).val val1
          $(e).trigger 'copy'
          arnum++
      else if $(td1).find('input[type="checkbox"]').length > 0
        val1 = $(td1).find('input[type="checkbox"]').prop('checked')
        arnum = 1
        while arnum < nr_ars
          td = $(tr).find('td[arnum="' + arnum + '"]')[0]
          e = $(td).find('input[type="checkbox"]')[0]
          if val1
            $(e).attr 'checked', true
          else
            $(e).removeAttr 'checked'
          $(e).trigger 'copy'
          arnum++
      return
    return

  # Specific handlers for fields requiring special actions  /////////////////

  ###
   --- These configure the jquery bindings for different fields ---
   client_selected        -
   contact_selected       -
   spec_selected          -
   samplepoint_selected   -
   sampletype_selected    -
   profile_selected       -
   template_selected      -
   drymatter_selected     -
   --- These are called by the above bindings, or by other javascript ---
   cc_contacts_set            - when contact is selected, apply CC Contacts
   spec_field_entry           - min/max/error field
   specification_refetch      - lookup ajax spec and apply to min/max/error
   specification_apply        - just re-apply the existing spec
   spec_from_sampletype       - sampletype selection may set the current spec
   spec_filter_on_sampletype  - there may be >1 allowed specs for a sampletype.
   samplepoint_set            - filter with sampletype<->samplepoint relation
   sampletype_set             - filter with sampletype<->samplepoint relation
   profile_set                - apply profile
   profile_unset_trigger      - Unset the deleted profile and its analyses
   template_set               - apply template
   template_unset             - empty template field in form and state
   drymatter_set              - select the DryMatterService and set state
   drymatter_unset            - unset state
  ###

  client_selected = ->

    ### Client field is visible and a client has been selected
    ###

    $('tr[fieldname="Client"] input[type="text"]').live('selected copy', (event, item) ->
      # filter any references that search inside the Client.
      arnum = get_arnum(this)
      filter_by_client arnum
      return
    ).each (i, e) ->
      if $(e).val()
        # trigger copy on form load
        $(e).trigger 'copy'
      return
    return


  contact_selected = ->

    ### Selected a Contact: retrieve and complete UI for CC Contacts
    ###

    $('tr[fieldname="Contact"] input[type="text"]').live 'selected copy', (event, item) ->
      arnum = get_arnum(this)
      cc_contacts_set arnum
      return
    # We do not trigger copy event on load for Contact because doing so would
    # clear any default value supplied for the CCContact field.
    return


  cc_contacts_set = (arnum) ->

    ### Setting the CC Contacts after a Contact was set
    #
    # Contact.CCContact may contain a list of Contact references.
    # So we need to select them in the form with some fakey html,
    # and set them in the state.
    ###

    td = $('tr[fieldname=\'Contact\'] td[arnum=\'' + arnum + '\']')
    contact_element = $(td).find('input[type=\'text\']')[0]
    contact_uid = $(contact_element).attr('uid')
    # clear the CC selector widget and listing DIV
    cc_div = $('tr[fieldname=\'CCContact\'] td[arnum=\'' + arnum + '\'] .multiValued-listing')
    cc_uid_element = $('#CCContact-' + arnum + '_uid')
    $(cc_div).empty()
    $(cc_uid_element).empty()
    if contact_uid
      request_data =
        catalog_name: 'portal_catalog'
        UID: contact_uid
      window.bika.lims.jsonapi_read request_data, (data) ->
        if data.objects and data.objects.length > 0
          ob = data.objects[0]
          cc_titles = ob['CCContact']
          cc_uids = ob['CCContact_uid']
          if !cc_uids
            return
          $(cc_uid_element).val cc_uids.join(',')
          i = 0
          while i < cc_uids.length
            title = cc_titles[i]
            uid = cc_uids[i]
            del_btn_src = window.portal_url + '/++resource++bika.lims.images/delete.png'
            del_btn = '<img class=\'deletebtn\' data-contact-title=\'' + title + '\' src=\'' + del_btn_src + '\' fieldname=\'CCContact\' uid=\'' + uid + '\'/>'
            new_item = '<div class=\'reference_multi_item\' uid=\'' + uid + '\'>' + del_btn + title + '</div>'
            $(cc_div).append $(new_item)
            i++
          state_set arnum, 'CCContact', cc_uids.join(',')
        return
    return

  cc_contacts_deletebtn_click = ->
    $('tr[fieldname=\'CCContact\'] .reference_multi_item .deletebtn').unbind()
    $('tr[fieldname=\'CCContact\'] .reference_multi_item .deletebtn').live 'click', ->
      arnum = get_arnum(this)
      fieldname = $(this).attr('fieldname')
      uid = $(this).attr('uid')
      existing_uids = $('td[arnum="' + arnum + '"] input[name$="_uid"]').val().split(',')
      destroy existing_uids, uid
      $('td[arnum="' + arnum + '"] input[name$="CCContact-' + arnum + '_uid"]').val existing_uids.join(',')
      $('td[arnum="' + arnum + '"] input[name="CCContact-0"]').attr 'uid', existing_uids.join(',')
      $(this).parent('div').remove()
      return
    return


  spec_selected = ->

    ### Configure handler for the selection of a Specification
    #
    ###

    $('tr[fieldname=\'Specification\'] td[arnum] input[type=\'text\']').live('selected copy', (event, item) ->
      arnum = get_arnum(this)
      state_set arnum, 'Specification', $(this).attr('uid')
      specification_refetch arnum
      return
    ).each (i, e) ->
      if $(e).val()
        # trigger copy on form load
        $(e).trigger 'copy'
      return
    return


  spec_field_entry = ->
    ### Validate entry into min/max/error fields, and save them
    # to the state.
    #
    # If min>max or max<min, or error<>0,100, correct the values directly
    # in the field by setting one or the other to a "" value to indicate
    # an error
    ###

    $('.min, .max, .error').live 'change', ->
      td = $(this).parents('td')
      tr = $(td).parent()
      arnum = $(td).attr('arnum')
      uid = $(tr).attr('uid')
      keyword = $(tr).attr('keyword')
      min_element = $(td).find('.min')
      max_element = $(td).find('.max')
      error_element = $(td).find('.error')
      min = parseInt(min_element.val(), 10)
      max = parseInt(max_element.val(), 10)
      error = parseInt(error_element.val(), 10)
      if $(this).hasClass('min')
        if isNaN(min)
          $(min_element).val ''
        else if !isNaN(max) and min > max
          $(max_element).val ''
      else if $(this).hasClass('max')
        if isNaN(max)
          $(max_element).val ''
        else if !isNaN(min) and max < min
          $(min_element).val ''
      else if $(this).hasClass('error')
        if isNaN(error) or error < 0 or error > 100
          $(error_element).val ''
      arnum_i = parseInt(arnum, 10)
      state = bika.lims.ar_add.state[arnum_i]
      hash = hashes_to_hash(state['ResultsRange'], 'uid')
      hash[uid] =
        'min': min_element.val()
        'max': max_element.val()
        'error': error_element.val()
        'uid': uid
        'keyword': keyword
      hashes = hash_to_hashes(hash)
      state_set arnum, 'ResultsRange', hashes
      return
    return


  specification_refetch = (arnum) ->
    ### Lookup the selected specification with ajax, then set all
    # min/max/error fields in all columns to match.
    #
    # If the specification does not define values for a particular service,
    # the form values will not be cleared.
    ###

    d = $.Deferred()
    arnum_i = parseInt(arnum, 10)
    state = bika.lims.ar_add.state[arnum_i]
    spec_uid = state['Specification']
    if !spec_uid
      d.resolve()
      return d.promise()
    request_data =
      catalog_name: 'bika_setup_catalog'
      UID: spec_uid
    window.bika.lims.jsonapi_read request_data, (data) ->
      if data.success and data.objects.length > 0
        rr = data.objects[0]['ResultsRange']
        if rr and rr.length > 0
          state_set arnum, 'ResultsRange', rr
          specification_apply()
      d.resolve()
      return
    d.promise()


  specification_apply = ->
    nr_ars = parseInt($('input[id="ar_count"]').val(), 10)
    arnum = 0
    while arnum < nr_ars
      hashlist = bika.lims.ar_add.state[arnum]['ResultsRange']
      if hashlist
        spec = hashes_to_hash(hashlist, 'uid')
        $.each $('tr.service_selector td[class*=\'ar\\.' + arnum + '\']'), (i, td) ->
          uid = $(td).parents('[uid]').attr('uid')
          if uid and uid != 'new' and uid of spec
            min = $(td).find('.min')
            max = $(td).find('.max')
            error = $(td).find('.error')
            $(min).attr 'value', spec[uid].min
            $(max).attr 'value', spec[uid].max
            $(error).attr 'value', spec[uid].error
          return
      arnum++
    return


  set_spec_from_sampletype = (arnum) ->
    ### Look for Specifications with the selected SampleType.
    #
    # 1) Set the value of the Specification field
    # 2) Fetch the spec from the server, and set all the spec field values
    # 3) Set the partition indicator numbers.
    ###

    st_uid = $('tr[fieldname=\'SampleType\'] ' + 'td[arnum=\'' + arnum + '\'] ' + 'input[type=\'text\']').attr('uid')
    if !st_uid
      return
    spec_filter_on_sampletype arnum
    spec_element = $('tr[fieldname=\'Specification\'] ' + 'td[arnum=\'' + arnum + '\'] ' + 'input[type=\'text\']')
    spec_uid_element = $('tr[fieldname=\'Specification\'] ' + 'td[arnum=\'' + arnum + '\'] ' + 'input[id$=\'_uid\']')
    request_data =
      catalog_name: 'bika_setup_catalog'
      portal_type: 'AnalysisSpec'
      getSampleTypeUID: st_uid
      include_fields: [
        'Title'
        'UID'
        'ResultsRange'
      ]
    window.bika.lims.jsonapi_read request_data, (data) ->
      if data.objects.length > 0
        # If there is one Lab and one Client spec defined, the
        # client spec will be objects[0]
        spec = data.objects[0]
        # set spec values for this arnum
        $(spec_element).val spec['Title']
        $(spec_element).attr 'uid', spec['UID']
        $(spec_uid_element).val spec['UID']
        state_set arnum, 'Specification', spec['UID']
        # set ResultsRange here!
        rr = data.objects[0]['ResultsRange']
        if rr and rr.length > 0
          state_set arnum, 'ResultsRange', rr
          specification_apply()
      return
    return


  spec_filter_on_sampletype = (arnum) ->
    ### Possibly filter the Specification dropdown when SampleType selected
    #
    # when a SampleType is selected I will allow only specs to be
    # selected which have a matching SampleType value, or which
    # have no sampletype set.
    ###

    arnum_i = parseInt(arnum, 10)
    sampletype_uid = bika.lims.ar_add.state[arnum_i]['SampleType']
    spec_element = $('tr[fieldname=\'Specification\'] td[arnum=\'' + arnum + '\'] input[type=\'text\']')
    query_str = $(spec_element).attr('search_query')
    query = $.parseJSON(query_str)
    if query.hasOwnProperty('getSampleTypeUID')
      delete query.getSampleTypeUID
    query.getSampleTypeUID = [
      encodeURIComponent(sampletype_uid)
      ''
    ]
    query_str = $.toJSON(query)
    $(spec_element).attr 'search_query', query_str
    return


  samplepoint_selected = ->
    $('tr[fieldname=\'SamplePoint\'] td[arnum] input[type=\'text\']').live('selected copy', (event, item) ->
      arnum = get_arnum(this)
      samplepoint_set arnum
      return
    ).each (i, e) ->
      if $(e).val()
        # trigger copy on form load
        $(e).trigger 'copy'
      return
    return


  samplepoint_set = (arnum) ->
    ###**
    # Sample point and Sample type can set each other.
    ###

    spe = $('tr[fieldname=\'SamplePoint\'] td[arnum=\'' + arnum + '\'] input[type=\'text\']')
    ste = $('tr[fieldname=\'SampleType\'] td[arnum=\'' + arnum + '\'] input[type=\'text\']')
    filter_combogrid ste, 'getSamplePointTitle', $(spe).val(), 'search_query'
    return


  sampletype_selected = ->
    $('tr[fieldname=\'SampleType\'] td[arnum] input[type=\'text\']').live('selected copy', (event, item) ->
      arnum = get_arnum(this)
      sampletype_set arnum
      return
    ).each (i, e) ->
      if $(e).val()
        # trigger copy on form load
        $(e).trigger 'copy'
      return
    return


  sampletype_set = (arnum) ->
    # setting the Sampletype - Fix the SamplePoint filter:
    # 1. Can select SamplePoint which does not link to any SampleType
    # 2. Can select SamplePoint linked to This SampleType.
    # 3. Cannot select SamplePoint linked to other sample types (and not to this one)
    spe = $('tr[fieldname=\'SamplePoint\'] td[arnum=\'' + arnum + '\'] input[type=\'text\']')
    ste = $('tr[fieldname=\'SampleType\'] td[arnum=\'' + arnum + '\'] input[type=\'text\']')
    filter_combogrid spe, 'getSampleTypeTitle', $(ste).val(), 'search_query'
    set_spec_from_sampletype arnum
    partition_indicators_set arnum
    return


  profile_selected = ->
    ### A profile is selected.
    # - Set the profile's analyses (existing analyses will be cleared)
    # - Set the partition number indicators
    ###

    $('tr[fieldname=\'Profiles\'] td[arnum] input[type=\'text\']').live('selected', (event, item) ->
      arnum = $(this).parents('td').attr('arnum')
      # We'll use this array to get the new added profile
      uids_array = $('#Profiles-' + arnum).attr('uid').split(',')
      template_unset arnum
      profile_set(arnum, uids_array[uids_array.length - 1]).then ->
        specification_apply()
        partition_indicators_set arnum
        return
      return
    ).live('copy', (event, item) ->
      arnum = $(this).parents('td').attr('arnum')
      # We'll use this array to get the ALL profiles
      profiles = $('#Profiles-' + arnum)
      if profiles.attr('uid')
        uids_array = profiles.attr('uid').split(',')
        template_unset arnum
        i = 0
        while i < uids_array.length
          profile_set(arnum, uids_array[i]).then ->
            specification_apply()
            partition_indicators_set arnum
            return
          i++
        recalc_prices arnum
      return
    ).each (i, e) ->
      if $(e).val()
        # trigger copy on form load
        $(e).trigger 'copy'
      return
    return


  profile_set = (arnum, profile_uid) ->
    ### Set the profile analyses for the AR in this column
    #  also clear the AR Template field.
    ###

    d = $.Deferred()

    request_data =
      catalog_name: 'bika_setup_catalog'
      portal_type: 'AnalysisProfile'
      UID: profile_uid

    bika.lims.jsonapi_read request_data, (data) ->
      profile_objects = data['objects'][0]
      # Set the services from the template into the form
      profile = $('div.reference_multi_item[uid=\'' + profile_objects.UID + '\']')
      defs = []
      service_data = profile_objects['service_data']
      arprofile_services_uid = []
      profile.attr 'price', profile_objects['AnalysisProfilePrice']
      profile.attr 'useprice', profile_objects['UseAnalysisProfilePrice']
      profile.attr 'VATAmount', profile_objects['VATAmount']
      # I'm not sure about unset dry matter, but it was done in 318
      drymatter_unset arnum
      # Adding the services uids inside the analysis profile div, so we can get its analyses quickly
      if service_data.length != 0
        i = 0
        while i < service_data.length
          arprofile_services_uid.push service_data[i].UID
          i++
      profile.attr 'services', arprofile_services_uid
      # Setting the services checkboxes
      if $('#singleservice').length > 0
        defs.push expand_services_singleservice(arnum, service_data)
      else
        defs.push expand_services_bika_listing(arnum, service_data)
      # Call $.when with all deferreds
      $.when.apply(null, defs).then ->
        d.resolve()
        return
      return
    d.promise()


  profiles_unset_all = (arnum) ->
    ###*
    # This function remove all the selected analysis profiles
    ###

    if $('#Profiles-' + arnum).attr('uid') != ''
      $('#Profiles-' + arnum).attr 'price', ''
      $('#Profiles-' + arnum).attr 'services', $.toJSON([])
      $('#Profiles-' + arnum + '_uid').val ''
      # Getting all ar-arnum-Profiles-listing divisions to obtain their analysis services and uncheck them
      profiles = $('div#Profiles-' + arnum + '-listing').children()
      i = undefined
      i = profiles.length - 1
      while i >= 0
        unset_profile_analysis_services profiles[i], arnum
        i--
      # Removing all Profiles-arnum-listing divisions
      profiles.children().remove()
      recalc_prices arnum
    return


  profile_unset_trigger = ->
    ###**
     After deleting an analysis profile we have to uncheck their associated analysis services, so we need to bind
     the analyses service unseting function. Ever since this binding should be done on the delete image and
     (that is inserted dynamically), we need to settle the the event on the first ancestor element which doesn't
     load dynamically
    ###

    $('div[id^=\'archetypes-fieldname-Profiles-\']').on 'click', 'div.reference_multi_item .deletebtn', ->
      profile_object = $(this).parent()
      arnum = get_arnum(profile_object)
      unset_profile_analysis_services profile_object, arnum
      recalc_prices arnum
      return
    return


  unset_profile_analysis_services = (profile, arnum) ->
    ###*
    # The function unsets the selected analyses services related with the removed analysis profile.
    # :profile: the profile DOM division
    # :arnum: the number of the column
    #
    ###
    service_uids = $(profile).attr('services').split(',')
    i = undefined
    i = service_uids.length - 1
    while i >= 0
      analysis_cb_uncheck arnum, service_uids[i]
      i--
    return


  composite_selected = (arnum) ->
    $('input#Composite-' + arnum).live 'change', (event, item) ->
      template_unset arnum
      # Removing composite bindings
      $('input#Composite-' + arnum).unbind()
      return
    return


  template_selected = ->
    $('tr[fieldname=\'Template\'] td[arnum] input[type=\'text\']').live('selected copy', (event, item) ->
      arnum = $(this).parents('td').attr('arnum')
      template_set arnum
      return
    ).each (i, e) ->
      if $(e).val()
        # trigger copy on form load
        $(e).trigger 'copy'
      return
    return


  template_set = (arnum) ->
    d = $.Deferred()
    uncheck_all_services arnum
    td = $('tr[fieldname=\'Template\'] ' + 'td[arnum=\'' + arnum + '\'] ')
    title = $(td).find('input[type=\'text\']').val()
    request_data =
      catalog_name: 'bika_setup_catalog'
      title: title
      include_fields: [
        'SampleType'
        'SampleTypeUID'
        'SamplePoint'
        'SamplePointUID'
        'ReportDryMatter'
        'Composite'
        'AnalysisProfile'
        'Partitions'
        'Analyses'
        'Prices'
      ]
    window.bika.lims.jsonapi_read request_data, (data) ->
      `var td`
      if data.success and data.objects.length > 0
        template = data.objects[0]
        td = undefined
        # set SampleType
        td = $('tr[fieldname=\'SampleType\'] td[arnum=\'' + arnum + '\']')
        $(td).find('input[type=\'text\']').val(template['SampleType']).attr 'uid', template['SampleTypeUID']
        $(td).find('input[id$=\'_uid\']').val template['SampleTypeUID']
        state_set arnum, 'SampleType', template['SampleTypeUID']
        # set Specification from selected SampleType
        set_spec_from_sampletype arnum
        # set SamplePoint
        td = $('tr[fieldname=\'SamplePoint\'] td[arnum=\'' + arnum + '\']')
        $(td).find('input[type=\'text\']').val(template['SamplePoint']).attr 'uid', template['SamplePointUID']
        $(td).find('input[id$=\'_uid\']').val template['SamplePointUID']
        state_set arnum, 'SamplePoint', template['SamplePointUID']
        # Set the ARTemplate's AnalysisProfile
        td = $('tr[fieldname=\'Profile\'] td[arnum=\'' + arnum + '\']')
        if template['AnalysisProfile']
          $(td).find('input[type=\'text\']').val(template['AnalysisProfile']).attr 'uid', template['AnalysisProfileUID']
          $(td).find('input[id$=\'_uid\']').val template['AnalysisProfileUID']
          state_set arnum, 'Profile', template['AnalysisProfileUID']
        else
          profiles_unset_all arnum
        # Set the services from the template into the form
        defs = []
        if $('#singleservice').length > 0
          defs.push expand_services_singleservice(arnum, template['service_data'])
        else
          defs.push expand_services_bika_listing(arnum, template['service_data'])
        # Set the composite checkbox if needed
        td = $('tr[fieldname=\'Composite\'] td[arnum=\'' + arnum + '\']')
        if template['Composite']
          $(td).find('input[type=\'checkbox\']').attr 'checked', true
          state_set arnum, 'Composite', template['Composite']
          composite_selected arnum
        else
          $(td).find('input[type=\'checkbox\']').attr 'checked', false
        # Call $.when with all deferreds
        $.when.apply(null, defs).then ->
          # Dry Matter checkbox.  drymatter_set will calculate it's
          # dependencies and select them, and apply specs
          td = $('tr[fieldname=\'ReportDryMatter\'] td[arnum=\'' + arnum + '\']')
          if template['ReportDryMatter']
            $(td).find('input[type=\'checkbox\']').attr 'checked', true
            drymatter_set arnum, true
          # Now apply the Template's partition information to the form.
          # If the template doesn't specify partition information,
          # calculate it like normal.
          if template['Partitions']
            # Stick the current template's partition setup into the state
            # though it were sent there by a the deps calculating ajax
            state_set arnum, 'Partitions', template['Partitions']
          else
            # ajax request to calculate the partitions from the form
            partnrs_calc arnum
          _partition_indicators_set arnum
          d.resolve()
          return
      return
    d.promise()


  template_unset = (arnum) ->
    td = $('tr[fieldname=\'Template\'] td[arnum=\'' + arnum + '\']')
    $(td).find('input[type=\'text\']').val('').attr 'uid', ''
    $(td).find('input[id$=\'_uid\']').val ''
    return


  drymatter_selected = ->
    $('tr[fieldname=\'ReportDryMatter\'] td[arnum] input[type=\'checkbox\']').live('click copy', (event) ->
      arnum = get_arnum(this)
      if $(this).prop('checked')
        drymatter_set arnum
        partition_indicators_set arnum
      else
        drymatter_unset arnum
      return
    ).each (i, e) ->
      # trigger copy on form load
      $(e).trigger 'copy'
      return
    return


  drymatter_set = (arnum) ->
    ### set the Dry Matter service, dependencies, etc

     skip_indicators should be true if you want to prevent partition
     indicators from being set.  This is useful if drymatter is being
     checked during the application of a Template to this column.
    ###

    dm_service = $('#getDryMatterService')
    uid = $(dm_service).val()
    cat = $(dm_service).attr('cat')
    poc = $(dm_service).attr('poc')
    keyword = $(dm_service).attr('keyword')
    title = $(dm_service).attr('title')
    price = $(dm_service).attr('price')
    vatamount = $(dm_service).attr('vatamount')
    element = $('tr[fieldname=\'ReportDryMatter\'] ' + 'td[arnum=\'' + arnum + '\'] ' + 'input[type=\'checkbox\']')
    # set drymatter service IF checkbox is checked
    if $(element).attr('checked')
      checkbox = $('tr[uid=\'' + uid + '\'] ' + 'td[class*=\'ar\\.' + arnum + '\'] ' + 'input[type=\'checkbox\']')
      # singleservice selection gets some added attributes.
      # singleservice_duplicate will apply these to the TR it creates
      if $('#singleservice').length > 0
        if $(checkbox).length > 0
          $('#ReportDryMatter-' + arnum).prop 'checked', true
        else
          $('#singleservice').attr 'uid', uid
          $('#singleservice').attr 'keyword', keyword
          $('#singleservice').attr 'title', title
          $('#singleservice').attr 'price', price
          $('#singleservice').attr 'vatamount', vatamount
          singleservice_duplicate uid, title, keyword, price, vatamount
          $('#ReportDryMatter-' + arnum).prop 'checked', true
        state_analyses_push arnum, uid
      else
        $('#ReportDryMatter-' + arnum).prop 'checked', true
        state_analyses_push arnum, uid
      deps_calc arnum, [ uid ], true, _('Dry Matter')
      recalc_prices arnum
      state_set arnum, 'ReportDryMatter', true
      specification_apply()
    return


  drymatter_unset = (arnum) ->
    # if disabling, then we must still update the state var
    state_set arnum, 'ReportDryMatter', false
    return


  sample_selected = ->
    $('tr[fieldname=\'Sample\'] td[arnum] input[type=\'text\']').live('selected copy', (event, item) ->
      arnum = get_arnum(this)
      sample_set arnum
      return
    ).each (i, e) ->
      if $(e).val()
        # trigger copy on form load
        $(e).trigger 'copy'
      return
    $('tr[fieldname=\'Sample\'] td[arnum] input[type=\'text\']').live 'blur', (event, item) ->
      # This is weird, because the combogrid causes 'blur' when an item
      # is selected, also - but no harm done.
      arnum = get_arnum(this)
      if !$(this).val()
        $('td[arnum="' + arnum + '"]').find(':disabled').prop 'disabled', false
      return
    return


  sample_set = (arnum) ->
    # Selected a sample to create a secondary AR.
    $.getJSON window.location.href.split('/ar_add')[0] + '/secondary_ar_sample_info', {
      'Sample_uid': $('#Sample-' + arnum).attr('uid')
      '_authenticator': $('input[name="_authenticator"]').val()
    }, (data) ->
      `var element`
      if ! !data
        i = 0
        while i < data.length
          fieldname = data[i][0]
          fieldvalue = data[i][1]
          if fieldname.search('_uid') > -1
            # If this fieldname ends with _uid, then we consider it a reference,
            # and set the HTML elements accordingly
            fieldname = fieldname.split('_uid')[0]
            element = $('#' + fieldname + '-' + arnum)[0]
            $(element).attr 'uid', fieldvalue
            $(element).val fieldvalue
          else
            element = $('#' + fieldname + '-' + arnum)[0]
            # In cases where the schema has been made weird, this JS
            # must protect itself against non-existing form elements
            if !element
              console.log 'Selector #' + fieldname + '-' + arnum + ' not present in form'
              i++
              continue
            # here we go
            switch element.type
              when 'text', 'select-one'
                $(element).val fieldvalue
                if fieldvalue
                  $(element).trigger 'copy'
                $(element).prop 'disabled', true
              when 'checkbox'
                if fieldvalue
                  $(element).attr 'checked', true
                  $(element).trigger 'copy'
                else
                  $(element).removeAttr 'checked'
                $(element).prop 'disabled', true
              else
                console.log 'Unhandled field type for field ' + fieldname + ': ' + element.type
            state_set arnum, fieldname, fieldvalue
          i++
      return
    return

  # Functions related to the service_selector forms.  ///////////////////////

  ###
   singleservice_dropdown_init    - configure the combogrid (includes handler)
   singleservice_duplicate        - create new service row
   singleservice_deletebtn_click  - remove a service from the form
   expand_services_singleservice  - add a list of services (single-service)
   expand_services_bika_listing   - add a list of services (bika_listing)
   uncheck_all_services           - unselect all from form and state
  ###

  singleservice_dropdown_init = ->
    ###
    # Configure the single-service selector combogrid
    ###

    authenticator = $('[name=\'_authenticator\']').val()
    url = window.location.href.split('/portal_factory')[0] + '/service_selector?_authenticator=' + authenticator
    options =
      url: url
      width: '700px'
      showOn: false
      searchIcon: true
      minLength: '2'
      resetButton: false
      sord: 'asc'
      sidx: 'Title'
      colModel: [
        {
          'columnName': 'Title'
          'align': 'left'
          'label': 'Title'
          'width': '50'
        }
        {
          'columnName': 'Identifiers'
          'align': 'left'
          'label': 'Identifiers'
          'width': '35'
        }
        {
          'columnName': 'Keyword'
          'align': 'left'
          'label': 'Keyword'
          'width': '15'
        }
        {
          'columnName': 'Price'
          'hidden': true
        }
        {
          'columnName': 'VAT'
          'hidden': true
        }
        {
          'columnName': 'UID'
          'hidden': true
        }
      ]
      select: (event, ui) ->
        # Set some attributes on #singleservice to assist the
        # singleservice_duplicate function in it's work
        $('#singleservice').attr 'uid', ui['item']['UID']
        $('#singleservice').attr 'keyword', ui['item']['Keyword']
        $('#singleservice').attr 'title', ui['item']['Title']
        singleservice_duplicate ui['item']['UID'], ui['item']['Title'], ui['item']['Keyword'], ui['item']['Price'], ui['item']['VAT']
        return
    $('#singleservice').combogrid options
    return


  singleservice_duplicate = (new_uid, new_title, new_keyword, new_price, new_vatamount) ->
    ###
     After selecting a service from the #singleservice combogrid,
     this function is reponsible for duplicating the TR.  This is
     factored out so that template, profile etc, can also duplicate
     rows.

     Clobber the old row first, set all it's attributes to look like
     bika_listing version of itself.

     The attributes are a little wonky perhaps.  They should mimic the
     attributes that bika_listing rows get, so that the event handlers
     don't have to care.  In some cases though, we need functions for
     both.

     does not set any checkbox values
    ###

    # Grab our operating parameters from wherever
    uid = new_uid or $('#singleservice').attr('uid')
    keyword = new_keyword or $('#singleservice').attr('keyword')
    title = new_title or $('#singleservice').attr('title')
    price = new_price or $('#singleservice').attr('price')
    vatamount = new_vatamount or $('#singleservice').attr('vatamount')
    # If this service already exists, abort
    existing = $('tr[uid=\'' + uid + '\']')
    if existing.length > 0
      return
    # clone tr before anything else
    tr = $('#singleservice').parents('tr')
    new_tr = $(tr).clone()
    # store row attributes on TR
    $(tr).attr 'uid', uid
    $(tr).attr 'keyword', keyword
    $(tr).attr 'title', title
    $(tr).attr 'price', price
    $(tr).attr 'vatamount', vatamount
    # select_all
    $(tr).find('input[name=\'uids:list\']').attr 'value', uid
    # alert containers
    $(tr).find('.alert').attr 'uid', uid
    # Replace the text widget with a label, delete btn etc:
    service_label = $('<a href=\'#\' class=\'deletebtn\'><img src=\'' + portal_url + '/++resource++bika.lims.images/delete.png\' uid=\'' + uid + '\' style=\'vertical-align: -3px;\'/></a>&nbsp;' + '<span>' + title + '</span>')
    $(tr).find('#singleservice').replaceWith service_label
    # Set spec values manually for the row xyz
    # Configure and insert new row
    $(new_tr).find('[type=\'checkbox\']').removeAttr 'checked'
    $(new_tr).find('[type=\'text\']').val ''
    $(new_tr).find('#singleservice').attr 'uid', 'new'
    $(new_tr).find('#singleservice').attr 'keyword', ''
    $(new_tr).find('#singleservice').attr 'title', ''
    $(new_tr).find('#singleservice').attr 'price', ''
    $(new_tr).find('#singleservice').attr 'vatamount', ''
    $(new_tr).find('#singleservice').removeClass 'has_combogrid_widget'
    $(tr).after new_tr
    specification_apply()
    singleservice_dropdown_init()
    return


  singleservice_deletebtn_click = ->
    ### Remove the service row.
    ###

    $('.service_selector a.deletebtn').live 'click', (event) ->
      event.preventDefault()
      tr = $(this).parents('tr[uid]')
      checkboxes = $(tr).find('input[type=\'checkbox\']').not('[name=\'uids:list\']')
      i = 0
      while i < checkboxes.length
        element = checkboxes[i]
        arnum = get_arnum(element)
        uid = $(element).parents('[uid]').attr('uid')
        state_analyses_remove arnum, uid
        i++
      $(tr).remove()
      return
    return


  expand_services_singleservice = (arnum, service_data) ->
    ###
     When the single-service serviceselector is in place,
     this function is called to select services for setting a bunch
     of services in one AR, eg Profiles and Templates.

     service_data is included from the JSONReadExtender of Profiles and
     Templates.
    ###

    # First Select services which are already present
    uid = undefined
    keyword = undefined
    title = undefined
    price = undefined
    vatamount = undefined
    not_present = []
    sd = service_data
    i = 0
    while i < sd.length
      uid = sd[i]['UID']
      keyword = sd[i]['Keyword']
      price = sd[i]['Price']
      vatamount = sd[i]['VAT']
      e = $('tr[uid=\'' + uid + '\'] td[class*=\'ar\\.' + arnum + '\'] ' + 'input[type=\'checkbox\']')
      if e.length > 0 then analysis_cb_check(arnum, sd[i]['UID']) else not_present.push(sd[i])
      i++
    # Insert services which are not yet present
    i = 0
    while i < not_present.length
      title = not_present[i]['Title']
      uid = not_present[i]['UID']
      keyword = not_present[i]['Keyword']
      price = not_present[i]['Price']
      vatamount = not_present[i]['VAT']
      $('#singleservice').val title
      $('#singleservice').attr 'uid', uid
      $('#singleservice').attr 'keyword', keyword
      $('#singleservice').attr 'title', title
      $('#singleservice').attr 'price', price
      $('#singleservice').attr 'vatamount', vatamount
      singleservice_duplicate uid, title, keyword, price, vatamount
      analysis_cb_check arnum, uid
      i++
    recalc_prices arnum
    return


  expand_services_bika_listing = (arnum, service_data) ->
    # When the bika_listing serviceselector is in place,
    # this function is called to select services for Profiles and Templates.
    d = $.Deferred()
    services = []
    defs = []
    expanded_categories = []
    if ! !service_data
      si = 0
      while si < service_data.length
        # Expand category
        service = service_data[si]
        services.push service
        th = $('table[form_id=\'' + service['PointOfCapture'] + '\'] ' + 'th[cat=\'' + service['CategoryTitle'] + '\']')
        if expanded_categories.indexOf(th) < 0
          expanded_categories.push th
          def = $.Deferred()
          def = category_header_expand_handler(th)
          defs.push def
        si++
    # Call $.when with all deferreds
    $.when.apply(null, defs).then ->
      `var si`
      # select services
      si = 0
      while si < services.length
        analysis_cb_check arnum, services[si]['UID']
        si++
      recalc_prices arnum
      d.resolve()
      return
    d.promise()


  uncheck_all_services = (arnum) ->
    # Can't have dry matter without any services
    drymatter_unset arnum
    # Remove checkboxes for all existing services in this column
    cblist = $('tr[uid] td[class*=\'ar\\.' + arnum + '\'] ' + 'input[type=\'checkbox\']').filter(':checked')
    i = 0
    while i < cblist.length
      e = cblist[i]
      arnum = get_arnum(e)
      uid = $(e).parents('[uid]').attr('uid')
      analysis_cb_uncheck arnum, uid
      i++
    return


  category_header_clicked = ->
    # expand/collapse categorised rows
    ajax_categories = $('input[name=\'ajax_categories\']')
    $('.bika-listing-table th.collapsed').unbind().live 'click', (event) ->
      category_header_expand_handler this
      return
    $('.bika-listing-table th.expanded').unbind().live 'click', ->
      # After ajax_category expansion, collapse and expand work as they would normally.
      $(this).parent().nextAll('tr[cat=\'' + $(this).attr('cat') + '\']').toggle false
      # Set collapsed class on TR
      $(this).removeClass('expanded').addClass 'collapsed'
      return
    return


  category_header_expand_handler = (element) ->
    ### Deferred function to expand the category with ajax (or not!!)
     on first expansion.  duplicated from bika.lims.bikalisting.js, this code
     fires when categories are expanded automatically (eg, when profiles or templates require
     that the category contents are visible for selection)

     Also, this code returns deferred objects, not their promises.

     :param: element - The category header TH element which normally receives 'click' event
    ###

    def = $.Deferred()
    # with form_id allow multiple ajax-categorised tables in a page
    form_id = $(element).parents('[form_id]').attr('form_id')
    cat_title = $(element).attr('cat')
    ar_count = parseInt($('#ar_count').val(), 10)
    # URL can be provided by bika_listing classes, with ajax_category_url attribute.
    url = if $('input[name=\'ajax_categories_url\']').length > 0 then $('input[name=\'ajax_categories_url\']').val() else window.location.href.split('?')[0]
    # We will replace this element with downloaded items:
    placeholder = $('tr[data-ajax_category=\'' + cat_title + '\']')
    # If it's already been expanded, ignore
    if $(element).hasClass('expanded')
      def.resolve()
      return def
    # If ajax_categories are enabled, we need to go request items now.
    ajax_categories_enabled = $('input[name=\'ajax_categories\']')
    if ajax_categories_enabled.length > 0 and placeholder.length > 0
      options = {}
      # this parameter allows the receiving view to know for sure what's expected
      options['ajax_category_expand'] = 1
      options['cat'] = cat_title
      options['ar_count'] = ar_count
      options['form_id'] = form_id
      if $('.review_state_selector a.selected').length > 0
        # review_state must be kept the same after items are loaded
        # (TODO does this work?)
        options['review_state'] = $('.review_state_selector a.selected')[0].id
      $.ajax(
        url: url
        data: options).done (data) ->
        # LIMS-1970 Analyses from AR Add form not displayed properly
        rows = $('<table>' + data + '</table>').find('tr')
        $('[form_id=\'' + form_id + '\'] tr[data-ajax_category=\'' + cat_title + '\']').replaceWith rows
        $(element).removeClass('collapsed').addClass 'expanded'
        specification_apply()
        def.resolve()
        return
    else
      # When ajax_categories are disabled, all cat items exist as TR elements:
      $(element).parent().nextAll('tr[cat=\'' + cat_title + '\']').toggle true
      $(element).removeClass('collapsed').addClass 'expanded'
      def.resolve()
    def


  # analysis service checkboxes /////////////////////////////////////////////

  ### - analysis_cb_click   user interaction with form (select, unselect)
  # - analysis_cb_check   performs the same action, but from code (no .click)
  # - analysis_cb_uncheck does the reverse
  # - analysis_cb_after_change  always runs when service checkbox changes.
  # - state_analyses_push        add selected service to state
  # - state_analyses_remove      remove service uid from state
  ###

  analysis_cb_click = ->
    ### configures handler for click event on analysis checkboxes
    # and their associated select-all checkboxes.
    #
    # As far as possible, the bika_listing and single-select selectors
    # try to emulate each other's HTML structure in each row.
    #
    ###

    # regular analysis cb
    $('.service_selector input[type=\'checkbox\'][name!=\'uids:list\']').live 'click', ->
      arnum = get_arnum(this)
      uid = $(this).parents('[uid]').attr('uid')
      analysis_cb_after_change arnum, uid
      # Now we will manually decide if we should add or
      # remove the service UID from state['Analyses'].
      if $(this).prop('checked')
        state_analyses_push arnum, uid
      else
        state_analyses_remove arnum, uid
      # If the click is on "new" row, focus the selector
      if uid == 'new'
        $('#singleservice').focus()
      title = $(this).parents('[title]').attr('title')
      deps_calc arnum, [ uid ], false, title
      partition_indicators_set arnum
      recalc_prices arnum
      return
    # select-all cb
    $('.service_selector input[type=\'checkbox\'][name=\'uids:list\']').live 'click', ->
      nr_ars = parseInt($('#ar_count').val(), 10)
      tr = $(this).parents('tr')
      uid = $(this).parents('[uid]').attr('uid')
      checked = $(this).prop('checked')
      checkboxes = $(tr).find('input[type=checkbox][name!=\'uids:list\']')
      i = 0
      while i < checkboxes.length
        if checked
          analysis_cb_check i, uid
        else
          analysis_cb_uncheck i, uid
        recalc_prices i
        i++
      title = $(this).parents('[title]').attr('title')
      i = 0
      while i < nr_ars
        deps_calc i, [ uid ], true, title
        partition_indicators_set i
        i++
      # If the click is on "new" row, focus the selector
      if uid == 'new'
        $('#singleservice').focus()
      return
    return


  analysis_cb_check = (arnum, uid) ->
    ### Called to un-check an Analysis' checkbox as though it were clicked.
    ###

    cb = $('tr[uid=\'' + uid + '\'] ' + 'td[class*=\'ar\\.' + arnum + '\'] ' + 'input[type=\'checkbox\']')
    $(cb).attr 'checked', true
    analysis_cb_after_change arnum, uid
    state_analyses_push arnum, uid
    specification_apply()
    return


  analysis_cb_uncheck = (arnum, uid) ->
    ### Called to un-check an Analysis' checkbox as though it were clicked.
    ###

    cb = $('tr[uid=\'' + uid + '\'] ' + 'td[class*=\'ar\\.' + arnum + '\'] ' + 'input[type=\'checkbox\']')
    $(cb).removeAttr 'checked'
    analysis_cb_after_change arnum, uid
    state_analyses_remove arnum, uid
    return


  analysis_cb_after_change = (arnum, uid) ->
    ### If changed by click or by other trigger, all analysis checkboxes
    # must invoke this function.
    ###

    cb = $('tr[uid=\'' + uid + '\'] ' + 'td[class*=\'ar\\.' + arnum + '\'] ' + 'input[type=\'checkbox\']')
    tr = $(cb).parents('tr')
    checked = $(cb).prop('checked')
    checkboxes = $(tr).find('input[type=checkbox][name!=\'uids:list\']')
    # sync the select-all checkbox state
    nr_checked = $(checkboxes).filter(':checked')
    if nr_checked.length == checkboxes.length
      $(tr).find('[name=\'uids:list\']').attr 'checked', true
    else
      $(tr).find('[name=\'uids:list\']').removeAttr 'checked'
    # Unselecting Dry Matter Service unsets 'Report Dry Matter'
    if uid == $('#getDryMatterService').val() and !checked
      dme = $('#ReportDryMatter-' + arnum)
      $(dme).removeAttr 'checked'
    return


  state_analyses_push = (arnum, uid) ->
    arnum = parseInt(arnum, 10)
    analyses = bika.lims.ar_add.state[arnum]['Analyses']
    if analyses.indexOf(uid) == -1
      analyses.push uid
      state_set arnum, 'Analyses', analyses
    return


  state_analyses_remove = (arnum, uid) ->
    # This function removes the analysis services checkbox's uid from the astate's analysis list.
    arnum = parseInt(arnum, 10)
    analyses = bika.lims.ar_add.state[arnum]['Analyses']
    if analyses.indexOf(uid) > -1
      analyses.splice analyses.indexOf(uid), 1
      state_set arnum, 'Analyses', analyses
      # Ever since this is the last function invoked on the analysis services uncheck process, we'll
      # remove the analysis profile related with the unset services here.
      # Unselecting the related analysis profiles
      profiles = $('div#Profiles-' + arnum + '-listing').children()
      $.each profiles, (i, profile) ->
        `var i`
        # If the profile has the attribute services
        if typeof $(profile).attr('services') != typeof undefined and $(profile).attr('services') != false
          service_uids = $(profile).attr('services').split(',')
          if $.inArray(uid, service_uids) != -1
            profile_uid = $(profile).attr('uid')
            $(profile).remove()
            # Removing the profile's uid from the profiles widget
            p = $('#Profiles-' + arnum).attr('uid').split(',')
            p = $.grep(p, (value) ->
              value != profile_uid
            )
            i = undefined
            p_str = ''
            i = p.length - 1
            while i >= 0
              p_str = p_str + ',' + p[i]
              i--
            $('#Profiles-' + arnum).attr 'uid', p_str
            $('#Profiles-' + arnum).attr 'uid_check', p_str
            $('#Profiles-' + arnum + '_uid').val p_str
        return
      recalc_prices arnum
    return


  # dependencies ////////////////////////////////////////////////////////////

  ###
   deps_calc                  - the main routine for dependencies/dependants
   dependencies_add_confirm   - adding dependancies to the form/state: confirm
   dependancies_add_yes       - clicked yes
   dependencies_add_no        - clicked no
  ###

  deps_calc = (arnum, uids, skip_confirmation, initiator) ->
    ### Calculate dependants and dependencies.
    #
    # arnum - the column number.
    # uids - zero or more service UIDs to calculate
    # skip_confirmation - assume yes instead of confirmation dialog
    # initiator - the service or control that initiated this check.
    #             used for a more pretty dialog box header.
    ###

    jarn.i18n.loadCatalog 'bika'
    _ = window.jarn.i18n.MessageFactory('bika')
    Dep = undefined
    i = undefined
    cb = undefined
    dep_element = undefined
    lims = window.bika.lims
    dep_services = []
    # actionable services
    dep_titles = []
    # pretty titles
    n = 0
    while n < uids.length
      uid = uids[n]
      if uid == 'new'
        n++
        continue
      element = $('tr[uid=\'' + uids[n] + '\'] ' + 'td[class*=\'ar\\.' + arnum + '\'] ' + 'input[type=\'checkbox\']')
      initiator = $(element).parents('[title]').attr('title')
      # selecting a service; discover dependencies
      if $(element).prop('checked')
        Dependencies = lims.AnalysisService.Dependencies(uid)
        i = 0
        while i < Dependencies.length
          Dep = Dependencies[i]
          dep_element = $('tr[uid=\'' + Dep['Service_uid'] + '\'] ' + 'td[class*=\'ar\\.' + arnum + '\'] ' + 'input[type=\'checkbox\']')
          if !$(dep_element).prop('checked')
            dep_titles.push Dep['Service']
            dep_services.push Dep
          i++
        if dep_services.length > 0
          if skip_confirmation
            dependancies_add_yes arnum, dep_services
          else
            dependencies_add_confirm(initiator, dep_services, dep_titles).done((data) ->
              dependancies_add_yes arnum, dep_services
              return
            ).fail (data) ->
              dependencies_add_no arnum, uid
              return
      else
        Dependants = lims.AnalysisService.Dependants(uid)
        i = 0
        while i < Dependants.length
          Dep = Dependants[i]
          dep_element = $('tr[uid=\'' + Dep['Service_uid'] + '\'] ' + 'td[class*=\'ar\\.' + arnum + '\'] ' + 'input[type=\'checkbox\']')
          if $(dep_element).prop('checked')
            dep_titles.push Dep['Service']
            dep_services.push Dep
          i++
        if dep_services.length > 0
          if skip_confirmation
            dependants_remove_yes arnum, dep_services
          else
            dependants_remove_confirm(initiator, dep_services, dep_titles).done((data) ->
              dependants_remove_yes arnum, dep_services
              return
            ).fail (data) ->
              dependants_remove_no arnum, uid
              return
      n++
    return


  dependants_remove_confirm = (initiator, dep_services, dep_titles) ->
    d = $.Deferred()
    $('body').append '<div id=\'messagebox\' style=\'display:none\' title=\'' + _('Service dependencies') + '\'>' + _('<p>The following services depend on ${service}, and will be unselected if you continue:</p><br/><p>${deps}</p><br/><p>Do you want to remove these selections now?</p>',
      service: initiator
      deps: dep_titles.join('<br/>')) + '</div>'
    $('#messagebox').dialog
      width: 450
      resizable: false
      closeOnEscape: false
      buttons:
        yes: ->
          d.resolve()
          $(this).dialog 'close'
          $('#messagebox').remove()
          return
        no: ->
          d.reject()
          $(this).dialog 'close'
          $('#messagebox').remove()
          return
    d.promise()


  dependants_remove_yes = (arnum, dep_services) ->
    i = 0
    while i < dep_services.length
      Dep = dep_services[i]
      uid = Dep['Service_uid']
      analysis_cb_uncheck arnum, uid
      i += 1
    _partition_indicators_set arnum
    return


  dependants_remove_no = (arnum, uid) ->
    analysis_cb_check arnum, uid
    _partition_indicators_set arnum
    return


  dependencies_add_confirm = (initiator_title, dep_services, dep_titles) ->
    ###
     uid - this is the analysisservice checkbox which was selected
     dep_services and dep_titles are the calculated dependencies
     initiator_title is the dialog title, this could be a service but also could
     be "Dry Matter" or some other name
    ###

    d = $.Deferred()
    html = '<div id=\'messagebox\' style=\'display:none\' title=\'' + _('Service dependencies') + '\'>'
    html = html + _('<p>${service} requires the following services to be selected:</p>' + '<br/><p>${deps}</p><br/><p>Do you want to apply these selections now?</p>',
      service: initiator_title
      deps: dep_titles.join('<br/>'))
    html = html + '</div>'
    $('body').append html
    $('#messagebox').dialog
      width: 450
      resizable: false
      closeOnEscape: false
      buttons:
        yes: ->
          d.resolve()
          $(this).dialog 'close'
          $('#messagebox').remove()
          return
        no: ->
          d.reject()
          $(this).dialog 'close'
          $('#messagebox').remove()
          return
    d.promise()


  dependancies_add_yes = (arnum, dep_services) ->
    ###
     Adding required analyses to this AR - Clicked "yes" to confirmation,
     or if confirmation dialog is skipped, this function is called directly.
    ###

    i = 0
    while i < dep_services.length
      Dep = dep_services[i]
      uid = Dep['Service_uid']
      dep_cb = $('tr[uid=\'' + uid + '\'] ' + 'td[class*=\'ar\\.' + arnum + '\'] ' + 'input[type=\'checkbox\']')
      if dep_cb.length > 0
        # row already exists
        if $(dep_cb).prop('checked')
          # skip if checked already
          i++
          continue
      else
        # create new row for all services we may need
        singleservice_duplicate Dep['Service_uid'], Dep['Service'], Dep['Keyword'], Dep['Price'], Dep['VAT']
      # finally check the service
      analysis_cb_check arnum, uid
      i++
    recalc_prices arnum
    _partition_indicators_set arnum
    return


  dependencies_add_no = (arnum, uid) ->
    ###
     Adding required analyses to this AR - clicked "no" to confirmation.
     This is just responsible for un-checking the service that was
     used to invoke this routine.
    ###

    element = $('tr[uid=\'' + uid + '\'] td[class*=\'ar\\.' + arnum + '\'] input[type=\'checkbox\']')
    if $(element).prop('checked')
      analysis_cb_uncheck arnum, uid
    _partition_indicators_set arnum
    return

  # form/UI functions: not related to specific fields ///////////////////////

  ### partnrs_calc calls the ajax url, and sets the state variable
  # partition_indicators_set calls partnrs_calc, and modifies the form.
  # partition_indicators_from_template set state partnrs from template
  # _partition_indicators_set actually does the form/ui work
  ###

  partnrs_calc = (arnum) ->
    ### Configure the state partition data with an ajax call
    # - calls to /calculate_partitions json url
    #
    ###

    d = $.Deferred()
    arnum = parseInt(arnum, 10)
    #// Template columns are not calculated - they are set manually.
    #// I have disabled this behaviour, to simplify the action of adding
    #// a single extra service to a Template column.
    #var te = $("tr[fieldname='Template'] td[arnum='" + arnum + "'] input[type='text']")
    #if (!$(te).val()) {
    #  d.resolve()
    #  return d.promise()
    #}
    st_uid = bika.lims.ar_add.state[arnum]['SampleType']
    service_uids = bika.lims.ar_add.state[arnum]['Analyses']
    # if no sampletype or no selected analyses:  remove partition markers
    if !st_uid or !service_uids
      d.resolve()
      return d.promise()
    request_data =
      services: service_uids.join(',')
      sampletype: st_uid
      _authenticator: $('input[name=\'_authenticator\']').val()
    # HEALTH-593 Partitions not submitted when creating AR
    # Disable the Add button until the partitions get calculated
    $('input[name="save_button"]').prop 'disabled', true
    window.jsonapi_cache = window.jsonapi_cache or {}
    cacheKey = $.param(request_data)
    if typeof window.jsonapi_cache[cacheKey] == 'undefined'
      $.ajax
        type: 'POST'
        dataType: 'json'
        url: window.portal_url + '/@@API/calculate_partitions'
        data: request_data
        success: (data) ->
          # Check if calculation succeeded
          if data.success == false
            bika.lims.log 'Error while calculating partitions: ' + data.message
          else
            window.jsonapi_cache[cacheKey] = data
            bika.lims.ar_add.state[arnum]['Partitions'] = data['parts']
          # HEALTH-593 Partitions not submitted when creating AR
          # Enable the Add button, partitions calculated
          $('input[name="save_button"]').prop 'disabled', false
          d.resolve()
          return
    else
      data = window.jsonapi_cache[cacheKey]
      bika.lims.ar_add.state[arnum]['Partitions'] = data['parts']
      # HEALTH-593 Partitions not submitted when creating AR
      # Enable the Add button, partitions calculated
      $('input[name="save_button"]').prop 'disabled', false
      d.resolve()
    d.promise()


  _partition_indicators_set = (arnum) ->
    # partnrs_calc (or some template!) should have already set the state.
    # Be aware here, that some services may not have part info, eg if a
    # template was applied with only partial info.  This function literally
    # uses "part-1" as a default
    arnum = parseInt(arnum, 10)
    parts = bika.lims.ar_add.state[arnum]['Partitions']
    if !parts
      return
    # I'll be looping all the checkboxes currently visible in this column
    checkboxes = $('tr[uid] td[class*=\'ar\\.' + arnum + '\'] ' + 'input[type=\'checkbox\'][name!=\'uids:list\']')
    # the UIDs of services which are not found in any partition should
    # be indicated.  anyway there should be some default applied, or
    # selection allowed.
    n = 0
    while n < checkboxes.length
      cb = checkboxes[n]
      span = $(cb).parents('[class*=\'ar\\.\']').find('.partnr')
      uid = $(cb).parents('[uid]').attr('uid')
      if $(cb).prop('checked')
        # this service is selected - locate a partnr for it
        partnr = 1
        p = 0
        while p < parts.length
          if parts[p]['services'].indexOf(uid) > -1
            if parts[p]['part_id']
              partnr = parts[p]['part_id'].split('-')[1]
            else
              partnr = p + 1
            break
          p++
        # print the new partnr into the span
        $(span).html partnr
      else
        # this service is not selected - remove the partnr
        $(span).html '&nbsp;'
      n++
    return


  partition_indicators_set = (arnum, skip_calculation) ->
    ### Calculate and Set partition indicators
    # set skip_calculation if the state variable already contains
    # calculated partitions (eg, when setting template)
    ###

    if skip_calculation
      _partition_indicators_set arnum
    else
      partnrs_calc(arnum).done ->
        _partition_indicators_set arnum
        return
    return

  recalc_prices = (arnum) ->
    console.debug "recalc_prices::arnum=#{arnum}"
    ardiscount_amount = 0.00
    arservices_price = 0.00
    # Getting all checked analysis services
    checked = $('tr[uid] td[class*=\'ar\\.' + arnum + '\'] input[type=\'checkbox\']:checked')
    member_discount = parseFloat($('#bika_setup').attr('MemberDiscount'))
    member_discount_applies = $.parseJSON($('#bika_setup').attr('MemberDiscountApplies'))

    profiles = $('div#Profiles-' + arnum + '-listing').children()
    arprofiles_price = 0.00
    arprofiles_vat_amount = 0.00
    arservice_vat_amount = 0.00
    services_from_priced_profile = []

    ### ANALYSIS PROFILES PRICE ###

    $.each profiles, (i, profile) ->
      # Getting available analysis profiles' prices and vat amounts
      if $(profile).attr('useprice') == 'true'
        profile_service_uids = $(profile).attr('services').split(',')
        profile_price = parseFloat($(profile).attr('price'))
        profile_vat = parseFloat($(profile).attr('VATAmount'))
        arprofiles_price += profile_price
        arprofiles_vat_amount += profile_vat
        # We don't want repeated analysis services because of two profiles with the same analysis, so we'll
        # check if the analysis is contained in the array before adding it
        $.each profile_service_uids, (i, el) ->
          if $.inArray(el, services_from_priced_profile) == -1
            services_from_priced_profile.push el
          return
      return

    ### ANALYSIS SERVICES PRICE###

    # Compute the price for each checked analysis service. We have to look for profiles which have set
    # "use price" attribute and sum the profile's price to the total instead of using their individual
    # services prices
    i = 0
    while i < checked.length
      cb = checked[i]
      # For some browsers, checkbox `attr` is undefined; for others, its false. Check for both.
      if $(cb).prop('checked') and !$(cb).prop('disabled') and typeof $(cb).prop('disabled') != 'undefined' and services_from_priced_profile.indexOf($(cb).attr('uid')) < 0
        service_price = parseFloat($(cb).parents('[price]').attr('price'))
        service_vat_amount = parseFloat($(cb).parents('[vat_percentage]').attr('vat_percentage'))
        arservice_vat_amount += service_price * service_vat_amount / 100
        arservices_price += service_price
      i++
    base_price = arservices_price + arprofiles_price

    # Calculate the member discount if it applies
    if member_discount and member_discount_applies
      console.debug "Member discount applies with #{member_discount}%"
      ardiscount_amount = base_price * member_discount / 100

    subtotal = base_price - ardiscount_amount
    vat_amount = arprofiles_vat_amount + arservice_vat_amount
    total = subtotal + vat_amount
    $('td[arnum=\'' + arnum + '\'] span.price.discount').html ardiscount_amount.toFixed(2)
    $('td[arnum=\'' + arnum + '\'] span.price.subtotal').html subtotal.toFixed(2)
    $('td[arnum=\'' + arnum + '\'] span.price.vat').html vat_amount.toFixed(2)
    $('td[arnum=\'' + arnum + '\'] span.price.total').html total.toFixed(2)
    return


  set_state_from_form_values = ->
    nr_ars = parseInt($('#ar_count').val(), 10)
    # Values flagged as 'hidden' in the AT schema widget visibility
    # attribute, are flagged so that we know they contain only "default"
    # values, and do not constitute data entry.
    $.each $('td[arnum][hidden] input[type="hidden"]'), (i, e) ->
      arnum = get_arnum(e)
      fieldname = $(e).parents('[fieldname]').attr('fieldname')
      value = if $(e).attr('uid') then $(e).attr('uid') else $(e).val()
      if fieldname
        state_set arnum, fieldname, value
        # To avoid confusion with other hidden inputs, these have a
        # 'hidden' attribute on their td.
        state_set arnum, fieldname + '_hidden', true
      return
    # other field values which are handled similarly:
    $.each $('td[arnum] input[type="text"], td[arnum] input.referencewidget').not('[class^="rejectionwidget-input"]'), (i, e) ->
      arnum = $(e).parents('[arnum]').attr('arnum')
      fieldname = $(e).parents('[fieldname]').attr('fieldname')
      #var value = $(e).attr("uid")
      #if (value){
      #    state_set(arnum, fieldname, value)
      #}
      value = if $(e).attr('uid') then $(e).attr('uid') else $(e).val()
      state_set arnum, fieldname, value
      return
    # checkboxes inside ar_add_widget table.
    $.each $('[ar_add_ar_widget] input[type="checkbox"]').not('[class^="rejectionwidget-checkbox"]'), (i, e) ->
      arnum = get_arnum(e)
      fieldname = $(e).parents('[fieldname]').attr('fieldname')
      value = $(e).prop('checked')
      state_set arnum, fieldname, value
      return
    # select widget values
    $.each $('td[arnum] select').not('[class^="rejectionwidget-multiselect"]'), (i, e) ->
      arnum = get_arnum(e)
      fieldname = $(e).parents('[fieldname]').attr('fieldname')
      value = $(e).val()
      state_set arnum, fieldname, value
      return
    # services
    uid = undefined
    arnum = undefined
    services = undefined
    arnum = 0
    while arnum < nr_ars
      services = []
      # list of UIDs
      cblist = $('.service_selector td[class*="ar\\.' + arnum + '"] input[type="checkbox"]').filter(':checked')
      $.each cblist, (i, e) ->
        uid = $(e).parents('[uid]').attr('uid')
        services.push uid
        return
      state_set arnum, 'Analyses', services
      arnum++
    # ResultsRange + specifications from UI
    rr = undefined
    specs = undefined
    min = undefined
    max = undefined
    error = undefined
    arnum = 0
    while arnum < nr_ars
      rr = bika.lims.ar_add.state[arnum]['ResultsRange']
      if rr != undefined
        specs = hashes_to_hash(rr, 'uid')
        $.each $('.service_selector td[class*=\'ar\\.' + arnum + '\'] .after'), (i, e) ->
          uid = $(e).parents('[uid]').attr('uid')
          keyword = $(e).parents('[keyword]').attr('keyword')
          if uid != 'new' and uid != undefined
            min = $(e).find('.min')
            max = $(e).find('.max')
            error = $(e).find('.error')
            if specs[uid] == undefined
              specs[uid] =
                'min': $(min).val()
                'max': $(max).val()
                'error': $(error).val()
                'uid': uid
                'keyword': keyword
            else
              specs[uid].min = if $(min) then $(min).val() else specs[uid].min
              specs[uid].max = if $(max) then $(max).val() else specs[uid].max
              specs[uid].error = if $(error) then $(error).val() else specs[uid].error
          return
        state_set arnum, 'ResultsRange', hash_to_hashes(specs)
      arnum++
    return


  form_submit = ->
    $('[name=\'save_button\']').click (event) ->
      event.preventDefault()
      set_state_from_form_values()
      request_data =
        _authenticator: $('input[name=\'_authenticator\']').val()
        state: $.toJSON(bika.lims.ar_add.state)
      $.ajax
        type: 'POST'
        dataType: 'json'
        url: window.location.href.split('/portal_factory')[0] + '/analysisrequest_submit'
        data: request_data
        success: (data) ->
          `var destination`

          ###
          # data contains the following useful keys:
          # - errors: any errors which prevented the AR from being created
          #   these are displayed immediately and no further ation is taken
          # - destination: the URL to which we should redirect on success.
          #   This includes GET params for printing labels, so that we do not
          #   have to care about this here.
          ###

          if data['errors']
            msg = ''
            for error of data.errors
              x = error.split('.')
              e = undefined
              if x.length == 2
                e = x[1] + ', AR ' + +x[0] + ': '
              else if x.length == 1
                e = x[0] + ': '
              else
                e = ''
              msg = msg + e + data.errors[error] + '<br/>'
            window.bika.lims.portalMessage msg
            window.scroll 0, 0
          else if data['stickers']
            destination = window.location.href.split('/portal_factory')[0]
            ars = data['stickers']
            stickertemplate = data['stickertemplate']
            q = '/sticker?autoprint=1&template=' + stickertemplate + '&items=' + ars.join(',')
            window.location.replace destination + q
          else
            destination = window.location.href.split('/portal_factory')[0]
            window.location.replace destination
          return
      return
    return


  fix_table_layout = ->
    'use strict'
    # Apply to header column
    headcolwidth = $('table.analysisrequest.add tr:first th').width()
    headcolwidth += $('table.analysisrequest.add tr:first td:first').width()
    $('table tr th input[id*="_toggle_cols"]').closest('th').css 'width', 24
    $('table tr th[id="foldercontents-Title-column"]').css 'width', headcolwidth
    $('table tr[id^="folder-contents-item-"] td[class*="Title"]').css 'width', headcolwidth
    # Apply to Analyses columns
    arcolswidth = $('table.analysisrequest td[arnum]').width()
    $('table tr th[id^="foldercontents-ar."]').css
      'width': arcolswidth
      'text-align': 'center'
    $('table tr[id^="folder-contents-item-"] td[class*="ar"]').css
      'width': arcolswidth
      'text-align': 'center'
    return

  'use strict'
  that = this

  that.load = ->
    console.debug "*** LOADING AR FORM CONTROLLER ***"

    # disable browser autocomplete
    $('input[type=text]').prop 'autocomplete', 'off'

    # load-time form configuration
    form_init()

    #// Handy for the debugging; alerts when a certain selector's 'value' is changed
    # var selector = input[id*='0_uid']
    # Object.defineProperty(document.querySelector(selector), 'value', {
    #  set: function (value) {
    #      if(!value || value.length < 2)
    #      {
    #          debugger;
    #      }
    #  }
    #})

    ###
     The state variable is fully populated when the form is submitted,
     but in many cases it must be updated on the fly, to allow the form
     to change behaviour based on some selection.  To help with this,
     there are some generic state-setting handlers below, but these must
     be augmented with specific handlers for difficult cases.
    ###

    checkbox_change()
    referencewidget_change()
    rejectionwidget_change()
    select_element_change()
    textinput_change()
    textarea_change()
    copybutton_selected()
    client_selected()
    contact_selected()
    cc_contacts_deletebtn_click()
    spec_field_entry()
    spec_selected()
    samplepoint_selected()
    sampletype_selected()
    profile_selected()
    profile_unset_trigger()
    template_selected()
    drymatter_selected()
    sample_selected()
    singleservice_dropdown_init()
    singleservice_deletebtn_click()
    analysis_cb_click()
    category_header_clicked()
    #      sample_selected()
    form_submit()
    fix_table_layout()
    from_sampling_round()
    return


  ###
  # Exposes the filter_combogrid method publicly.
  # Accessible through window.bika.lims.AnalysisRequestAddByCol.filter_combogrid
  ###

  that.filter_combogrid = (element, filterkey, filtervalue, querytype) ->
    filter_combogrid element, filterkey, filtervalue, querytype
    return

  return
