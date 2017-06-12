### Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../ -c bika.lims.bikalisting.coffee
###

###*
# Controller class for Bika Listing Table view
###

window.BikaListingTableView = ->
  that = this
  # Entry-point method for AnalysisServiceEditView

  show_more_clicked = ->
    $('a.bika_listing_show_more').click (e) ->
      e.preventDefault()
      formid = $(this).attr('data-form-id')
      pagesize = parseInt($(this).attr('data-pagesize'))
      url = $(this).attr('data-ajax-url')
      limit_from = parseInt($(this).attr('data-limitfrom'))
      url = url.replace('_limit_from=', '_olf=')
      url += '&' + formid + '_limit_from=' + limit_from
      # $('#'+formid+' a.bika_listing_show_more').fadeOut();
      tbody = $('table.bika-listing-table[form_id="' + formid + '"] tbody.item-listing-tbody')
      # The results must be filtered?
      filter_options = []
      filters1 = $('.bika_listing_filter_bar input[name][value!=""]')
      filters2 = $('.bika_listing_filter_bar select option:selected[value!=""]')
      filters = $.merge(filters1, filters2)
      $(filters).each (e) ->
        opt = [
          $(this).attr('name')
          $(this).val()
        ]
        filter_options.push opt
        return
      filterbar = {}
      if filter_options.length > 0
        filterbar.bika_listing_filter_bar = $.toJSON(filter_options)
      $.post(url, filterbar).done((data) ->
        try
          # We must surround <tr> inside valid TABLE tags before extracting
          rows = $('<html><table>' + data + '</table></html>').find('tr')
          # Then we can simply append the rows to existing TBODY.
          $(tbody).append rows
          # Increase limit_from so that next iteration uses correct start point
          $('#' + formid + ' a.bika_listing_show_more').attr 'data-limitfrom', limit_from + pagesize
        catch e
          $('#' + formid + ' a.bika_listing_show_more').hide()
          console.log e
        return
      ).fail(->
        $('#' + formid + ' a.bika_listing_show_more').hide()
        console.log 'bika_listing_show_more failed'
        return
      ).always ->
        numitems = $('table.bika-listing-table[form_id="' + formid + '"] tbody.item-listing-tbody tr').length
        $('#' + formid + ' span.number-items').html numitems
        if numitems % pagesize != 0
          $('#' + formid + ' a.bika_listing_show_more').hide()
        return
      return
    return

  column_header_clicked = ->
    # Click column header - set or modify sort order.
    $('th.sortable').live 'click', ->
      form = $(this).parents('form')
      form_id = $(form).attr('id')
      column_id = @id.split('-')[1]
      column_index = $(this).parent().children('th').index(this)
      sort_on_selector = '[name=' + form_id + '_sort_on]'
      sort_on = $(sort_on_selector).val()
      sort_order_selector = '[name=' + form_id + '_sort_order]'
      sort_order = $(sort_order_selector).val()
      # if this column_id is the current sort
      if sort_on == column_id
        # then we reverse sort order
        if sort_order == 'descending'
          sort_order = 'ascending'
        else
          sort_order = 'descending'
      else
        sort_on = column_id
        sort_order = 'ascending'
      # reset these values in the form (ajax sort uses them)
      $(sort_on_selector).val sort_on
      $(sort_order_selector).val sort_order
      # request new table content
      stored_form_action = $(form).attr('action')
      $(form).attr 'action', window.location.href
      $(form).append '<input type=\'hidden\' name=\'table_only\' value=\'' + form_id + '\'>'
      options =
        target: $(this).parents('table')
        replaceTarget: true
        data: form.formToArray()
      form.ajaxSubmit options
      $('[name=\'table_only\']').remove()
      $(form).attr 'action', stored_form_action
      return
    return

  show_or_hide_transition_buttons = ->
    # Get all transitions for all items, into all_valid_transitions
    all_valid_transitions = []
    # array of arrays
    checked = $('input[name=\'uids:list\']:checked')
    if checked.length == 0
      $('input[workflow_transition]').hide()
      return
    i = 0
    while i < checked.length
      all_valid_transitions.push $(checked[i]).attr('data-valid_transitions').split(',')
      i++
    # intersect values from all arrays in all_valid_transitions
    valid_transitions = all_valid_transitions.shift().filter((v) ->
      all_valid_transitions.every (a) ->
        a.indexOf(v) != -1
    )
    # Hide all buttons except the ones listed as valid.
    $.each $('input[workflow_transition=\'yes\']'), (i, e) ->
      if $.inArray($(e).attr('transition'), valid_transitions) == -1
        $(e).hide()
      else
        $(e).show()
      return
    # if any checkboxes are checked, then all "custom" action buttons are shown.
    # This means any action button that is not linked to a workflow transition.
    if checked.length > 0
      $('input[workflow_transition=\'no\']').show()
    else
      $('input[workflow_transition=\'no\']').hide()
    return

  select_one_clicked = ->
    $('input[name=\'uids:list\']').live 'click', ->
      show_or_hide_transition_buttons()
      return
    return

  select_all_clicked = ->
    # select all (on this page at least)
    $('input[id*=\'select_all\']').live 'click', ->
      checkboxes = $(this).parents('form').find('[id*=\'_cb_\']')
      if $(this).prop('checked')
        $(checkboxes).filter('input:checkbox:not(:checked)').prop 'checked', true
      else
        $(checkboxes).filter('input:checkbox:checked').prop 'checked', false
      show_or_hide_transition_buttons()
      return
    return

  manage_select_all_state = ->
    # modify select_all checkbox when regular checkboxes are modified
    $('input[id*=\'_cb_\']').live 'change', ->
      form_id = $(this).parents('form').attr('id')
      all_selected = true
      $.each $('input[id^=\'' + form_id + '_cb_\']'), (i, v) ->
        if !$(v).prop('checked')
          all_selected = false
        return
      if all_selected
        $('#' + form_id + '_select_all').prop 'checked', true
      else
        $('#' + form_id + '_select_all').prop 'checked', false
      return
    return

  listing_string_input_keypress = ->
    $('.listing_string_entry,.listing_select_entry').live 'keypress', (event) ->
      # Prevent automatic submissions of manage_results forms when enter is pressed
      enter = 13
      if event.which == enter
        event.preventDefault()
      # check the item's checkbox
      form_id = $(this).parents('form').attr('id')
      uid = $(this).attr('uid')
      if !$('#' + form_id + '_cb_' + uid).prop('checked')
        $('#' + form_id + '_cb_' + uid).prop 'checked', true
      return
    return

  listing_string_select_changed = ->
    # always select checkbox when selectable listing item is changed
    $('.listing_select_entry').live 'change', ->
      form_id = $(this).parents('form').attr('id')
      uid = $(this).attr('uid')
      # check the item's checkbox
      if !$('#' + form_id + '_cb_' + uid).prop('checked')
        $('#' + form_id + '_cb_' + uid).prop 'checked', true
      return
    return

  pagesize_change = ->
    # pagesize
    $('select.pagesize').live 'change', ->
      form = $(this).parents('form')
      form_id = $(form).attr('id')
      pagesize = $(this).val()
      new_query = $.query.set(form_id + '_pagesize', pagesize).set(form_id + '_pagenumber', 1).toString()
      window.location = window.location.href.split('?')[0] + new_query
      return
    return

  category_header_clicked = ->
    # expand/collapse categorised rows
    $('.bika-listing-table th.collapsed').live 'click', ->
      if !$(this).hasClass('ignore_bikalisting_default_handler')
        category_header_expand_handler this
      return
    $('.bika-listing-table th.expanded').live 'click', ->
      if !$(this).hasClass('ignore_bikalisting_default_handler')
        # After ajax_category expansion, collapse and expand work as they would normally.
        $(this).parent().nextAll('tr[cat=\'' + $(this).attr('cat') + '\']').toggle()
        if $(this).hasClass('expanded')
          # Set collapsed class on TR
          $(this).removeClass('expanded').addClass 'collapsed'
        else if $(this).hasClass('collapsed')
          # Set expanded class on TR
          $(this).removeClass('collapsed').addClass 'expanded'
      return
    return

  category_header_expand_handler = (element) ->
    # element is the category header TH.
    # duplicated in bika.lims.analysisrequest.add_by_col.js
    def = $.Deferred()
    # with form_id allow multiple ajax-categorised tables in a page
    form_id = $(element).parents('[form_id]').attr('form_id')
    cat_title = $(element).attr('cat')
    # URL can be provided by bika_listing classes, with ajax_category_url attribute.
    url = if $('input[name=\'ajax_categories_url\']').length > 0 then $('input[name=\'ajax_categories_url\']').val() else window.location.href.split('?')[0]
    # We will replace this element with downloaded items:
    placeholder = $('tr[data-ajax_category=\'' + cat_title + '\']')
    # If it's already been expanded, ignore
    if $(element).hasClass('expanded')
      def.resolve()
      return def.promise()
    # If ajax_categories are enabled, we need to go request items now.
    ajax_categories_enabled = $('input[name=\'ajax_categories\']')
    if ajax_categories_enabled.length > 0 and placeholder.length > 0
      options = {}
      options['ajax_category_expand'] = 1
      options['cat'] = cat_title
      options['form_id'] = form_id
      url = if $('input[name=\'ajax_categories_url\']').length > 0 then $('input[name=\'ajax_categories_url\']').val() else url
      if $('.review_state_selector a.selected').length > 0
        # review_state must be kept the same after items are loaded
        # (TODO does this work?)
        options['review_state'] = $('.review_state_selector a.selected')[0].id
      $.ajax(
        url: url
        data: options).done (data) ->
        # The same as: LIMS-1970 Analyses from AR Add form not displayed properly
        rows = $('<table>' + data + '</table>').find('tr')
        $('[form_id=\'' + form_id + '\'] tr[data-ajax_category=\'' + cat_title + '\']').replaceWith rows
        $(element).removeClass('collapsed').addClass 'expanded'
        def.resolve()
        return
    else
      # When ajax_categories are disabled, all cat items exist as TR elements:
      $(element).parent().nextAll('tr[cat=\'' + $(element).attr('cat') + '\']').toggle true
      $(element).removeClass('collapsed').addClass 'expanded'
      def.resolve()
    # Set expanded class on TR
    def.promise()

  filter_search_keypress = ->
    # pressing enter on filter search will trigger
    # a click on the search link.
    $('.filter-search-input').live 'keypress', (event) ->
      enter = 13
      if event.which == enter
        $('.filter-search-button').click()
        return false
      return
    return

  filter_search_button_click = ->
    # trap the Clear search / Search buttons
    $('.filter-search-button').live 'click', (event) ->
      form = $(this).parents('form')
      form_id = $(form).attr('id')
      stored_form_action = $(form).attr('action')
      $(form).attr 'action', window.location.href
      $(form).append '<input type=\'hidden\' name=\'table_only\' value=\'' + form_id + '\'>'
      options =
        target: $(this).parents('table')
        replaceTarget: true
        data: form.formToArray()
      form.ajaxSubmit options
      $('[name="table_only"]').remove()
      $(form).attr 'action', stored_form_action
      false
    return

  workflow_action_button_click = ->
    # Workflow Action button was clicked.
    $('.workflow_action_button').live 'click', (event) ->
      # The submit buttons would like to put the translated action title
      # into the request.  Insert the real action name here to prevent the
      # WorkflowAction handler from having to look it up (painful/slow).
      form = $(this).parents('form')
      form_id = $(form).attr('id')
      $(form).append '<input type=\'hidden\' name=\'workflow_action_id\' value=\'' + $(this).attr('transition') + '\'>'
      # This submit_transition cheat fixes a bug where hitting submit caused
      # form to be posted before ajax calculation is returned
      if @id == 'submit_transition'
        focus = $('.ajax_calculate_focus')
        if focus.length > 0
          e = $(focus[0])
          if $(e).attr('focus_value') == $(e).val()
            # value did not change - transparent blur handler.
            $(e).removeAttr 'focus_value'
            $(e).removeClass 'ajax_calculate_focus'
          else
            # The calcs.js code is now responsible for submitting
            # this form when the calculation ajax is complete
            $(e).parents('form').attr 'submit_after_calculation', 1
            event.preventDefault()
      # If a custom_actions action with a URL is clicked
      # the form will be submitted there
      if $(this).attr('url') != ''
        form = $(this).parents('form')
        $(form).attr 'action', $(this).attr('url')
        $(form).submit()
      return
    return

  column_toggle_context_menu = ->
    # show / hide columns - the right-click pop-up
    $('th[id^="foldercontents-"]').live 'contextmenu', (event) ->
      event.preventDefault()
      form_id = $(this).parents('form').attr('id')
      portal_url = window.portal_url
      toggle_cols = $('#' + form_id + '_toggle_cols').val()
      if toggle_cols == '' or toggle_cols == undefined or toggle_cols == null
        return false
      sorted_toggle_cols = []
      $.each $.parseJSON(toggle_cols), (col_id, v) ->
        v['id'] = col_id
        sorted_toggle_cols.push v
        return
      sorted_toggle_cols.sort (a, b) ->
        titleA = a['title'].toLowerCase()
        titleB = b['title'].toLowerCase()
        if titleA < titleB
          return -1
        if titleA > titleB
          return 1
        0
      txt = '<div class="tooltip"><table class="contextmenu" cellpadding="0" cellspacing="0">'
      txt = txt + '<tr><th colspan=\'2\'>' + _('Display columns') + '</th></tr>'
      i = 0
      while i < sorted_toggle_cols.length
        col = sorted_toggle_cols[i]
        col_id = col['id']
        col_title = _(col['title'])
        enabled = $('#foldercontents-' + col_id + '-column')
        if enabled.length > 0
          txt = txt + '<tr class=\'enabled\' col_id=\'' + col_id + '\' form_id=\'' + form_id + '\'>'
          txt = txt + '<td>'
          txt = txt + '<img style=\'height:1em;\' src=\'' + portal_url + '/++resource++bika.lims.images/ok.png\'/>'
          txt = txt + '</td>'
          txt = txt + '<td>' + col_title + '</td></tr>'
        else
          txt = txt + '<tr col_id=\'' + col_id + '\' form_id=\'' + form_id + '\'>'
          txt = txt + '<td>&nbsp;</td>'
          txt = txt + '<td>' + col_title + '</td></tr>'
        i++
      txt = txt + '<tr col_id=\'' + _('All') + '\' form_id=\'' + form_id + '\'>'
      txt = txt + '<td style=\'border-top:1px solid #ddd\'>&nbsp;</td>'
      txt = txt + '<td style=\'border-top:1px solid #ddd\'>' + _('All') + '</td></tr>'
      txt = txt + '<tr col_id=\'' + _('Default') + '\' form_id=\'' + form_id + '\'>'
      txt = txt + '<td>&nbsp;</td>'
      txt = txt + '<td>' + _('Default') + '</td></tr>'
      txt = txt + '</table></div>'
      $(txt).appendTo 'body'
      positionTooltip event
      false
    return

  column_toggle_context_menu_selection = ->
    # show / hide columns - the action when a column is clicked in the menu
    $('.contextmenu tr').live 'click', (event) ->
      form_id = $(this).attr('form_id')
      form = $('form#' + form_id)
      col_id = $(this).attr('col_id')
      col_title = $(this).text()
      enabled = $(this).hasClass('enabled')
      cookie = readCookie('toggle_cols')
      cookie = $.parseJSON(cookie)
      cookie_key = $(form[0].portal_type).val() + form_id
      if cookie == null or cookie == undefined
        cookie = {}
      if col_id == _('Default')
        # Remove entry from existing cookie if there is one
        delete cookie[cookie_key]
        createCookie 'toggle_cols', $.toJSON(cookie), 365
      else if col_id == _('All')
        # add all possible columns
        toggle_cols = []
        $.each $.parseJSON($('#' + form_id + '_toggle_cols').val()), (i, v) ->
          toggle_cols.push i
          return
        cookie[cookie_key] = toggle_cols
        createCookie 'toggle_cols', $.toJSON(cookie), 365
      else
        toggle_cols = cookie[cookie_key]
        if toggle_cols == null or toggle_cols == undefined
          # this cookie key not yet defined
          toggle_cols = []
          $.each $.parseJSON($('#' + form_id + '_toggle_cols').val()), (i, v) ->
            if !(col_id == i and enabled) and v['toggle']
              toggle_cols.push i
            return
        else
          # modify existing cookie
          if enabled
            toggle_cols.splice toggle_cols.indexOf(col_id), 1
          else
            toggle_cols.push col_id
        cookie[cookie_key] = toggle_cols
        createCookie 'toggle_cols', $.toJSON(cookie), 365
      $(form).attr 'action', window.location.href
      $('.tooltip').remove()
      form.submit()
      false
    return

  positionTooltip = (event) ->
    tPosX = event.pageX - 5
    tPosY = event.pageY - 5
    $('div.tooltip').css
      'border': '1px solid #fff'
      'border-radius': '.25em'
      'background-color': '#fff'
      'position': 'absolute'
      'top': tPosY
      'left': tPosX
    return

  autosave = ->

    ###
    This function looks for the column defined as 'autosave' and if
    its value is true, the result of this input will be saved after each
    change via ajax.
    ###

    $('select.autosave, input.autosave').not('[type="hidden"]').each (i) ->
      # Save select fields
      $(this).change ->
        pointer = this
        build_typical_save_request pointer
        return
      return
    return

  build_typical_save_request = (pointer) ->

    ###*
    # Build an array with the data to be saved for the typical data fields.
    # @pointer is the object which has been modified and we want to save its new data.
    ###

    fieldvalue = undefined
    fieldname = undefined
    requestdata = {}
    uid = undefined
    tr = undefined
    fieldvalue = $(pointer).val()
    fieldname = $(pointer).attr('field')
    tr = $(pointer).closest('tr')
    uid = $(pointer).attr('uid')
    requestdata[fieldname] = fieldvalue
    requestdata['obj_uid'] = uid
    save_elements requestdata, tr
    return

  save_elements = (requestdata, tr) ->

    ###*
    # Given a dict with a fieldname and a fieldvalue, save this data via ajax petition.
    # @requestdata should has the format  {fieldname=fieldvalue, uid=xxxx} ->  { ReportDryMatter=false, uid=xxx}.
    ###

    url = window.location.href.replace('/base_view', '')
    # Staff for the notification
    name = $(tr).attr('title')
    anch = '<a href=\'' + url + '\'>' + name + '</a>'
    $.ajax(
      type: 'POST'
      url: window.portal_url + '/@@API/update'
      data: requestdata).done((data) ->
      #success alert
      if data != null and data['success'] == true
        bika.lims.SiteView.notificationPanel anch + ': ' + name + ' updated successfully', 'succeed'
      else
        bika.lims.SiteView.notificationPanel 'Error while updating ' + name + ' for ' + anch, 'error'
        msg = '[bika.lims.analysisrequest.js] Error while updating ' + name + ' for ' + ar
        console.warn msg
        window.bika.lims.error msg
      return
    ).fail ->
      #error
      bika.lims.SiteView.notificationPanel 'Error while updating ' + name + ' for ' + anch, 'error'
      msg = '[bika.lims.analysisrequest.js] Error while updating ' + name + ' for ' + ar
      console.warn msg
      window.bika.lims.error msg
      return
    return

  that.load = ->
    column_header_clicked()
    select_one_clicked()
    select_all_clicked()
    manage_select_all_state()
    listing_string_input_keypress()
    listing_string_select_changed()
    pagesize_change()
    category_header_clicked()
    filter_search_keypress()
    filter_search_button_click()
    workflow_action_button_click()
    column_toggle_context_menu()
    column_toggle_context_menu_selection()
    show_more_clicked()
    autosave()
    $('*').click ->
      if $('.tooltip').length > 0
        $('.tooltip').remove()
      return
    return

  return

# ---
# generated by js2coffee 2.2.0
