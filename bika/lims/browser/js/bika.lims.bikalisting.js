
/* Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../ -c bika.lims.bikalisting.coffee
 */


/**
 * Controller class for Bika Listing Table view
 */

(function() {
  window.BikaListingTableView = function() {
    var autosave, build_typical_save_request, category_header_clicked, category_header_expand_handler, column_header_clicked, column_toggle_context_menu, column_toggle_context_menu_selection, filter_search_button_click, filter_search_keypress, listing_string_input_keypress, listing_string_select_changed, manage_select_all_state, pagesize_change, positionTooltip, save_elements, select_all_clicked, select_one_clicked, show_more_clicked, show_or_hide_transition_buttons, that, workflow_action_button_click;
    that = this;
    show_more_clicked = function() {
      $('a.bika_listing_show_more').click(function(e) {
        var filter_options, filterbar, filters, filters1, filters2, formid, limit_from, pagesize, tbody, url;
        e.preventDefault();
        formid = $(this).attr('data-form-id');
        pagesize = parseInt($(this).attr('data-pagesize'));
        url = $(this).attr('data-ajax-url');
        limit_from = parseInt($(this).attr('data-limitfrom'));
        url = url.replace('_limit_from=', '_olf=');
        url += '&' + formid + '_limit_from=' + limit_from;
        tbody = $('table.bika-listing-table[form_id="' + formid + '"] tbody.item-listing-tbody');
        filter_options = [];
        filters1 = $('.bika_listing_filter_bar input[name][value!=""]');
        filters2 = $('.bika_listing_filter_bar select option:selected[value!=""]');
        filters = $.merge(filters1, filters2);
        $(filters).each(function(e) {
          var opt;
          opt = [$(this).attr('name'), $(this).val()];
          filter_options.push(opt);
        });
        filterbar = {};
        if (filter_options.length > 0) {
          filterbar.bika_listing_filter_bar = $.toJSON(filter_options);
        }
        $.post(url, filterbar).done(function(data) {
          var rows;
          try {
            rows = $('<html><table>' + data + '</table></html>').find('tr');
            $(tbody).append(rows);
            $('#' + formid + ' a.bika_listing_show_more').attr('data-limitfrom', limit_from + pagesize);
          } catch (error) {
            e = error;
            $('#' + formid + ' a.bika_listing_show_more').hide();
            console.log(e);
          }
        }).fail(function() {
          $('#' + formid + ' a.bika_listing_show_more').hide();
          console.log('bika_listing_show_more failed');
        }).always(function() {
          var numitems;
          numitems = $('table.bika-listing-table[form_id="' + formid + '"] tbody.item-listing-tbody tr').length;
          $('#' + formid + ' span.number-items').html(numitems);
          if (numitems % pagesize !== 0) {
            $('#' + formid + ' a.bika_listing_show_more').hide();
          }
        });
      });
    };
    column_header_clicked = function() {
      $('th.sortable').live('click', function() {
        var column_id, column_index, form, form_id, options, sort_on, sort_on_selector, sort_order, sort_order_selector, stored_form_action;
        form = $(this).parents('form');
        form_id = $(form).attr('id');
        column_id = this.id.split('-')[1];
        column_index = $(this).parent().children('th').index(this);
        sort_on_selector = '[name=' + form_id + '_sort_on]';
        sort_on = $(sort_on_selector).val();
        sort_order_selector = '[name=' + form_id + '_sort_order]';
        sort_order = $(sort_order_selector).val();
        if (sort_on === column_id) {
          if (sort_order === 'descending') {
            sort_order = 'ascending';
          } else {
            sort_order = 'descending';
          }
        } else {
          sort_on = column_id;
          sort_order = 'ascending';
        }
        $(sort_on_selector).val(sort_on);
        $(sort_order_selector).val(sort_order);
        stored_form_action = $(form).attr('action');
        $(form).attr('action', window.location.href);
        $(form).append('<input type=\'hidden\' name=\'table_only\' value=\'' + form_id + '\'>');
        options = {
          target: $(this).parents('table'),
          replaceTarget: true,
          data: form.formToArray()
        };
        form.ajaxSubmit(options);
        $('[name=\'table_only\']').remove();
        $(form).attr('action', stored_form_action);
      });
    };
    show_or_hide_transition_buttons = function() {
      var all_valid_transitions, checked, i, valid_transitions;
      all_valid_transitions = [];
      checked = $('input[name=\'uids:list\']:checked');
      if (checked.length === 0) {
        $('input[workflow_transition]').hide();
        return;
      }
      i = 0;
      while (i < checked.length) {
        all_valid_transitions.push($(checked[i]).attr('data-valid_transitions').split(','));
        i++;
      }
      valid_transitions = all_valid_transitions.shift().filter(function(v) {
        return all_valid_transitions.every(function(a) {
          return a.indexOf(v) !== -1;
        });
      });
      $.each($('input[workflow_transition=\'yes\']'), function(i, e) {
        if ($.inArray($(e).attr('transition'), valid_transitions) === -1) {
          $(e).hide();
        } else {
          $(e).show();
        }
      });
      if (checked.length > 0) {
        $('input[workflow_transition=\'no\']').show();
      } else {
        $('input[workflow_transition=\'no\']').hide();
      }
    };
    select_one_clicked = function() {
      $('input[name=\'uids:list\']').live('click', function() {
        show_or_hide_transition_buttons();
      });
    };
    select_all_clicked = function() {
      $('input[id*=\'select_all\']').live('click', function() {
        var checkboxes;
        checkboxes = $(this).parents('form').find('[id*=\'_cb_\']');
        if ($(this).prop('checked')) {
          $(checkboxes).filter('input:checkbox:not(:checked)').prop('checked', true);
        } else {
          $(checkboxes).filter('input:checkbox:checked').prop('checked', false);
        }
        show_or_hide_transition_buttons();
      });
    };
    manage_select_all_state = function() {
      $('input[id*=\'_cb_\']').live('change', function() {
        var all_selected, form_id;
        form_id = $(this).parents('form').attr('id');
        all_selected = true;
        $.each($('input[id^=\'' + form_id + '_cb_\']'), function(i, v) {
          if (!$(v).prop('checked')) {
            all_selected = false;
          }
        });
        if (all_selected) {
          $('#' + form_id + '_select_all').prop('checked', true);
        } else {
          $('#' + form_id + '_select_all').prop('checked', false);
        }
      });
    };
    listing_string_input_keypress = function() {
      $('.listing_string_entry,.listing_select_entry').live('keypress', function(event) {
        var enter, form_id, uid;
        enter = 13;
        if (event.which === enter) {
          event.preventDefault();
        }
        form_id = $(this).parents('form').attr('id');
        uid = $(this).attr('uid');
        if (!$('#' + form_id + '_cb_' + uid).prop('checked')) {
          $('#' + form_id + '_cb_' + uid).prop('checked', true);
        }
      });
    };
    listing_string_select_changed = function() {
      $('.listing_select_entry').live('change', function() {
        var form_id, uid;
        form_id = $(this).parents('form').attr('id');
        uid = $(this).attr('uid');
        if (!$('#' + form_id + '_cb_' + uid).prop('checked')) {
          $('#' + form_id + '_cb_' + uid).prop('checked', true);
        }
      });
    };
    pagesize_change = function() {
      $('select.pagesize').live('change', function() {
        var form, form_id, new_query, pagesize;
        form = $(this).parents('form');
        form_id = $(form).attr('id');
        pagesize = $(this).val();
        new_query = $.query.set(form_id + '_pagesize', pagesize).set(form_id + '_pagenumber', 1).toString();
        window.location = window.location.href.split('?')[0] + new_query;
      });
    };
    category_header_clicked = function() {
      $('.bika-listing-table th.collapsed').live('click', function() {
        if (!$(this).hasClass('ignore_bikalisting_default_handler')) {
          category_header_expand_handler(this);
        }
      });
      $('.bika-listing-table th.expanded').live('click', function() {
        if (!$(this).hasClass('ignore_bikalisting_default_handler')) {
          $(this).parent().nextAll('tr[cat=\'' + $(this).attr('cat') + '\']').toggle();
          if ($(this).hasClass('expanded')) {
            $(this).removeClass('expanded').addClass('collapsed');
          } else if ($(this).hasClass('collapsed')) {
            $(this).removeClass('collapsed').addClass('expanded');
          }
        }
      });
    };
    category_header_expand_handler = function(element) {
      var ajax_categories_enabled, cat_title, def, form_id, options, placeholder, url;
      def = $.Deferred();
      form_id = $(element).parents('[form_id]').attr('form_id');
      cat_title = $(element).attr('cat');
      url = $('input[name=\'ajax_categories_url\']').length > 0 ? $('input[name=\'ajax_categories_url\']').val() : window.location.href.split('?')[0];
      placeholder = $('tr[data-ajax_category=\'' + cat_title + '\']');
      if ($(element).hasClass('expanded')) {
        def.resolve();
        return def.promise();
      }
      ajax_categories_enabled = $('input[name=\'ajax_categories\']');
      if (ajax_categories_enabled.length > 0 && placeholder.length > 0) {
        options = {};
        options['ajax_category_expand'] = 1;
        options['cat'] = cat_title;
        options['form_id'] = form_id;
        url = $('input[name=\'ajax_categories_url\']').length > 0 ? $('input[name=\'ajax_categories_url\']').val() : url;
        if ($('.review_state_selector a.selected').length > 0) {
          options['review_state'] = $('.review_state_selector a.selected')[0].id;
        }
        $.ajax({
          url: url,
          data: options
        }).done(function(data) {
          var rows;
          rows = $('<table>' + data + '</table>').find('tr');
          $('[form_id=\'' + form_id + '\'] tr[data-ajax_category=\'' + cat_title + '\']').replaceWith(rows);
          $(element).removeClass('collapsed').addClass('expanded');
          def.resolve();
        });
      } else {
        $(element).parent().nextAll('tr[cat=\'' + $(element).attr('cat') + '\']').toggle(true);
        $(element).removeClass('collapsed').addClass('expanded');
        def.resolve();
      }
      return def.promise();
    };
    filter_search_keypress = function() {
      $('.filter-search-input').live('keypress', function(event) {
        var enter;
        enter = 13;
        if (event.which === enter) {
          $('.filter-search-button').click();
          return false;
        }
      });
    };
    filter_search_button_click = function() {
      $('.filter-search-button').live('click', function(event) {
        var form, form_id, options, stored_form_action;
        form = $(this).parents('form');
        form_id = $(form).attr('id');
        stored_form_action = $(form).attr('action');
        $(form).attr('action', window.location.href);
        $(form).append('<input type=\'hidden\' name=\'table_only\' value=\'' + form_id + '\'>');
        options = {
          target: $(this).parents('table'),
          replaceTarget: true,
          data: form.formToArray()
        };
        form.ajaxSubmit(options);
        $('[name="table_only"]').remove();
        $(form).attr('action', stored_form_action);
        return false;
      });
    };
    workflow_action_button_click = function() {
      $('.workflow_action_button').live('click', function(event) {
        var e, focus, form, form_id;
        form = $(this).parents('form');
        form_id = $(form).attr('id');
        $(form).append('<input type=\'hidden\' name=\'workflow_action_id\' value=\'' + $(this).attr('transition') + '\'>');
        if (this.id === 'submit_transition') {
          focus = $('.ajax_calculate_focus');
          if (focus.length > 0) {
            e = $(focus[0]);
            if ($(e).attr('focus_value') === $(e).val()) {
              $(e).removeAttr('focus_value');
              $(e).removeClass('ajax_calculate_focus');
            } else {
              $(e).parents('form').attr('submit_after_calculation', 1);
              event.preventDefault();
            }
          }
        }
        if ($(this).attr('url') !== '') {
          form = $(this).parents('form');
          $(form).attr('action', $(this).attr('url'));
          $(form).submit();
        }
      });
    };
    column_toggle_context_menu = function() {
      $('th[id^="foldercontents-"]').live('contextmenu', function(event) {
        var col, col_id, col_title, enabled, form_id, i, portal_url, sorted_toggle_cols, toggle_cols, txt;
        event.preventDefault();
        form_id = $(this).parents('form').attr('id');
        portal_url = window.portal_url;
        toggle_cols = $('#' + form_id + '_toggle_cols').val();
        if (toggle_cols === '' || toggle_cols === void 0 || toggle_cols === null) {
          return false;
        }
        sorted_toggle_cols = [];
        $.each($.parseJSON(toggle_cols), function(col_id, v) {
          v['id'] = col_id;
          sorted_toggle_cols.push(v);
        });
        sorted_toggle_cols.sort(function(a, b) {
          var titleA, titleB;
          titleA = a['title'].toLowerCase();
          titleB = b['title'].toLowerCase();
          if (titleA < titleB) {
            return -1;
          }
          if (titleA > titleB) {
            return 1;
          }
          return 0;
        });
        txt = '<div class="tooltip"><table class="contextmenu" cellpadding="0" cellspacing="0">';
        txt = txt + '<tr><th colspan=\'2\'>' + _('Display columns') + '</th></tr>';
        i = 0;
        while (i < sorted_toggle_cols.length) {
          col = sorted_toggle_cols[i];
          col_id = col['id'];
          col_title = _(col['title']);
          enabled = $('#foldercontents-' + col_id + '-column');
          if (enabled.length > 0) {
            txt = txt + '<tr class=\'enabled\' col_id=\'' + col_id + '\' form_id=\'' + form_id + '\'>';
            txt = txt + '<td>';
            txt = txt + '<img style=\'height:1em;\' src=\'' + portal_url + '/++resource++bika.lims.images/ok.png\'/>';
            txt = txt + '</td>';
            txt = txt + '<td>' + col_title + '</td></tr>';
          } else {
            txt = txt + '<tr col_id=\'' + col_id + '\' form_id=\'' + form_id + '\'>';
            txt = txt + '<td>&nbsp;</td>';
            txt = txt + '<td>' + col_title + '</td></tr>';
          }
          i++;
        }
        txt = txt + '<tr col_id=\'' + _('All') + '\' form_id=\'' + form_id + '\'>';
        txt = txt + '<td style=\'border-top:1px solid #ddd\'>&nbsp;</td>';
        txt = txt + '<td style=\'border-top:1px solid #ddd\'>' + _('All') + '</td></tr>';
        txt = txt + '<tr col_id=\'' + _('Default') + '\' form_id=\'' + form_id + '\'>';
        txt = txt + '<td>&nbsp;</td>';
        txt = txt + '<td>' + _('Default') + '</td></tr>';
        txt = txt + '</table></div>';
        $(txt).appendTo('body');
        positionTooltip(event);
        return false;
      });
    };
    column_toggle_context_menu_selection = function() {
      $('.contextmenu tr').live('click', function(event) {
        var col_id, col_title, cookie, cookie_key, enabled, form, form_id, toggle_cols;
        form_id = $(this).attr('form_id');
        form = $('form#' + form_id);
        col_id = $(this).attr('col_id');
        col_title = $(this).text();
        enabled = $(this).hasClass('enabled');
        cookie = readCookie('toggle_cols');
        cookie = $.parseJSON(cookie);
        cookie_key = $(form[0].portal_type).val() + form_id;
        if (cookie === null || cookie === void 0) {
          cookie = {};
        }
        if (col_id === _('Default')) {
          delete cookie[cookie_key];
          createCookie('toggle_cols', $.toJSON(cookie), 365);
        } else if (col_id === _('All')) {
          toggle_cols = [];
          $.each($.parseJSON($('#' + form_id + '_toggle_cols').val()), function(i, v) {
            toggle_cols.push(i);
          });
          cookie[cookie_key] = toggle_cols;
          createCookie('toggle_cols', $.toJSON(cookie), 365);
        } else {
          toggle_cols = cookie[cookie_key];
          if (toggle_cols === null || toggle_cols === void 0) {
            toggle_cols = [];
            $.each($.parseJSON($('#' + form_id + '_toggle_cols').val()), function(i, v) {
              if (!(col_id === i && enabled) && v['toggle']) {
                toggle_cols.push(i);
              }
            });
          } else {
            if (enabled) {
              toggle_cols.splice(toggle_cols.indexOf(col_id), 1);
            } else {
              toggle_cols.push(col_id);
            }
          }
          cookie[cookie_key] = toggle_cols;
          createCookie('toggle_cols', $.toJSON(cookie), 365);
        }
        $(form).attr('action', window.location.href);
        $('.tooltip').remove();
        form.submit();
        return false;
      });
    };
    positionTooltip = function(event) {
      var tPosX, tPosY;
      tPosX = event.pageX - 5;
      tPosY = event.pageY - 5;
      $('div.tooltip').css({
        'border': '1px solid #fff',
        'border-radius': '.25em',
        'background-color': '#fff',
        'position': 'absolute',
        'top': tPosY,
        'left': tPosX
      });
    };
    autosave = function() {

      /*
      This function looks for the column defined as 'autosave' and if
      its value is true, the result of this input will be saved after each
      change via ajax.
       */
      $('select.autosave, input.autosave').not('[type="hidden"]').each(function(i) {
        $(this).change(function() {
          var pointer;
          pointer = this;
          build_typical_save_request(pointer);
        });
      });
    };
    build_typical_save_request = function(pointer) {

      /**
       * Build an array with the data to be saved for the typical data fields.
       * @pointer is the object which has been modified and we want to save its new data.
       */
      var fieldname, fieldvalue, requestdata, tr, uid;
      fieldvalue = void 0;
      fieldname = void 0;
      requestdata = {};
      uid = void 0;
      tr = void 0;
      fieldvalue = $(pointer).val();
      fieldname = $(pointer).attr('field');
      tr = $(pointer).closest('tr');
      uid = $(pointer).attr('uid');
      requestdata[fieldname] = fieldvalue;
      requestdata['obj_uid'] = uid;
      save_elements(requestdata, tr);
    };
    save_elements = function(requestdata, tr) {

      /**
       * Given a dict with a fieldname and a fieldvalue, save this data via ajax petition.
       * @requestdata should has the format  {fieldname=fieldvalue, uid=xxxx} ->  { ReportDryMatter=false, uid=xxx}.
       */
      var anch, name, url;
      url = window.location.href.replace('/base_view', '');
      name = $(tr).attr('title');
      anch = '<a href=\'' + url + '\'>' + name + '</a>';
      $.ajax({
        type: 'POST',
        url: window.portal_url + '/@@API/update',
        data: requestdata
      }).done(function(data) {
        var msg;
        if (data !== null && data['success'] === true) {
          bika.lims.SiteView.notificationPanel(anch + ': ' + name + ' updated successfully', 'succeed');
        } else {
          bika.lims.SiteView.notificationPanel('Error while updating ' + name + ' for ' + anch, 'error');
          msg = '[bika.lims.analysisrequest.js] Error while updating ' + name + ' for ' + ar;
          console.warn(msg);
          window.bika.lims.error(msg);
        }
      }).fail(function() {
        var msg;
        bika.lims.SiteView.notificationPanel('Error while updating ' + name + ' for ' + anch, 'error');
        msg = '[bika.lims.analysisrequest.js] Error while updating ' + name + ' for ' + ar;
        console.warn(msg);
        window.bika.lims.error(msg);
      });
    };
    that.load = function() {
      column_header_clicked();
      select_one_clicked();
      select_all_clicked();
      manage_select_all_state();
      listing_string_input_keypress();
      listing_string_select_changed();
      pagesize_change();
      category_header_clicked();
      filter_search_keypress();
      filter_search_button_click();
      workflow_action_button_click();
      column_toggle_context_menu();
      column_toggle_context_menu_selection();
      show_more_clicked();
      autosave();
      $('*').click(function() {
        if ($('.tooltip').length > 0) {
          $('.tooltip').remove();
        }
      });
    };
  };

}).call(this);
