
/* Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../ -c bika.lims.analysisrequest.add_by_col.coffee
 */


/* Controller class for AnalysisRequestAddView - column layout.
 *
 * The form elements are not submitted.  Instead, their values are inserted
 * into bika.lims.ar_add.state, and this variable is submitted as a json
 * string.
 *
 *
 * Regarding checkboxes: JQuery recommends using .prop() instead of .attr(),
 * but selenium/xpath cannot discover the state of such inputs.  I use
 * .attr("checked",true) and .removeAttr("checked") to set their values,
 * although .prop("checked") is still the correct way to check state of
 * a particular element from JS.
 */

(function() {
  window.AnalysisRequestAddByCol = function() {

    /* form_init - load time form config
     * state_set - should be used when setting fields in the state var
     * filter_combogrid - filter an existing dropdown (referencewidget)
     * filter_by_client - Grab the client UID and filter all applicable dropdowns
     * get_arnum(element) - convenience to compensate for different form layouts.
     */
    var _partition_indicators_set, analysis_cb_after_change, analysis_cb_check, analysis_cb_click, analysis_cb_uncheck, category_header_clicked, category_header_expand_handler, cc_contacts_deletebtn_click, cc_contacts_set, checkbox_change, checkbox_change_handler, client_selected, composite_selected, contact_selected, copybutton_selected, dependancies_add_yes, dependants_remove_confirm, dependants_remove_no, dependants_remove_yes, dependencies_add_confirm, dependencies_add_no, deps_calc, destroy, drymatter_selected, drymatter_set, drymatter_unset, expand_services_bika_listing, expand_services_singleservice, filter_by_client, filter_combogrid, fix_table_layout, form_init, form_submit, from_sampling_round, get_arnum, hash_to_hashes, hashes_to_hash, partition_indicators_set, partnrs_calc, profile_selected, profile_set, profile_unset_trigger, profiles_unset_all, recalc_prices, referencewidget_change, referencewidget_change_handler, rejectionwidget_change, rejectionwidget_change_handler, sample_selected, sample_set, samplepoint_selected, samplepoint_set, sampletype_selected, sampletype_set, select_element_change, select_element_change_handler, set_spec_from_sampletype, set_state_from_form_values, setupSamplingRoundInfo, singleservice_deletebtn_click, singleservice_dropdown_init, singleservice_duplicate, spec_field_entry, spec_filter_on_sampletype, spec_selected, specification_apply, specification_refetch, state_analyses_push, state_analyses_remove, state_set, template_selected, template_set, template_unset, textarea_change, textarea_change_handler, textinput_change, textinput_change_handler, that, uncheck_all_services, unset_profile_analysis_services;
    form_init = function() {

      /* load-time form configuration
       *
       * - Create empty state var
       * - fix generated elements
       * - clear existing values (on page reload)
       * - filter fields based on the selected Client
       */
      var arnum, element, elements, i, nr_ars, request_data, uid;
      $(".blurrable").removeClass("blurrable");
      bika.lims.ar_add = {};
      bika.lims.ar_add.state = {};
      nr_ars = parseInt($('input[id="ar_count"]').val(), 10);
      console.debug("Initializing for " + nr_ars + " ARs");
      arnum = 0;
      while (arnum < nr_ars) {
        bika.lims.ar_add.state[arnum] = {
          'Analyses': []
        };
        arnum++;
      }
      elements = $('input[type!=\'hidden\']').not('[disabled]');
      i = elements.length - 1;
      while (i >= 0) {
        element = elements[i];
        $(element).removeAttr('required');
        i--;
      }
      $.each($('[id^=\'archetypes-fieldname\']'), function(i, div) {
        var e, fieldname;
        arnum = $(div).parents('[arnum]').attr('arnum');
        fieldname = $(div).parents('[fieldname]').attr('fieldname');
        e = void 0;
        console.debug("Renaming field " + fieldname + " for AR " + arnum);
        if ($(div).hasClass('ArchetypesSelectionWidget')) {
          e = $(div).find('select')[0];
          $(e).attr('id', fieldname + '-' + arnum);
          $(e).attr('name', fieldname + '-' + arnum);
        } else if ($(div).hasClass('ArchetypesReferenceWidget')) {
          e = $(div).find('[type="text"]')[0];
          $(e).attr('id', $(e).attr('id') + '-' + arnum);
          $(e).attr('name', $(e).attr('name') + '-' + arnum);
          e = $(div).find('[id$="_uid"]')[0];
          $(e).attr('id', fieldname + '-' + arnum + '_uid');
          $(e).attr('name', fieldname + '-' + arnum + '_uid');
          e = $(div).find('[id$="-listing"]');
          if (e.length > 0) {
            $(e).attr('id', fieldname + '-' + arnum + '-listing');
          }
        } else if ($(div).hasClass('ArchetypesStringWidget') || $(div).hasClass('ArchetypesDateTimeWidget')) {
          e = $(div).find('[type="text"]')[0];
          $(e).attr('id', $(e).attr('id') + '-' + arnum);
          $(e).attr('name', $(e).attr('name') + '-' + arnum);
        } else if ($(div).hasClass('ArchetypesBooleanWidget')) {
          e = $(div).find('[type="checkbox"]')[0];
          $(e).attr('id', $(e).attr('id') + '-' + arnum);
          $(e).attr('name', $(e).attr('name') + '-' + arnum + ':boolean');
          e = $(div).find('[type="hidden"]')[0];
          $(e).attr('name', $(e).attr('name') + '-' + arnum + ':boolean:default');
        } else if ($(div).hasClass('RejectionWidget')) {
          e = $(div).find('input[id="RejectionReasons.checkbox"]')[0];
          $(e).attr('id', fieldname + '.checkbox-' + arnum);
          $(e).attr('name', fieldname + '.checkbox-' + arnum);
          e = $(div).find('select[id="RejectionReasons.multiselection"]')[0];
          $(e).attr('id', fieldname + '.multiselection-' + arnum);
          $(e).attr('name', fieldname + '.multiselection-' + arnum);
          e = $(div).find('input[id="RejectionReasons.checkbox.other"]')[0];
          $(e).attr('id', fieldname + '.checkbox.other-' + arnum);
          $(e).attr('name', fieldname + '.checkbox.other-' + arnum);
          e = $(div).find('input[id="RejectionReasons.textfield.other"]')[0];
          $(e).attr('id', fieldname + '.textfield.other-' + arnum);
          $(e).attr('name', fieldname + '.textfield.other-' + arnum);
        } else if ($(div).hasClass('ArchetypesTextAreaWidget')) {
          e = $(div).find('textarea')[0];
          $(e).attr('id', fieldname + '-' + arnum);
          $(e).attr('name', fieldname + '-' + arnum);
        } else if ($(div).hasClass('ArchetypesDecimalWidget')) {
          e = $(div).find('input')[0];
          $(e).attr('id', fieldname + '-' + arnum);
          $(e).attr('name', fieldname + '-' + arnum);
        } else {
          console.warn("Could not rename " + fieldname + " for AR " + arnum + "!");
        }
        $(div).attr('id', 'archetypes-fieldname-' + fieldname + '-' + arnum);
      });
      $('#singleservice').val('');
      $('#singleservice').attr('uid', 'new');
      $('#singleservice').attr('title', '');
      $('#singleservice').parents('[uid]').attr('uid', 'new');
      $('#singleservice').parents('[keyword]').attr('keyword', '');
      $('#singleservice').parents('[title]').attr('title', '');
      $('input[type=\'checkbox\']').removeAttr('checked');
      $('.min,.max,.error').val('');
      setTimeout((function() {
        nr_ars = parseInt($('#ar_count').val(), 10);
        arnum = 0;
        while (arnum < nr_ars) {
          filter_by_client(arnum);
          arnum++;
        }
      }), 250);

      /** If client only has one contect, and the analysis request comes from
        * a client, then Auto-complete first Contact field.
        * If client only has one contect, and the analysis request comes from
        * a batch, then Auto-complete all Contact field.
       */
      uid = $($('tr[fieldname=\'Client\'] input')[0]).attr('uid');
      request_data = {
        catalog_name: 'portal_catalog',
        portal_type: 'Contact',
        getParentUID: uid,
        inactive_state: 'active'
      };
      window.bika.lims.jsonapi_read(request_data, function(data) {

        /** If the analysis request comes from a client
         * window.location.pathname.split('batches') should not be splitted
         * in 2 parts
         */
        var contact;
        if (data.success && data.total_objects === 1 && window.location.pathname.split('batches').length < 2) {
          contact = data.objects[0];
          $('input#Contact-0').attr('uid', contact['UID']).val(contact['Title']).attr('uid_check', contact['UID']).attr('val_check', contact['UID']);
          $('#Contact-0_uid').val(contact['UID']);
          state_set(0, 'Contact', contact['UID']);
          cc_contacts_set(0);
        } else if (data.success && data.total_objects === 1 && window.location.pathname.split('batches').length === 2) {
          nr_ars = parseInt($('#ar_count').val(), 10);
          contact = data.objects[0];
          $('input[id^="Contact-"]').attr('uid', contact['UID']).val(contact['Title']).attr('uid_check', contact['UID']).attr('val_check', contact['UID']);
          $('[id^="Contact-"][id$="_uid"]').val(contact['UID']);
          i = 0;
          while (i < nr_ars) {
            state_set(i, 'Contact', contact['UID']);
            cc_contacts_set(i);
            i++;
          }
        }
      });
    };
    state_set = function(arnum, fieldname, value) {
      var arnum_i;
      console.info("state_set::" + fieldname + " -> " + value);

      /* Use this function to set values in the state variable.
       */
      arnum_i = parseInt(arnum, 10);
      if (fieldname && value !== void 0) {
        bika.lims.ar_add.state[arnum_i][fieldname] = value;
      }
    };
    from_sampling_round = function() {
      var i, sPageURL, sParameterName, sURLVariables, samplinground_UID;
      sPageURL = decodeURIComponent(window.location.search.substring(1));
      sURLVariables = sPageURL.split('&');
      sParameterName = void 0;
      i = 0;
      while (i < sURLVariables.length) {
        sParameterName = sURLVariables[i].split('=');
        if (sParameterName[0] === 'samplinground') {
          samplinground_UID = sParameterName[1];
          setupSamplingRoundInfo(samplinground_UID);
        }
        i++;
      }
    };
    setupSamplingRoundInfo = function(samplinground_UID) {

      /**
       * This function sets up the sampling round information such as the sampling round to use and the
       * different analysis request templates needed.
       * :samplinground_uid: a string with the sampling round uid
       */
      var request_data;
      request_data = {
        catalog_name: 'portal_catalog',
        portal_type: 'SamplingRound',
        UID: samplinground_UID,
        include_fields: ['Title', 'UID', 'analysisRequestTemplates', 'samplingRoundSamplingDate']
      };
      window.bika.lims.jsonapi_read(request_data, function(data) {
        var ar_templates, i, sampleTypes, spec, sr, to_disable;
        if (data.objects.length > 0) {
          spec = data.objects[0];
          sr = $('input[id^="SamplingRound-"]');
          sr.attr('uid', spec['UID']).val(spec['Title']).attr('uid_check', spec['UID']).attr('val_check', spec['Title']).attr('disabled', 'disabled');
          $('[id^="SamplingRound-"][id$="_uid"]').val(spec['UID']);
          ar_templates = $('input[id^="Template-"]:visible');
          ar_templates.each(function(index, element) {
            $(element).attr('uid', spec['analysisRequestTemplates'][index][1]).val(spec['analysisRequestTemplates'][index][0]).attr('uid_check', spec['analysisRequestTemplates'][index][1]).attr('val_check', spec['analysisRequestTemplates'][index][1]).attr('disabled', 'disabled');
            $('input#Template-' + index + '_uid').val(spec['analysisRequestTemplates'][index][1]);
            template_set(index);
          });
          $('input[id^="SamplingDate-"]:visible').val(spec['samplingRoundSamplingDate']);
          to_disable = ['Specification', 'SamplePoint', 'ReportDryMatter', 'Sample', 'Batch', 'SubGroup', 'SamplingDate', 'Composite', 'Profiles', 'DefaultContainerType', 'AdHoc'];
          i = 0;
          while (to_disable.length > i) {
            $('tr[fieldname="' + to_disable[i] + '"]').hide();
            i++;
          }
          sampleTypes = $('input[id^="SampleType-"]');
          sampleTypes.each(function(index, element) {
            if ($(element).attr('uid')) {
              $(element).attr('disabled', 'disabled');
            }
          });
          $('table.add tfoot').hide();
          $('th.collapsed').hide();
          setTimeout((function() {
            $('input[selector^="bika_analysisservices"]').attr('disabled', true);
            $('input[selector^="ar."][type="checkbox"]').attr('disabled', true);
            $('input.min, input.max, input.error').attr('disabled', true);
          }), 1000);
        }
      });
    };
    filter_combogrid = function(element, filterkey, filtervalue, querytype) {

      /* Apply or modify a query filter for a reference widget.
       *
       *  This will set the options, then re-create the combogrid widget
       *  with the new filter key/value.
       *
       *  querytype can be 'base_query' or 'search_query'.
       */
      var options, query;
      if (!$(element).is(':visible')) {
        return;
      }
      if (!querytype) {
        querytype = 'base_query';
      }
      query = $.parseJSON($(element).attr(querytype));
      query[filterkey] = filtervalue;
      $(element).attr(querytype, $.toJSON(query));
      options = $.parseJSON($(element).attr('combogrid_options'));
      options.url = window.location.href.split('/ar_add')[0] + '/' + options.url;
      options.url = options.url + '?_authenticator=' + $('input[name=\'_authenticator\']').val();
      options.url = options.url + '&catalog_name=' + $(element).attr('catalog_name');
      if (querytype === 'base_query') {
        options.url = options.url + '&base_query=' + $.toJSON(query);
        options.url = options.url + '&search_query=' + $(element).attr('search_query');
      } else {
        options.url = options.url + '&base_query=' + $(element).attr('base_query');
        options.url = options.url + '&search_query=' + $.toJSON(query);
      }
      options.url = options.url + '&colModel=' + $.toJSON($.parseJSON($(element).attr('combogrid_options')).colModel);
      options.url = options.url + '&search_fields=' + $.toJSON($.parseJSON($(element).attr('combogrid_options'))['search_fields']);
      options.url = options.url + '&discard_empty=' + $.toJSON($.parseJSON($(element).attr('combogrid_options'))['discard_empty']);
      options.force_all = 'false';
      $(element).combogrid(options);
      $(element).attr('search_query', '{}');
    };
    filter_by_client = function(arnum) {

      /***
       * Filter all Reference fields that reference Client items
       *
       * Some reference fields can select Lab or Client items.  In these
       * cases, the 'getParentUID' or 'getClientUID' index is used
       * to filter against Lab and Client folders.
       */
      var element, uid, uids;
      element = void 0;
      uids = void 0;
      uid = $($('tr[fieldname=\'Client\'] td[arnum=\'' + arnum + '\'] input')[0]).attr('uid');
      element = $('tr[fieldname=Contact] td[arnum=' + arnum + '] input')[0];
      filter_combogrid(element, 'getParentUID', uid);
      element = $('tr[fieldname=CCContact] td[arnum=' + arnum + '] input')[0];
      filter_combogrid(element, 'getParentUID', uid);
      element = $('tr[fieldname=InvoiceContact] td[arnum=' + arnum + '] input')[0];
      filter_combogrid(element, 'getParentUID', uid);
      uids = [uid, $('#bika_setup').attr('bika_samplepoints_uid')];
      element = $('tr[fieldname=SamplePoint] td[arnum=' + arnum + '] input')[0];
      filter_combogrid(element, 'getClientUID', uids);
      uids = [uid, $('#bika_setup').attr('bika_artemplates_uid')];
      element = $('tr[fieldname=Template] td[arnum=' + arnum + '] input')[0];
      filter_combogrid(element, 'getClientUID', uids);
      uids = [uid, $('#bika_setup').attr('bika_analysisprofiles_uid')];
      element = $('tr[fieldname=Profiles] td[arnum=' + arnum + '] input')[0];
      filter_combogrid(element, 'getClientUID', uids);
      uids = [uid, $('#bika_setup').attr('bika_analysisspecs_uid')];
      element = $('tr[fieldname=Specification] td[arnum=' + arnum + '] input')[0];
      filter_combogrid(element, 'getClientUID', uids);
    };
    hashes_to_hash = function(hashlist, key) {

      /* Convert a list of hashes to a hash, by one of their keys.
       *
       * This will return a single hash: the key that will be used must
       * of course exist in all hashes in hashlist.
       */
      var i, ret;
      ret = {};
      i = 0;
      while (i < hashlist.length) {
        ret[hashlist[i][key]] = hashlist[i];
        i++;
      }
      return ret;
    };
    hash_to_hashes = function(hash) {

      /* Convert a single hash into a list of hashes
       *
       * Basically, this just returns the keys, unmodified.
       */
      var ret;
      ret = [];
      $.each(hash, function(i, v) {
        ret.push(v);
      });
      return ret;
    };
    get_arnum = function(element) {
      var arnum, td;
      arnum = void 0;
      arnum = $(element).parents('[arnum]').attr('arnum');
      if (arnum) {
        return arnum;
      }
      td = $(element).parents('[class*=\'ar\\.\']');
      if (td.length > 0) {
        arnum = $(td).attr('class').split('ar.')[1].split()[0];
        if (arnum) {
          return arnum;
        }
      }
      console.error('No arnum found for element ' + element);
    };
    destroy = function(arr, val) {
      var i;
      i = 0;
      while (i < arr.length) {
        if (arr[i] === val) {
          arr.splice(i, 1);
        }
        i++;
      }
      return arr;
    };

    /*
     checkbox_change - applies to all except analysis services
     checkbox_change_handler
     referencewidget_change - applies to all except #singleservice
     referencewidget_change_handler
     select_element_change - select elements are a bit different
     select_element_change_handler
     textinput_change - all except referencwidget text elements
     textinput_change_handler
     */
    checkbox_change_handler = function(element) {
      var arnum, fieldname, value;
      arnum = get_arnum(element);
      fieldname = $(element).parents('[fieldname]').attr('fieldname');
      value = $(element).prop('checked');
      state_set(arnum, fieldname, value);
    };
    checkbox_change = function() {

      /* Generic state-setter for AR field checkboxes
       * The checkboxes used to select analyses are handled separately.
       */
      $('tr[fieldname] input[type="checkbox"]').not('[class^="rejectionwidget-checkbox"]').live('change copy', function() {
        checkbox_change_handler(this);
      }).each(function(i, e) {
        $(e).trigger('copy');
      });
    };
    referencewidget_change_handler = function(element, item) {
      var arnum, existing_values, fieldname, multiValued, uid_element, value;
      arnum = get_arnum(element);
      fieldname = $(element).parents('[fieldname]').attr('fieldname');
      multiValued = $(element).attr('multiValued') === '1';
      value = item.UID;
      if (multiValued) {
        uid_element = $(element).siblings('input[name*=\'_uid\']');
        existing_values = $(uid_element).val();
        if (existing_values.search(value) === -1) {
          value = existing_values + ',' + value;
        } else {
          value = existing_values;
        }
      }
      state_set(arnum, fieldname, value);
    };
    referencewidget_change = function() {

      /* Generic state-setter for AR field referencewidgets
       */
      $('tr[fieldname] input.referencewidget').live('selected', function(event, item) {
        referencewidget_change_handler(this, item);
      });
      $('tr[fieldname] input.referencewidget').live('copy', function(event) {
        var item;
        item = {
          UID: $(this).attr('uid')
        };
        referencewidget_change_handler(this, item);
      });
    };
    rejectionwidget_change_handler = function(element, item) {
      var arnum, ch_val, fieldname, i, multi_val, option, other_ch_val, other_val, rej_widget_state, selected_options, td;
      td = $(element).closest('td');
      ch_val = false;
      multi_val = [];
      other_ch_val = false;
      other_val = '';
      option = void 0;
      ch_val = $(td).find('.rejectionwidget-checkbox').prop('checked');
      if (ch_val) {
        selected_options = $(td).find('.rejectionwidget-multiselect').find('option');
        i = 0;
        while (selected_options.length > i) {
          option = selected_options[i];
          if (option.selected) {
            multi_val.push($(option).val());
          }
          i++;
        }
        other_ch_val = $(td).find('.rejectionwidget-checkbox-other').prop('checked');
        if (other_ch_val) {
          other_val = $(td).find('.rejectionwidget-input-other').val();
        }
      }
      rej_widget_state = {
        checkbox: ch_val,
        selected: multi_val,
        checkbox_other: other_ch_val,
        other: other_val
      };
      fieldname = $(element).parents('[fieldname]').attr('fieldname');
      arnum = get_arnum(element);
      state_set(arnum, fieldname, rej_widget_state);
    };
    rejectionwidget_change = function() {
      $('tr[fieldname] input.rejectionwidget-checkbox,' + 'tr[fieldname] select.rejectionwidget-multiselect,' + 'tr[fieldname] input.rejectionwidget-checkbox-other,' + 'tr[fieldname] input.rejectionwidget-input-other').live('change copy select', function(event, item) {
        rejectionwidget_change_handler(this, item);
      });
    };
    select_element_change_handler = function(element) {
      var arnum, fieldname, value;
      arnum = get_arnum(element);
      fieldname = $(element).parents('[fieldname]').attr('fieldname');
      value = $(element).val();
      state_set(arnum, fieldname, value);
    };
    select_element_change = function() {

      /* Generic state-setter for SELECT inputs
       */
      $('tr[fieldname] select').not('[class^="rejectionwidget-multiselect"]').live('change copy', function(event, item) {
        select_element_change_handler(this);
      }).each(function(i, e) {
        $(e).trigger('copy');
      });
    };
    textinput_change_handler = function(element) {
      var arnum, fieldname, value;
      arnum = get_arnum(element);
      fieldname = $(element).parents('[fieldname]').attr('fieldname');
      value = $(element).val();
      state_set(arnum, fieldname, value);
    };
    textinput_change = function() {

      /* Generic state-setter for TEXT inputs
       */
      return $('tr[fieldname] input[type="text"]').not('[class^="rejectionwidget-input"]').not('#singleservice').not('.referencewidget').live('change copy', function() {
        textinput_change_handler(this);
      }).each(function(i, e) {
        if ($(e).val()) {
          $(e).trigger('copy');
        }
      });
    };
    textarea_change_handler = function(element) {
      var arnum, fieldname, value;
      arnum = get_arnum(element);
      fieldname = $(element).parents('[fieldname]').attr('fieldname');
      value = $(element).val();
      state_set(arnum, fieldname, value);
    };
    textarea_change = function() {

      /* Generic state-setter for TEXTAREA fields
       */
      $('tr[fieldname] textarea').on('change copy', function() {
        textarea_change_handler(this);
      }).each(function(i, e) {
        if ($(e).val()) {
          $(e).trigger('copy');
        }
      });
      return;
    };
    copybutton_selected = function() {
      $('img.copybutton').live('click', function() {
        var arnum, checkbox, checkbox_other, e, fieldname, html, i, input, input_other, multi_div, multi_divX, nr_ars, option, select_options, selected, td, td1, tr, uid1, val1, value;
        nr_ars = parseInt($('input[id="ar_count"]').val(), 10);
        tr = $(this).parents('tr')[0];
        fieldname = $(tr).attr('fieldname');
        td1 = $(tr).find('td[arnum="0"]')[0];
        e = void 0;
        td = void 0;
        html = void 0;
        if ($(td1).find('.ArchetypesReferenceWidget').length > 0) {
          val1 = $(td1).find('input[type="text"]').val();
          uid1 = $(td1).find('input[type="text"]').attr('uid');
          multi_div = $('#' + fieldname + '-0-listing');
          arnum = 1;
          while (arnum < nr_ars) {
            td = $(tr).find('td[arnum="' + arnum + '"]')[0];
            e = $(td).find('input[type="text"]');
            $(e).val(val1);
            $(e).attr('uid', uid1);
            $(td).find('input[id$="_uid"]').val(uid1);
            multi_divX = multi_div.clone(true);
            $(multi_divX).attr('id', fieldname + '-' + arnum + '-listing');
            $('#' + fieldname + '-' + arnum + '-listing').replaceWith(multi_divX);
            $(e).trigger('copy');
            arnum++;
          }
        } else if ($(td1).find('.RejectionWidget').length > 0) {
          checkbox = $(td1).find('.rejectionwidget-checkbox').prop('checked');
          arnum = 1;
          while (arnum < nr_ars) {
            td = $(tr).find('td[arnum="' + arnum + '"]')[0];
            e = $(td).find('.rejectionwidget-checkbox')[0];
            if (checkbox) {
              $(e).attr('checked', true);
            } else {
              $(e).removeAttr('checked');
            }
            $(e).trigger('copy');
            arnum++;
          }
          checkbox_other = $(td1).find('.rejectionwidget-checkbox-other').prop('checked');
          arnum = 1;
          while (arnum < nr_ars) {
            td = $(tr).find('td[arnum="' + arnum + '"]')[0];
            e = $(td).find('.rejectionwidget-checkbox-other')[0];
            if (checkbox_other) {
              $(e).attr('checked', true);
            } else {
              $(e).removeAttr('checked');
            }
            $(e).trigger('copy');
            arnum++;
          }
          input_other = $(td1).find('.rejectionwidget-input-other').val();
          arnum = 1;
          while (arnum < nr_ars) {
            td = $(tr).find('td[arnum="' + arnum + '"]')[0];
            e = $(td).find('.rejectionwidget-input-other')[0];
            $(e).val(input_other);
            $(e).trigger('copy');
            arnum++;
          }
          select_options = $(td1).find('.rejectionwidget-multiselect').find('option');
          i = 0;
          while (select_options.length > i) {
            option = select_options[i];
            value = $(option).val();
            selected = option.selected;
            arnum = 1;
            while (arnum < nr_ars) {
              td = $(tr).find('td[arnum="' + arnum + '"]')[0];
              e = $(td).find('.rejectionwidget-multiselect option[value="' + value + '"]');
              $(e).attr('selected', selected);
              $(td).find('select.rejectionwidget-multiselect').trigger('copy');
              arnum++;
            }
            i++;
          }
        } else if ($(td1).find('select').length > 0) {
          input = $(td1).find('select').val();
          arnum = 1;
          while (arnum < nr_ars) {
            td = $(tr).find('td[arnum="' + arnum + '"]')[0];
            e = $(td).find('select')[0];
            $(e).val(input);
            $(e).trigger('copy');
            arnum++;
          }
        } else if ($(td1).find('input[type="text"]').length > 0) {
          val1 = $(td1).find('input').val();
          arnum = 1;
          while (arnum < nr_ars) {
            td = $(tr).find('td[arnum="' + arnum + '"]')[0];
            e = $(td).find('input')[0];
            $(e).val(val1);
            $(e).trigger('copy');
            arnum++;
          }
        } else if ($(td1).find('textarea').length > 0) {
          val1 = $(td1).find('textarea').val();
          arnum = 1;
          while (arnum < nr_ars) {
            td = $(tr).find('td[arnum="' + arnum + '"]')[0];
            e = $(td).find('textarea')[0];
            $(e).val(val1);
            $(e).trigger('copy');
            arnum++;
          }
        } else if ($(td1).find('input[type="checkbox"]').length > 0) {
          val1 = $(td1).find('input[type="checkbox"]').prop('checked');
          arnum = 1;
          while (arnum < nr_ars) {
            td = $(tr).find('td[arnum="' + arnum + '"]')[0];
            e = $(td).find('input[type="checkbox"]')[0];
            if (val1) {
              $(e).attr('checked', true);
            } else {
              $(e).removeAttr('checked');
            }
            $(e).trigger('copy');
            arnum++;
          }
        }
      });
    };

    /*
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
     */
    client_selected = function() {

      /* Client field is visible and a client has been selected
       */
      $('tr[fieldname="Client"] input[type="text"]').live('selected copy', function(event, item) {
        var arnum;
        arnum = get_arnum(this);
        filter_by_client(arnum);
      }).each(function(i, e) {
        if ($(e).val()) {
          $(e).trigger('copy');
        }
      });
    };
    contact_selected = function() {

      /* Selected a Contact: retrieve and complete UI for CC Contacts
       */
      $('tr[fieldname="Contact"] input[type="text"]').live('selected copy', function(event, item) {
        var arnum;
        arnum = get_arnum(this);
        cc_contacts_set(arnum);
      });
    };
    cc_contacts_set = function(arnum) {

      /* Setting the CC Contacts after a Contact was set
       *
       * Contact.CCContact may contain a list of Contact references.
       * So we need to select them in the form with some fakey html,
       * and set them in the state.
       */
      var cc_div, cc_uid_element, contact_element, contact_uid, request_data, td;
      td = $('tr[fieldname=\'Contact\'] td[arnum=\'' + arnum + '\']');
      contact_element = $(td).find('input[type=\'text\']')[0];
      contact_uid = $(contact_element).attr('uid');
      cc_div = $('tr[fieldname=\'CCContact\'] td[arnum=\'' + arnum + '\'] .multiValued-listing');
      cc_uid_element = $('#CCContact-' + arnum + '_uid');
      $(cc_div).empty();
      $(cc_uid_element).empty();
      if (contact_uid) {
        request_data = {
          catalog_name: 'portal_catalog',
          UID: contact_uid
        };
        window.bika.lims.jsonapi_read(request_data, function(data) {
          var cc_titles, cc_uids, del_btn, del_btn_src, i, new_item, ob, title, uid;
          if (data.objects && data.objects.length > 0) {
            ob = data.objects[0];
            cc_titles = ob['CCContact'];
            cc_uids = ob['CCContact_uid'];
            if (!cc_uids) {
              return;
            }
            $(cc_uid_element).val(cc_uids.join(','));
            i = 0;
            while (i < cc_uids.length) {
              title = cc_titles[i];
              uid = cc_uids[i];
              del_btn_src = window.portal_url + '/++resource++bika.lims.images/delete.png';
              del_btn = '<img class=\'deletebtn\' data-contact-title=\'' + title + '\' src=\'' + del_btn_src + '\' fieldname=\'CCContact\' uid=\'' + uid + '\'/>';
              new_item = '<div class=\'reference_multi_item\' uid=\'' + uid + '\'>' + del_btn + title + '</div>';
              $(cc_div).append($(new_item));
              i++;
            }
            state_set(arnum, 'CCContact', cc_uids.join(','));
          }
        });
      }
    };
    cc_contacts_deletebtn_click = function() {
      $('tr[fieldname=\'CCContact\'] .reference_multi_item .deletebtn').unbind();
      $('tr[fieldname=\'CCContact\'] .reference_multi_item .deletebtn').live('click', function() {
        var arnum, existing_uids, fieldname, uid;
        arnum = get_arnum(this);
        fieldname = $(this).attr('fieldname');
        uid = $(this).attr('uid');
        existing_uids = $('td[arnum="' + arnum + '"] input[name$="_uid"]').val().split(',');
        destroy(existing_uids, uid);
        $('td[arnum="' + arnum + '"] input[name$="CCContact-' + arnum + '_uid"]').val(existing_uids.join(','));
        $('td[arnum="' + arnum + '"] input[name="CCContact-0"]').attr('uid', existing_uids.join(','));
        $(this).parent('div').remove();
      });
    };
    spec_selected = function() {

      /* Configure handler for the selection of a Specification
       *
       */
      $('tr[fieldname=\'Specification\'] td[arnum] input[type=\'text\']').live('selected copy', function(event, item) {
        var arnum;
        arnum = get_arnum(this);
        state_set(arnum, 'Specification', $(this).attr('uid'));
        specification_refetch(arnum);
      }).each(function(i, e) {
        if ($(e).val()) {
          $(e).trigger('copy');
        }
      });
    };
    spec_field_entry = function() {

      /* Validate entry into min/max/error fields, and save them
       * to the state.
       *
       * If min>max or max<min, or error<>0,100, correct the values directly
       * in the field by setting one or the other to a "" value to indicate
       * an error
       */
      $('.min, .max, .error').live('change', function() {
        var arnum, arnum_i, error, error_element, hash, hashes, keyword, max, max_element, min, min_element, state, td, tr, uid;
        td = $(this).parents('td');
        tr = $(td).parent();
        arnum = $(td).attr('arnum');
        uid = $(tr).attr('uid');
        keyword = $(tr).attr('keyword');
        min_element = $(td).find('.min');
        max_element = $(td).find('.max');
        error_element = $(td).find('.error');
        min = parseInt(min_element.val(), 10);
        max = parseInt(max_element.val(), 10);
        error = parseInt(error_element.val(), 10);
        if ($(this).hasClass('min')) {
          if (isNaN(min)) {
            $(min_element).val('');
          } else if (!isNaN(max) && min > max) {
            $(max_element).val('');
          }
        } else if ($(this).hasClass('max')) {
          if (isNaN(max)) {
            $(max_element).val('');
          } else if (!isNaN(min) && max < min) {
            $(min_element).val('');
          }
        } else if ($(this).hasClass('error')) {
          if (isNaN(error) || error < 0 || error > 100) {
            $(error_element).val('');
          }
        }
        arnum_i = parseInt(arnum, 10);
        state = bika.lims.ar_add.state[arnum_i];
        hash = hashes_to_hash(state['ResultsRange'], 'uid');
        hash[uid] = {
          'min': min_element.val(),
          'max': max_element.val(),
          'error': error_element.val(),
          'uid': uid,
          'keyword': keyword
        };
        hashes = hash_to_hashes(hash);
        state_set(arnum, 'ResultsRange', hashes);
      });
    };
    specification_refetch = function(arnum) {

      /* Lookup the selected specification with ajax, then set all
       * min/max/error fields in all columns to match.
       *
       * If the specification does not define values for a particular service,
       * the form values will not be cleared.
       */
      var arnum_i, d, request_data, spec_uid, state;
      d = $.Deferred();
      arnum_i = parseInt(arnum, 10);
      state = bika.lims.ar_add.state[arnum_i];
      spec_uid = state['Specification'];
      if (!spec_uid) {
        d.resolve();
        return d.promise();
      }
      request_data = {
        catalog_name: 'bika_setup_catalog',
        UID: spec_uid
      };
      window.bika.lims.jsonapi_read(request_data, function(data) {
        var rr;
        if (data.success && data.objects.length > 0) {
          rr = data.objects[0]['ResultsRange'];
          if (rr && rr.length > 0) {
            state_set(arnum, 'ResultsRange', rr);
            specification_apply();
          }
        }
        d.resolve();
      });
      return d.promise();
    };
    specification_apply = function() {
      var arnum, hashlist, nr_ars, spec;
      nr_ars = parseInt($('input[id="ar_count"]').val(), 10);
      arnum = 0;
      while (arnum < nr_ars) {
        hashlist = bika.lims.ar_add.state[arnum]['ResultsRange'];
        if (hashlist) {
          spec = hashes_to_hash(hashlist, 'uid');
          $.each($('tr.service_selector td[class*=\'ar\\.' + arnum + '\']'), function(i, td) {
            var error, max, min, uid;
            uid = $(td).parents('[uid]').attr('uid');
            if (uid && uid !== 'new' && uid in spec) {
              min = $(td).find('.min');
              max = $(td).find('.max');
              error = $(td).find('.error');
              $(min).attr('value', spec[uid].min);
              $(max).attr('value', spec[uid].max);
              $(error).attr('value', spec[uid].error);
            }
          });
        }
        arnum++;
      }
    };
    set_spec_from_sampletype = function(arnum) {

      /* Look for Specifications with the selected SampleType.
       *
       * 1) Set the value of the Specification field
       * 2) Fetch the spec from the server, and set all the spec field values
       * 3) Set the partition indicator numbers.
       */
      var request_data, spec_element, spec_uid_element, st_uid;
      st_uid = $('tr[fieldname=\'SampleType\'] ' + 'td[arnum=\'' + arnum + '\'] ' + 'input[type=\'text\']').attr('uid');
      if (!st_uid) {
        return;
      }
      spec_filter_on_sampletype(arnum);
      spec_element = $('tr[fieldname=\'Specification\'] ' + 'td[arnum=\'' + arnum + '\'] ' + 'input[type=\'text\']');
      spec_uid_element = $('tr[fieldname=\'Specification\'] ' + 'td[arnum=\'' + arnum + '\'] ' + 'input[id$=\'_uid\']');
      request_data = {
        catalog_name: 'bika_setup_catalog',
        portal_type: 'AnalysisSpec',
        getSampleTypeUID: st_uid,
        include_fields: ['Title', 'UID', 'ResultsRange']
      };
      window.bika.lims.jsonapi_read(request_data, function(data) {
        var rr, spec;
        if (data.objects.length > 0) {
          spec = data.objects[0];
          $(spec_element).val(spec['Title']);
          $(spec_element).attr('uid', spec['UID']);
          $(spec_uid_element).val(spec['UID']);
          state_set(arnum, 'Specification', spec['UID']);
          rr = data.objects[0]['ResultsRange'];
          if (rr && rr.length > 0) {
            state_set(arnum, 'ResultsRange', rr);
            specification_apply();
          }
        }
      });
    };
    spec_filter_on_sampletype = function(arnum) {

      /* Possibly filter the Specification dropdown when SampleType selected
       *
       * when a SampleType is selected I will allow only specs to be
       * selected which have a matching SampleType value, or which
       * have no sampletype set.
       */
      var arnum_i, query, query_str, sampletype_uid, spec_element;
      arnum_i = parseInt(arnum, 10);
      sampletype_uid = bika.lims.ar_add.state[arnum_i]['SampleType'];
      spec_element = $('tr[fieldname=\'Specification\'] td[arnum=\'' + arnum + '\'] input[type=\'text\']');
      query_str = $(spec_element).attr('search_query');
      query = $.parseJSON(query_str);
      if (query.hasOwnProperty('getSampleTypeUID')) {
        delete query.getSampleTypeUID;
      }
      query.getSampleTypeUID = [encodeURIComponent(sampletype_uid), ''];
      query_str = $.toJSON(query);
      $(spec_element).attr('search_query', query_str);
    };
    samplepoint_selected = function() {
      $('tr[fieldname=\'SamplePoint\'] td[arnum] input[type=\'text\']').live('selected copy', function(event, item) {
        var arnum;
        arnum = get_arnum(this);
        samplepoint_set(arnum);
      }).each(function(i, e) {
        if ($(e).val()) {
          $(e).trigger('copy');
        }
      });
    };
    samplepoint_set = function(arnum) {

      /***
       * Sample point and Sample type can set each other.
       */
      var spe, ste;
      spe = $('tr[fieldname=\'SamplePoint\'] td[arnum=\'' + arnum + '\'] input[type=\'text\']');
      ste = $('tr[fieldname=\'SampleType\'] td[arnum=\'' + arnum + '\'] input[type=\'text\']');
      filter_combogrid(ste, 'getSamplePointTitle', $(spe).val(), 'search_query');
    };
    sampletype_selected = function() {
      $('tr[fieldname=\'SampleType\'] td[arnum] input[type=\'text\']').live('selected copy', function(event, item) {
        var arnum;
        arnum = get_arnum(this);
        sampletype_set(arnum);
      }).each(function(i, e) {
        if ($(e).val()) {
          $(e).trigger('copy');
        }
      });
    };
    sampletype_set = function(arnum) {
      var spe, ste;
      spe = $('tr[fieldname=\'SamplePoint\'] td[arnum=\'' + arnum + '\'] input[type=\'text\']');
      ste = $('tr[fieldname=\'SampleType\'] td[arnum=\'' + arnum + '\'] input[type=\'text\']');
      filter_combogrid(spe, 'getSampleTypeTitle', $(ste).val(), 'search_query');
      set_spec_from_sampletype(arnum);
      partition_indicators_set(arnum);
    };
    profile_selected = function() {

      /* A profile is selected.
       * - Set the profile's analyses (existing analyses will be cleared)
       * - Set the partition number indicators
       */
      $('tr[fieldname=\'Profiles\'] td[arnum] input[type=\'text\']').live('selected', function(event, item) {
        var arnum, uids_array;
        arnum = $(this).parents('td').attr('arnum');
        uids_array = $('#Profiles-' + arnum).attr('uid').split(',');
        template_unset(arnum);
        profile_set(arnum, uids_array[uids_array.length - 1]).then(function() {
          specification_apply();
          partition_indicators_set(arnum);
        });
      }).live('copy', function(event, item) {
        var arnum, i, profiles, uids_array;
        arnum = $(this).parents('td').attr('arnum');
        profiles = $('#Profiles-' + arnum);
        if (profiles.attr('uid')) {
          uids_array = profiles.attr('uid').split(',');
          template_unset(arnum);
          i = 0;
          while (i < uids_array.length) {
            profile_set(arnum, uids_array[i]).then(function() {
              specification_apply();
              partition_indicators_set(arnum);
            });
            i++;
          }
          recalc_prices(arnum);
        }
      }).each(function(i, e) {
        if ($(e).val()) {
          $(e).trigger('copy');
        }
      });
    };
    profile_set = function(arnum, profile_uid) {

      /* Set the profile analyses for the AR in this column
       *  also clear the AR Template field.
       */
      var d, request_data;
      d = $.Deferred();
      request_data = {
        catalog_name: 'bika_setup_catalog',
        portal_type: 'AnalysisProfile',
        UID: profile_uid
      };
      bika.lims.jsonapi_read(request_data, function(data) {
        var arprofile_services_uid, defs, i, profile, profile_objects, service_data;
        profile_objects = data['objects'][0];
        profile = $('div.reference_multi_item[uid=\'' + profile_objects.UID + '\']');
        defs = [];
        service_data = profile_objects['service_data'];
        arprofile_services_uid = [];
        profile.attr('price', profile_objects['AnalysisProfilePrice']);
        profile.attr('useprice', profile_objects['UseAnalysisProfilePrice']);
        profile.attr('VATAmount', profile_objects['VATAmount']);
        drymatter_unset(arnum);
        if (service_data.length !== 0) {
          i = 0;
          while (i < service_data.length) {
            arprofile_services_uid.push(service_data[i].UID);
            i++;
          }
        }
        profile.attr('services', arprofile_services_uid);
        if ($('#singleservice').length > 0) {
          defs.push(expand_services_singleservice(arnum, service_data));
        } else {
          defs.push(expand_services_bika_listing(arnum, service_data));
        }
        $.when.apply(null, defs).then(function() {
          d.resolve();
        });
      });
      return d.promise();
    };
    profiles_unset_all = function(arnum) {

      /**
       * This function remove all the selected analysis profiles
       */
      var i, profiles;
      if ($('#Profiles-' + arnum).attr('uid') !== '') {
        $('#Profiles-' + arnum).attr('price', '');
        $('#Profiles-' + arnum).attr('services', $.toJSON([]));
        $('#Profiles-' + arnum + '_uid').val('');
        profiles = $('div#Profiles-' + arnum + '-listing').children();
        i = void 0;
        i = profiles.length - 1;
        while (i >= 0) {
          unset_profile_analysis_services(profiles[i], arnum);
          i--;
        }
        profiles.children().remove();
        recalc_prices(arnum);
      }
    };
    profile_unset_trigger = function() {

      /***
       After deleting an analysis profile we have to uncheck their associated analysis services, so we need to bind
       the analyses service unseting function. Ever since this binding should be done on the delete image and
       (that is inserted dynamically), we need to settle the the event on the first ancestor element which doesn't
       load dynamically
       */
      $('div[id^=\'archetypes-fieldname-Profiles-\']').on('click', 'div.reference_multi_item .deletebtn', function() {
        var arnum, profile_object;
        profile_object = $(this).parent();
        arnum = get_arnum(profile_object);
        unset_profile_analysis_services(profile_object, arnum);
        recalc_prices(arnum);
      });
    };
    unset_profile_analysis_services = function(profile, arnum) {

      /**
       * The function unsets the selected analyses services related with the removed analysis profile.
       * :profile: the profile DOM division
       * :arnum: the number of the column
       *
       */
      var i, service_uids;
      service_uids = $(profile).attr('services').split(',');
      i = void 0;
      i = service_uids.length - 1;
      while (i >= 0) {
        analysis_cb_uncheck(arnum, service_uids[i]);
        i--;
      }
    };
    composite_selected = function(arnum) {
      $('input#Composite-' + arnum).live('change', function(event, item) {
        template_unset(arnum);
        $('input#Composite-' + arnum).unbind();
      });
    };
    template_selected = function() {
      $('tr[fieldname=\'Template\'] td[arnum] input[type=\'text\']').live('selected copy', function(event, item) {
        var arnum;
        arnum = $(this).parents('td').attr('arnum');
        template_set(arnum);
      }).each(function(i, e) {
        if ($(e).val()) {
          $(e).trigger('copy');
        }
      });
    };
    template_set = function(arnum) {
      var d, request_data, td, title;
      d = $.Deferred();
      uncheck_all_services(arnum);
      td = $('tr[fieldname=\'Template\'] ' + 'td[arnum=\'' + arnum + '\'] ');
      title = $(td).find('input[type=\'text\']').val();
      request_data = {
        catalog_name: 'bika_setup_catalog',
        title: title,
        include_fields: ['SampleType', 'SampleTypeUID', 'SamplePoint', 'SamplePointUID', 'ReportDryMatter', 'Composite', 'AnalysisProfile', 'Partitions', 'Analyses', 'Prices']
      };
      window.bika.lims.jsonapi_read(request_data, function(data) {
        var td;
        var defs, template;
        if (data.success && data.objects.length > 0) {
          template = data.objects[0];
          td = void 0;
          td = $('tr[fieldname=\'SampleType\'] td[arnum=\'' + arnum + '\']');
          $(td).find('input[type=\'text\']').val(template['SampleType']).attr('uid', template['SampleTypeUID']);
          $(td).find('input[id$=\'_uid\']').val(template['SampleTypeUID']);
          state_set(arnum, 'SampleType', template['SampleTypeUID']);
          set_spec_from_sampletype(arnum);
          td = $('tr[fieldname=\'SamplePoint\'] td[arnum=\'' + arnum + '\']');
          $(td).find('input[type=\'text\']').val(template['SamplePoint']).attr('uid', template['SamplePointUID']);
          $(td).find('input[id$=\'_uid\']').val(template['SamplePointUID']);
          state_set(arnum, 'SamplePoint', template['SamplePointUID']);
          td = $('tr[fieldname=\'Profile\'] td[arnum=\'' + arnum + '\']');
          if (template['AnalysisProfile']) {
            $(td).find('input[type=\'text\']').val(template['AnalysisProfile']).attr('uid', template['AnalysisProfileUID']);
            $(td).find('input[id$=\'_uid\']').val(template['AnalysisProfileUID']);
            state_set(arnum, 'Profile', template['AnalysisProfileUID']);
          } else {
            profiles_unset_all(arnum);
          }
          defs = [];
          if ($('#singleservice').length > 0) {
            defs.push(expand_services_singleservice(arnum, template['service_data']));
          } else {
            defs.push(expand_services_bika_listing(arnum, template['service_data']));
          }
          td = $('tr[fieldname=\'Composite\'] td[arnum=\'' + arnum + '\']');
          if (template['Composite']) {
            $(td).find('input[type=\'checkbox\']').attr('checked', true);
            state_set(arnum, 'Composite', template['Composite']);
            composite_selected(arnum);
          } else {
            $(td).find('input[type=\'checkbox\']').attr('checked', false);
          }
          $.when.apply(null, defs).then(function() {
            td = $('tr[fieldname=\'ReportDryMatter\'] td[arnum=\'' + arnum + '\']');
            if (template['ReportDryMatter']) {
              $(td).find('input[type=\'checkbox\']').attr('checked', true);
              drymatter_set(arnum, true);
            }
            if (template['Partitions']) {
              state_set(arnum, 'Partitions', template['Partitions']);
            } else {
              partnrs_calc(arnum);
            }
            _partition_indicators_set(arnum);
            d.resolve();
          });
        }
      });
      return d.promise();
    };
    template_unset = function(arnum) {
      var td;
      td = $('tr[fieldname=\'Template\'] td[arnum=\'' + arnum + '\']');
      $(td).find('input[type=\'text\']').val('').attr('uid', '');
      $(td).find('input[id$=\'_uid\']').val('');
    };
    drymatter_selected = function() {
      $('tr[fieldname=\'ReportDryMatter\'] td[arnum] input[type=\'checkbox\']').live('click copy', function(event) {
        var arnum;
        arnum = get_arnum(this);
        if ($(this).prop('checked')) {
          drymatter_set(arnum);
          partition_indicators_set(arnum);
        } else {
          drymatter_unset(arnum);
        }
      }).each(function(i, e) {
        $(e).trigger('copy');
      });
    };
    drymatter_set = function(arnum) {

      /* set the Dry Matter service, dependencies, etc
      
       skip_indicators should be true if you want to prevent partition
       indicators from being set.  This is useful if drymatter is being
       checked during the application of a Template to this column.
       */
      var cat, checkbox, dm_service, element, keyword, poc, price, title, uid, vatamount;
      dm_service = $('#getDryMatterService');
      uid = $(dm_service).val();
      cat = $(dm_service).attr('cat');
      poc = $(dm_service).attr('poc');
      keyword = $(dm_service).attr('keyword');
      title = $(dm_service).attr('title');
      price = $(dm_service).attr('price');
      vatamount = $(dm_service).attr('vatamount');
      element = $('tr[fieldname=\'ReportDryMatter\'] ' + 'td[arnum=\'' + arnum + '\'] ' + 'input[type=\'checkbox\']');
      if ($(element).attr('checked')) {
        checkbox = $('tr[uid=\'' + uid + '\'] ' + 'td[class*=\'ar\\.' + arnum + '\'] ' + 'input[type=\'checkbox\']');
        if ($('#singleservice').length > 0) {
          if ($(checkbox).length > 0) {
            $('#ReportDryMatter-' + arnum).prop('checked', true);
          } else {
            $('#singleservice').attr('uid', uid);
            $('#singleservice').attr('keyword', keyword);
            $('#singleservice').attr('title', title);
            $('#singleservice').attr('price', price);
            $('#singleservice').attr('vatamount', vatamount);
            singleservice_duplicate(uid, title, keyword, price, vatamount);
            $('#ReportDryMatter-' + arnum).prop('checked', true);
          }
          state_analyses_push(arnum, uid);
        } else {
          $('#ReportDryMatter-' + arnum).prop('checked', true);
          state_analyses_push(arnum, uid);
        }
        deps_calc(arnum, [uid], true, _('Dry Matter'));
        recalc_prices(arnum);
        state_set(arnum, 'ReportDryMatter', true);
        specification_apply();
      }
    };
    drymatter_unset = function(arnum) {
      state_set(arnum, 'ReportDryMatter', false);
    };
    sample_selected = function() {
      $('tr[fieldname=\'Sample\'] td[arnum] input[type=\'text\']').live('selected copy', function(event, item) {
        var arnum;
        arnum = get_arnum(this);
        sample_set(arnum);
      }).each(function(i, e) {
        if ($(e).val()) {
          $(e).trigger('copy');
        }
      });
      $('tr[fieldname=\'Sample\'] td[arnum] input[type=\'text\']').live('blur', function(event, item) {
        var arnum;
        arnum = get_arnum(this);
        if (!$(this).val()) {
          $('td[arnum="' + arnum + '"]').find(':disabled').prop('disabled', false);
        }
      });
    };
    sample_set = function(arnum) {
      $.getJSON(window.location.href.split('/ar_add')[0] + '/secondary_ar_sample_info', {
        'Sample_uid': $('#Sample-' + arnum).attr('uid'),
        '_authenticator': $('input[name="_authenticator"]').val()
      }, function(data) {
        var element;
        var element, fieldname, fieldvalue, i;
        if (!!data) {
          i = 0;
          while (i < data.length) {
            fieldname = data[i][0];
            fieldvalue = data[i][1];
            if (fieldname.search('_uid') > -1) {
              fieldname = fieldname.split('_uid')[0];
              element = $('#' + fieldname + '-' + arnum)[0];
              $(element).attr('uid', fieldvalue);
              $(element).val(fieldvalue);
            } else {
              element = $('#' + fieldname + '-' + arnum)[0];
              if (!element) {
                console.log('Selector #' + fieldname + '-' + arnum + ' not present in form');
                i++;
                continue;
              }
              switch (element.type) {
                case 'text':
                case 'select-one':
                  $(element).val(fieldvalue);
                  if (fieldvalue) {
                    $(element).trigger('copy');
                  }
                  $(element).prop('disabled', true);
                  break;
                case 'checkbox':
                  if (fieldvalue) {
                    $(element).attr('checked', true);
                    $(element).trigger('copy');
                  } else {
                    $(element).removeAttr('checked');
                  }
                  $(element).prop('disabled', true);
                  break;
                default:
                  console.log('Unhandled field type for field ' + fieldname + ': ' + element.type);
              }
              state_set(arnum, fieldname, fieldvalue);
            }
            i++;
          }
        }
      });
    };

    /*
     singleservice_dropdown_init    - configure the combogrid (includes handler)
     singleservice_duplicate        - create new service row
     singleservice_deletebtn_click  - remove a service from the form
     expand_services_singleservice  - add a list of services (single-service)
     expand_services_bika_listing   - add a list of services (bika_listing)
     uncheck_all_services           - unselect all from form and state
     */
    singleservice_dropdown_init = function() {

      /*
       * Configure the single-service selector combogrid
       */
      var authenticator, options, url;
      authenticator = $('[name=\'_authenticator\']').val();
      url = window.location.href.split('/portal_factory')[0] + '/service_selector?_authenticator=' + authenticator;
      options = {
        url: url,
        width: '700px',
        showOn: false,
        searchIcon: true,
        minLength: '2',
        resetButton: false,
        sord: 'asc',
        sidx: 'Title',
        colModel: [
          {
            'columnName': 'Title',
            'align': 'left',
            'label': 'Title',
            'width': '50'
          }, {
            'columnName': 'Identifiers',
            'align': 'left',
            'label': 'Identifiers',
            'width': '35'
          }, {
            'columnName': 'Keyword',
            'align': 'left',
            'label': 'Keyword',
            'width': '15'
          }, {
            'columnName': 'Price',
            'hidden': true
          }, {
            'columnName': 'VAT',
            'hidden': true
          }, {
            'columnName': 'UID',
            'hidden': true
          }
        ],
        select: function(event, ui) {
          $('#singleservice').attr('uid', ui['item']['UID']);
          $('#singleservice').attr('keyword', ui['item']['Keyword']);
          $('#singleservice').attr('title', ui['item']['Title']);
          singleservice_duplicate(ui['item']['UID'], ui['item']['Title'], ui['item']['Keyword'], ui['item']['Price'], ui['item']['VAT']);
        }
      };
      $('#singleservice').combogrid(options);
    };
    singleservice_duplicate = function(new_uid, new_title, new_keyword, new_price, new_vatamount) {

      /*
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
       */
      var existing, keyword, new_tr, price, service_label, title, tr, uid, vatamount;
      uid = new_uid || $('#singleservice').attr('uid');
      keyword = new_keyword || $('#singleservice').attr('keyword');
      title = new_title || $('#singleservice').attr('title');
      price = new_price || $('#singleservice').attr('price');
      vatamount = new_vatamount || $('#singleservice').attr('vatamount');
      existing = $('tr[uid=\'' + uid + '\']');
      if (existing.length > 0) {
        return;
      }
      tr = $('#singleservice').parents('tr');
      new_tr = $(tr).clone();
      $(tr).attr('uid', uid);
      $(tr).attr('keyword', keyword);
      $(tr).attr('title', title);
      $(tr).attr('price', price);
      $(tr).attr('vatamount', vatamount);
      $(tr).find('input[name=\'uids:list\']').attr('value', uid);
      $(tr).find('.alert').attr('uid', uid);
      service_label = $('<a href=\'#\' class=\'deletebtn\'><img src=\'' + portal_url + '/++resource++bika.lims.images/delete.png\' uid=\'' + uid + '\' style=\'vertical-align: -3px;\'/></a>&nbsp;' + '<span>' + title + '</span>');
      $(tr).find('#singleservice').replaceWith(service_label);
      $(new_tr).find('[type=\'checkbox\']').removeAttr('checked');
      $(new_tr).find('[type=\'text\']').val('');
      $(new_tr).find('#singleservice').attr('uid', 'new');
      $(new_tr).find('#singleservice').attr('keyword', '');
      $(new_tr).find('#singleservice').attr('title', '');
      $(new_tr).find('#singleservice').attr('price', '');
      $(new_tr).find('#singleservice').attr('vatamount', '');
      $(new_tr).find('#singleservice').removeClass('has_combogrid_widget');
      $(tr).after(new_tr);
      specification_apply();
      singleservice_dropdown_init();
    };
    singleservice_deletebtn_click = function() {

      /* Remove the service row.
       */
      $('.service_selector a.deletebtn').live('click', function(event) {
        var arnum, checkboxes, element, i, tr, uid;
        event.preventDefault();
        tr = $(this).parents('tr[uid]');
        checkboxes = $(tr).find('input[type=\'checkbox\']').not('[name=\'uids:list\']');
        i = 0;
        while (i < checkboxes.length) {
          element = checkboxes[i];
          arnum = get_arnum(element);
          uid = $(element).parents('[uid]').attr('uid');
          state_analyses_remove(arnum, uid);
          i++;
        }
        $(tr).remove();
      });
    };
    expand_services_singleservice = function(arnum, service_data) {

      /*
       When the single-service serviceselector is in place,
       this function is called to select services for setting a bunch
       of services in one AR, eg Profiles and Templates.
      
       service_data is included from the JSONReadExtender of Profiles and
       Templates.
       */
      var e, i, keyword, not_present, price, sd, title, uid, vatamount;
      uid = void 0;
      keyword = void 0;
      title = void 0;
      price = void 0;
      vatamount = void 0;
      not_present = [];
      sd = service_data;
      i = 0;
      while (i < sd.length) {
        uid = sd[i]['UID'];
        keyword = sd[i]['Keyword'];
        price = sd[i]['Price'];
        vatamount = sd[i]['VAT'];
        e = $('tr[uid=\'' + uid + '\'] td[class*=\'ar\\.' + arnum + '\'] ' + 'input[type=\'checkbox\']');
        if (e.length > 0) {
          analysis_cb_check(arnum, sd[i]['UID']);
        } else {
          not_present.push(sd[i]);
        }
        i++;
      }
      i = 0;
      while (i < not_present.length) {
        title = not_present[i]['Title'];
        uid = not_present[i]['UID'];
        keyword = not_present[i]['Keyword'];
        price = not_present[i]['Price'];
        vatamount = not_present[i]['VAT'];
        $('#singleservice').val(title);
        $('#singleservice').attr('uid', uid);
        $('#singleservice').attr('keyword', keyword);
        $('#singleservice').attr('title', title);
        $('#singleservice').attr('price', price);
        $('#singleservice').attr('vatamount', vatamount);
        singleservice_duplicate(uid, title, keyword, price, vatamount);
        analysis_cb_check(arnum, uid);
        i++;
      }
      recalc_prices(arnum);
    };
    expand_services_bika_listing = function(arnum, service_data) {
      var d, def, defs, expanded_categories, service, services, si, th;
      d = $.Deferred();
      services = [];
      defs = [];
      expanded_categories = [];
      if (!!service_data) {
        si = 0;
        while (si < service_data.length) {
          service = service_data[si];
          services.push(service);
          th = $('table[form_id=\'' + service['PointOfCapture'] + '\'] ' + 'th[cat=\'' + service['CategoryTitle'] + '\']');
          if (expanded_categories.indexOf(th) < 0) {
            expanded_categories.push(th);
            def = $.Deferred();
            def = category_header_expand_handler(th);
            defs.push(def);
          }
          si++;
        }
      }
      $.when.apply(null, defs).then(function() {
        var si;
        si = 0;
        while (si < services.length) {
          analysis_cb_check(arnum, services[si]['UID']);
          si++;
        }
        recalc_prices(arnum);
        d.resolve();
      });
      return d.promise();
    };
    uncheck_all_services = function(arnum) {
      var cblist, e, i, uid;
      drymatter_unset(arnum);
      cblist = $('tr[uid] td[class*=\'ar\\.' + arnum + '\'] ' + 'input[type=\'checkbox\']').filter(':checked');
      i = 0;
      while (i < cblist.length) {
        e = cblist[i];
        arnum = get_arnum(e);
        uid = $(e).parents('[uid]').attr('uid');
        analysis_cb_uncheck(arnum, uid);
        i++;
      }
    };
    category_header_clicked = function() {
      var ajax_categories;
      ajax_categories = $('input[name=\'ajax_categories\']');
      $('.bika-listing-table th.collapsed').unbind().live('click', function(event) {
        category_header_expand_handler(this);
      });
      $('.bika-listing-table th.expanded').unbind().live('click', function() {
        $(this).parent().nextAll('tr[cat=\'' + $(this).attr('cat') + '\']').toggle(false);
        $(this).removeClass('expanded').addClass('collapsed');
      });
    };
    category_header_expand_handler = function(element) {

      /* Deferred function to expand the category with ajax (or not!!)
       on first expansion.  duplicated from bika.lims.bikalisting.js, this code
       fires when categories are expanded automatically (eg, when profiles or templates require
       that the category contents are visible for selection)
      
       Also, this code returns deferred objects, not their promises.
      
       :param: element - The category header TH element which normally receives 'click' event
       */
      var ajax_categories_enabled, ar_count, cat_title, def, form_id, options, placeholder, url;
      def = $.Deferred();
      form_id = $(element).parents('[form_id]').attr('form_id');
      cat_title = $(element).attr('cat');
      ar_count = parseInt($('#ar_count').val(), 10);
      url = $('input[name=\'ajax_categories_url\']').length > 0 ? $('input[name=\'ajax_categories_url\']').val() : window.location.href.split('?')[0];
      placeholder = $('tr[data-ajax_category=\'' + cat_title + '\']');
      if ($(element).hasClass('expanded')) {
        def.resolve();
        return def;
      }
      ajax_categories_enabled = $('input[name=\'ajax_categories\']');
      if (ajax_categories_enabled.length > 0 && placeholder.length > 0) {
        options = {};
        options['ajax_category_expand'] = 1;
        options['cat'] = cat_title;
        options['ar_count'] = ar_count;
        options['form_id'] = form_id;
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
          specification_apply();
          def.resolve();
        });
      } else {
        $(element).parent().nextAll('tr[cat=\'' + cat_title + '\']').toggle(true);
        $(element).removeClass('collapsed').addClass('expanded');
        def.resolve();
      }
      return def;
    };

    /* - analysis_cb_click   user interaction with form (select, unselect)
     * - analysis_cb_check   performs the same action, but from code (no .click)
     * - analysis_cb_uncheck does the reverse
     * - analysis_cb_after_change  always runs when service checkbox changes.
     * - state_analyses_push        add selected service to state
     * - state_analyses_remove      remove service uid from state
     */
    analysis_cb_click = function() {

      /* configures handler for click event on analysis checkboxes
       * and their associated select-all checkboxes.
       *
       * As far as possible, the bika_listing and single-select selectors
       * try to emulate each other's HTML structure in each row.
       *
       */
      $('.service_selector input[type=\'checkbox\'][name!=\'uids:list\']').live('click', function() {
        var arnum, title, uid;
        arnum = get_arnum(this);
        uid = $(this).parents('[uid]').attr('uid');
        analysis_cb_after_change(arnum, uid);
        if ($(this).prop('checked')) {
          state_analyses_push(arnum, uid);
        } else {
          state_analyses_remove(arnum, uid);
        }
        if (uid === 'new') {
          $('#singleservice').focus();
        }
        title = $(this).parents('[title]').attr('title');
        deps_calc(arnum, [uid], false, title);
        partition_indicators_set(arnum);
        recalc_prices(arnum);
      });
      $('.service_selector input[type=\'checkbox\'][name=\'uids:list\']').live('click', function() {
        var checkboxes, checked, i, nr_ars, title, tr, uid;
        nr_ars = parseInt($('#ar_count').val(), 10);
        tr = $(this).parents('tr');
        uid = $(this).parents('[uid]').attr('uid');
        checked = $(this).prop('checked');
        checkboxes = $(tr).find('input[type=checkbox][name!=\'uids:list\']');
        i = 0;
        while (i < checkboxes.length) {
          if (checked) {
            analysis_cb_check(i, uid);
          } else {
            analysis_cb_uncheck(i, uid);
          }
          recalc_prices(i);
          i++;
        }
        title = $(this).parents('[title]').attr('title');
        i = 0;
        while (i < nr_ars) {
          deps_calc(i, [uid], true, title);
          partition_indicators_set(i);
          i++;
        }
        if (uid === 'new') {
          $('#singleservice').focus();
        }
      });
    };
    analysis_cb_check = function(arnum, uid) {

      /* Called to un-check an Analysis' checkbox as though it were clicked.
       */
      var cb;
      cb = $('tr[uid=\'' + uid + '\'] ' + 'td[class*=\'ar\\.' + arnum + '\'] ' + 'input[type=\'checkbox\']');
      $(cb).attr('checked', true);
      analysis_cb_after_change(arnum, uid);
      state_analyses_push(arnum, uid);
      specification_apply();
    };
    analysis_cb_uncheck = function(arnum, uid) {

      /* Called to un-check an Analysis' checkbox as though it were clicked.
       */
      var cb;
      cb = $('tr[uid=\'' + uid + '\'] ' + 'td[class*=\'ar\\.' + arnum + '\'] ' + 'input[type=\'checkbox\']');
      $(cb).removeAttr('checked');
      analysis_cb_after_change(arnum, uid);
      state_analyses_remove(arnum, uid);
    };
    analysis_cb_after_change = function(arnum, uid) {

      /* If changed by click or by other trigger, all analysis checkboxes
       * must invoke this function.
       */
      var cb, checkboxes, checked, dme, nr_checked, tr;
      cb = $('tr[uid=\'' + uid + '\'] ' + 'td[class*=\'ar\\.' + arnum + '\'] ' + 'input[type=\'checkbox\']');
      tr = $(cb).parents('tr');
      checked = $(cb).prop('checked');
      checkboxes = $(tr).find('input[type=checkbox][name!=\'uids:list\']');
      nr_checked = $(checkboxes).filter(':checked');
      if (nr_checked.length === checkboxes.length) {
        $(tr).find('[name=\'uids:list\']').attr('checked', true);
      } else {
        $(tr).find('[name=\'uids:list\']').removeAttr('checked');
      }
      if (uid === $('#getDryMatterService').val() && !checked) {
        dme = $('#ReportDryMatter-' + arnum);
        $(dme).removeAttr('checked');
      }
    };
    state_analyses_push = function(arnum, uid) {
      var analyses;
      arnum = parseInt(arnum, 10);
      analyses = bika.lims.ar_add.state[arnum]['Analyses'];
      if (analyses.indexOf(uid) === -1) {
        analyses.push(uid);
        state_set(arnum, 'Analyses', analyses);
      }
    };
    state_analyses_remove = function(arnum, uid) {
      var analyses, profiles;
      arnum = parseInt(arnum, 10);
      analyses = bika.lims.ar_add.state[arnum]['Analyses'];
      if (analyses.indexOf(uid) > -1) {
        analyses.splice(analyses.indexOf(uid), 1);
        state_set(arnum, 'Analyses', analyses);
        profiles = $('div#Profiles-' + arnum + '-listing').children();
        $.each(profiles, function(i, profile) {
          var i;
          var p, p_str, profile_uid, service_uids;
          if (typeof $(profile).attr('services') !== typeof void 0 && $(profile).attr('services') !== false) {
            service_uids = $(profile).attr('services').split(',');
            if ($.inArray(uid, service_uids) !== -1) {
              profile_uid = $(profile).attr('uid');
              $(profile).remove();
              p = $('#Profiles-' + arnum).attr('uid').split(',');
              p = $.grep(p, function(value) {
                return value !== profile_uid;
              });
              i = void 0;
              p_str = '';
              i = p.length - 1;
              while (i >= 0) {
                p_str = p_str + ',' + p[i];
                i--;
              }
              $('#Profiles-' + arnum).attr('uid', p_str);
              $('#Profiles-' + arnum).attr('uid_check', p_str);
              $('#Profiles-' + arnum + '_uid').val(p_str);
            }
          }
        });
        recalc_prices(arnum);
      }
    };

    /*
     deps_calc                  - the main routine for dependencies/dependants
     dependencies_add_confirm   - adding dependancies to the form/state: confirm
     dependancies_add_yes       - clicked yes
     dependencies_add_no        - clicked no
     */
    deps_calc = function(arnum, uids, skip_confirmation, initiator) {

      /* Calculate dependants and dependencies.
       *
       * arnum - the column number.
       * uids - zero or more service UIDs to calculate
       * skip_confirmation - assume yes instead of confirmation dialog
       * initiator - the service or control that initiated this check.
       *             used for a more pretty dialog box header.
       */
      var Dep, Dependants, Dependencies, _, cb, dep_element, dep_services, dep_titles, element, i, lims, n, uid;
      jarn.i18n.loadCatalog('bika');
      _ = window.jarn.i18n.MessageFactory('bika');
      Dep = void 0;
      i = void 0;
      cb = void 0;
      dep_element = void 0;
      lims = window.bika.lims;
      dep_services = [];
      dep_titles = [];
      n = 0;
      while (n < uids.length) {
        uid = uids[n];
        if (uid === 'new') {
          n++;
          continue;
        }
        element = $('tr[uid=\'' + uids[n] + '\'] ' + 'td[class*=\'ar\\.' + arnum + '\'] ' + 'input[type=\'checkbox\']');
        initiator = $(element).parents('[title]').attr('title');
        if ($(element).prop('checked')) {
          Dependencies = lims.AnalysisService.Dependencies(uid);
          i = 0;
          while (i < Dependencies.length) {
            Dep = Dependencies[i];
            dep_element = $('tr[uid=\'' + Dep['Service_uid'] + '\'] ' + 'td[class*=\'ar\\.' + arnum + '\'] ' + 'input[type=\'checkbox\']');
            if (!$(dep_element).prop('checked')) {
              dep_titles.push(Dep['Service']);
              dep_services.push(Dep);
            }
            i++;
          }
          if (dep_services.length > 0) {
            if (skip_confirmation) {
              dependancies_add_yes(arnum, dep_services);
            } else {
              dependencies_add_confirm(initiator, dep_services, dep_titles).done(function(data) {
                dependancies_add_yes(arnum, dep_services);
              }).fail(function(data) {
                dependencies_add_no(arnum, uid);
              });
            }
          }
        } else {
          Dependants = lims.AnalysisService.Dependants(uid);
          i = 0;
          while (i < Dependants.length) {
            Dep = Dependants[i];
            dep_element = $('tr[uid=\'' + Dep['Service_uid'] + '\'] ' + 'td[class*=\'ar\\.' + arnum + '\'] ' + 'input[type=\'checkbox\']');
            if ($(dep_element).prop('checked')) {
              dep_titles.push(Dep['Service']);
              dep_services.push(Dep);
            }
            i++;
          }
          if (dep_services.length > 0) {
            if (skip_confirmation) {
              dependants_remove_yes(arnum, dep_services);
            } else {
              dependants_remove_confirm(initiator, dep_services, dep_titles).done(function(data) {
                dependants_remove_yes(arnum, dep_services);
              }).fail(function(data) {
                dependants_remove_no(arnum, uid);
              });
            }
          }
        }
        n++;
      }
    };
    dependants_remove_confirm = function(initiator, dep_services, dep_titles) {
      var d;
      d = $.Deferred();
      $('body').append('<div id=\'messagebox\' style=\'display:none\' title=\'' + _('Service dependencies') + '\'>' + _('<p>The following services depend on ${service}, and will be unselected if you continue:</p><br/><p>${deps}</p><br/><p>Do you want to remove these selections now?</p>', {
        service: initiator,
        deps: dep_titles.join('<br/>')
      }) + '</div>');
      $('#messagebox').dialog({
        width: 450,
        resizable: false,
        closeOnEscape: false,
        buttons: {
          yes: function() {
            d.resolve();
            $(this).dialog('close');
            $('#messagebox').remove();
          },
          no: function() {
            d.reject();
            $(this).dialog('close');
            $('#messagebox').remove();
          }
        }
      });
      return d.promise();
    };
    dependants_remove_yes = function(arnum, dep_services) {
      var Dep, i, uid;
      i = 0;
      while (i < dep_services.length) {
        Dep = dep_services[i];
        uid = Dep['Service_uid'];
        analysis_cb_uncheck(arnum, uid);
        i += 1;
      }
      _partition_indicators_set(arnum);
    };
    dependants_remove_no = function(arnum, uid) {
      analysis_cb_check(arnum, uid);
      _partition_indicators_set(arnum);
    };
    dependencies_add_confirm = function(initiator_title, dep_services, dep_titles) {

      /*
       uid - this is the analysisservice checkbox which was selected
       dep_services and dep_titles are the calculated dependencies
       initiator_title is the dialog title, this could be a service but also could
       be "Dry Matter" or some other name
       */
      var d, html;
      d = $.Deferred();
      html = '<div id=\'messagebox\' style=\'display:none\' title=\'' + _('Service dependencies') + '\'>';
      html = html + _('<p>${service} requires the following services to be selected:</p>' + '<br/><p>${deps}</p><br/><p>Do you want to apply these selections now?</p>', {
        service: initiator_title,
        deps: dep_titles.join('<br/>')
      });
      html = html + '</div>';
      $('body').append(html);
      $('#messagebox').dialog({
        width: 450,
        resizable: false,
        closeOnEscape: false,
        buttons: {
          yes: function() {
            d.resolve();
            $(this).dialog('close');
            $('#messagebox').remove();
          },
          no: function() {
            d.reject();
            $(this).dialog('close');
            $('#messagebox').remove();
          }
        }
      });
      return d.promise();
    };
    dependancies_add_yes = function(arnum, dep_services) {

      /*
       Adding required analyses to this AR - Clicked "yes" to confirmation,
       or if confirmation dialog is skipped, this function is called directly.
       */
      var Dep, dep_cb, i, uid;
      i = 0;
      while (i < dep_services.length) {
        Dep = dep_services[i];
        uid = Dep['Service_uid'];
        dep_cb = $('tr[uid=\'' + uid + '\'] ' + 'td[class*=\'ar\\.' + arnum + '\'] ' + 'input[type=\'checkbox\']');
        if (dep_cb.length > 0) {
          if ($(dep_cb).prop('checked')) {
            i++;
            continue;
          }
        } else {
          singleservice_duplicate(Dep['Service_uid'], Dep['Service'], Dep['Keyword'], Dep['Price'], Dep['VAT']);
        }
        analysis_cb_check(arnum, uid);
        i++;
      }
      recalc_prices(arnum);
      _partition_indicators_set(arnum);
    };
    dependencies_add_no = function(arnum, uid) {

      /*
       Adding required analyses to this AR - clicked "no" to confirmation.
       This is just responsible for un-checking the service that was
       used to invoke this routine.
       */
      var element;
      element = $('tr[uid=\'' + uid + '\'] td[class*=\'ar\\.' + arnum + '\'] input[type=\'checkbox\']');
      if ($(element).prop('checked')) {
        analysis_cb_uncheck(arnum, uid);
      }
      _partition_indicators_set(arnum);
    };

    /* partnrs_calc calls the ajax url, and sets the state variable
     * partition_indicators_set calls partnrs_calc, and modifies the form.
     * partition_indicators_from_template set state partnrs from template
     * _partition_indicators_set actually does the form/ui work
     */
    partnrs_calc = function(arnum) {

      /* Configure the state partition data with an ajax call
       * - calls to /calculate_partitions json url
       *
       */
      var cacheKey, d, data, request_data, service_uids, st_uid;
      d = $.Deferred();
      arnum = parseInt(arnum, 10);
      st_uid = bika.lims.ar_add.state[arnum]['SampleType'];
      service_uids = bika.lims.ar_add.state[arnum]['Analyses'];
      if (!st_uid || !service_uids) {
        d.resolve();
        return d.promise();
      }
      request_data = {
        services: service_uids.join(','),
        sampletype: st_uid,
        _authenticator: $('input[name=\'_authenticator\']').val()
      };
      $('input[name="save_button"]').prop('disabled', true);
      window.jsonapi_cache = window.jsonapi_cache || {};
      cacheKey = $.param(request_data);
      if (typeof window.jsonapi_cache[cacheKey] === 'undefined') {
        $.ajax({
          type: 'POST',
          dataType: 'json',
          url: window.portal_url + '/@@API/calculate_partitions',
          data: request_data,
          success: function(data) {
            if (data.success === false) {
              bika.lims.log('Error while calculating partitions: ' + data.message);
            } else {
              window.jsonapi_cache[cacheKey] = data;
              bika.lims.ar_add.state[arnum]['Partitions'] = data['parts'];
            }
            $('input[name="save_button"]').prop('disabled', false);
            d.resolve();
          }
        });
      } else {
        data = window.jsonapi_cache[cacheKey];
        bika.lims.ar_add.state[arnum]['Partitions'] = data['parts'];
        $('input[name="save_button"]').prop('disabled', false);
        d.resolve();
      }
      return d.promise();
    };
    _partition_indicators_set = function(arnum) {
      var cb, checkboxes, n, p, partnr, parts, span, uid;
      arnum = parseInt(arnum, 10);
      parts = bika.lims.ar_add.state[arnum]['Partitions'];
      if (!parts) {
        return;
      }
      checkboxes = $('tr[uid] td[class*=\'ar\\.' + arnum + '\'] ' + 'input[type=\'checkbox\'][name!=\'uids:list\']');
      n = 0;
      while (n < checkboxes.length) {
        cb = checkboxes[n];
        span = $(cb).parents('[class*=\'ar\\.\']').find('.partnr');
        uid = $(cb).parents('[uid]').attr('uid');
        if ($(cb).prop('checked')) {
          partnr = 1;
          p = 0;
          while (p < parts.length) {
            if (parts[p]['services'].indexOf(uid) > -1) {
              if (parts[p]['part_id']) {
                partnr = parts[p]['part_id'].split('-')[1];
              } else {
                partnr = p + 1;
              }
              break;
            }
            p++;
          }
          $(span).html(partnr);
        } else {
          $(span).html('&nbsp;');
        }
        n++;
      }
    };
    partition_indicators_set = function(arnum, skip_calculation) {

      /* Calculate and Set partition indicators
       * set skip_calculation if the state variable already contains
       * calculated partitions (eg, when setting template)
       */
      if (skip_calculation) {
        _partition_indicators_set(arnum);
      } else {
        partnrs_calc(arnum).done(function() {
          _partition_indicators_set(arnum);
        });
      }
    };
    recalc_prices = function(arnum) {
      var ardiscount_amount, arprofiles_price, arprofiles_vat_amount, arservice_vat_amount, arservices_price, base_price, cb, checked, i, member_discount, member_discount_applies, profiles, service_price, service_vat_amount, services_from_priced_profile, subtotal, total, vat_amount;
      console.debug("recalc_prices::arnum=" + arnum);
      ardiscount_amount = 0.00;
      arservices_price = 0.00;
      checked = $('tr[uid] td[class*=\'ar\\.' + arnum + '\'] input[type=\'checkbox\']:checked');
      member_discount = parseFloat($('#bika_setup').attr('MemberDiscount'));
      member_discount_applies = $.parseJSON($('#bika_setup').attr('MemberDiscountApplies'));
      profiles = $('div#Profiles-' + arnum + '-listing').children();
      arprofiles_price = 0.00;
      arprofiles_vat_amount = 0.00;
      arservice_vat_amount = 0.00;
      services_from_priced_profile = [];

      /* ANALYSIS PROFILES PRICE */
      $.each(profiles, function(i, profile) {
        var profile_price, profile_service_uids, profile_vat;
        if ($(profile).attr('useprice') === 'true') {
          profile_service_uids = $(profile).attr('services').split(',');
          profile_price = parseFloat($(profile).attr('price'));
          profile_vat = parseFloat($(profile).attr('VATAmount'));
          arprofiles_price += profile_price;
          arprofiles_vat_amount += profile_vat;
          $.each(profile_service_uids, function(i, el) {
            if ($.inArray(el, services_from_priced_profile) === -1) {
              services_from_priced_profile.push(el);
            }
          });
        }
      });

      /* ANALYSIS SERVICES PRICE */
      i = 0;
      while (i < checked.length) {
        cb = checked[i];
        if ($(cb).prop('checked') && !$(cb).prop('disabled') && typeof $(cb).prop('disabled') !== 'undefined' && services_from_priced_profile.indexOf($(cb).attr('uid')) < 0) {
          service_price = parseFloat($(cb).parents('[price]').attr('price'));
          service_vat_amount = parseFloat($(cb).parents('[vat_percentage]').attr('vat_percentage'));
          arservice_vat_amount += service_price * service_vat_amount / 100;
          arservices_price += service_price;
        }
        i++;
      }
      base_price = arservices_price + arprofiles_price;
      if (member_discount && member_discount_applies) {
        console.debug("Member discount applies with " + member_discount + "%");
        ardiscount_amount = base_price * member_discount / 100;
      }
      subtotal = base_price - ardiscount_amount;
      vat_amount = arprofiles_vat_amount + arservice_vat_amount;
      total = subtotal + vat_amount;
      $('td[arnum=\'' + arnum + '\'] span.price.discount').html(ardiscount_amount.toFixed(2));
      $('td[arnum=\'' + arnum + '\'] span.price.subtotal').html(subtotal.toFixed(2));
      $('td[arnum=\'' + arnum + '\'] span.price.vat').html(vat_amount.toFixed(2));
      $('td[arnum=\'' + arnum + '\'] span.price.total').html(total.toFixed(2));
    };
    set_state_from_form_values = function() {
      var arnum, cblist, error, max, min, nr_ars, rr, services, specs, uid;
      nr_ars = parseInt($('#ar_count').val(), 10);
      $.each($('td[arnum][hidden] input[type="hidden"]'), function(i, e) {
        var arnum, fieldname, value;
        arnum = get_arnum(e);
        fieldname = $(e).parents('[fieldname]').attr('fieldname');
        value = $(e).attr('uid') ? $(e).attr('uid') : $(e).val();
        if (fieldname) {
          state_set(arnum, fieldname, value);
          state_set(arnum, fieldname + '_hidden', true);
        }
      });
      $.each($('td[arnum] input[type="text"], td[arnum] input.referencewidget').not('[class^="rejectionwidget-input"]'), function(i, e) {
        var arnum, fieldname, value;
        arnum = $(e).parents('[arnum]').attr('arnum');
        fieldname = $(e).parents('[fieldname]').attr('fieldname');
        value = $(e).attr('uid') ? $(e).attr('uid') : $(e).val();
        state_set(arnum, fieldname, value);
      });
      $.each($('[ar_add_ar_widget] input[type="checkbox"]').not('[class^="rejectionwidget-checkbox"]'), function(i, e) {
        var arnum, fieldname, value;
        arnum = get_arnum(e);
        fieldname = $(e).parents('[fieldname]').attr('fieldname');
        value = $(e).prop('checked');
        state_set(arnum, fieldname, value);
      });
      $.each($('td[arnum] select').not('[class^="rejectionwidget-multiselect"]'), function(i, e) {
        var arnum, fieldname, value;
        arnum = get_arnum(e);
        fieldname = $(e).parents('[fieldname]').attr('fieldname');
        value = $(e).val();
        state_set(arnum, fieldname, value);
      });
      uid = void 0;
      arnum = void 0;
      services = void 0;
      arnum = 0;
      while (arnum < nr_ars) {
        services = [];
        cblist = $('.service_selector td[class*="ar\\.' + arnum + '"] input[type="checkbox"]').filter(':checked');
        $.each(cblist, function(i, e) {
          uid = $(e).parents('[uid]').attr('uid');
          services.push(uid);
        });
        state_set(arnum, 'Analyses', services);
        arnum++;
      }
      rr = void 0;
      specs = void 0;
      min = void 0;
      max = void 0;
      error = void 0;
      arnum = 0;
      while (arnum < nr_ars) {
        rr = bika.lims.ar_add.state[arnum]['ResultsRange'];
        if (rr !== void 0) {
          specs = hashes_to_hash(rr, 'uid');
          $.each($('.service_selector td[class*=\'ar\\.' + arnum + '\'] .after'), function(i, e) {
            var keyword;
            uid = $(e).parents('[uid]').attr('uid');
            keyword = $(e).parents('[keyword]').attr('keyword');
            if (uid !== 'new' && uid !== void 0) {
              min = $(e).find('.min');
              max = $(e).find('.max');
              error = $(e).find('.error');
              if (specs[uid] === void 0) {
                specs[uid] = {
                  'min': $(min).val(),
                  'max': $(max).val(),
                  'error': $(error).val(),
                  'uid': uid,
                  'keyword': keyword
                };
              } else {
                specs[uid].min = $(min) ? $(min).val() : specs[uid].min;
                specs[uid].max = $(max) ? $(max).val() : specs[uid].max;
                specs[uid].error = $(error) ? $(error).val() : specs[uid].error;
              }
            }
          });
          state_set(arnum, 'ResultsRange', hash_to_hashes(specs));
        }
        arnum++;
      }
    };
    form_submit = function() {
      $('[name=\'save_button\']').click(function(event) {
        var request_data;
        event.preventDefault();
        set_state_from_form_values();
        request_data = {
          _authenticator: $('input[name=\'_authenticator\']').val(),
          state: $.toJSON(bika.lims.ar_add.state)
        };
        $.ajax({
          type: 'POST',
          dataType: 'json',
          url: window.location.href.split('/portal_factory')[0] + '/analysisrequest_submit',
          data: request_data,
          success: function(data) {
            var destination;

            /*
             * data contains the following useful keys:
             * - errors: any errors which prevented the AR from being created
             *   these are displayed immediately and no further ation is taken
             * - destination: the URL to which we should redirect on success.
             *   This includes GET params for printing labels, so that we do not
             *   have to care about this here.
             */
            var ars, destination, e, error, msg, q, stickertemplate, x;
            if (data['errors']) {
              msg = '';
              for (error in data.errors) {
                x = error.split('.');
                e = void 0;
                if (x.length === 2) {
                  e = x[1] + ', AR ' + +x[0] + ': ';
                } else if (x.length === 1) {
                  e = x[0] + ': ';
                } else {
                  e = '';
                }
                msg = msg + e + data.errors[error] + '<br/>';
              }
              window.bika.lims.portalMessage(msg);
              window.scroll(0, 0);
            } else if (data['stickers']) {
              destination = window.location.href.split('/portal_factory')[0];
              ars = data['stickers'];
              stickertemplate = data['stickertemplate'];
              q = '/sticker?autoprint=1&template=' + stickertemplate + '&items=' + ars.join(',');
              window.location.replace(destination + q);
            } else {
              destination = window.location.href.split('/portal_factory')[0];
              window.location.replace(destination);
            }
          }
        });
      });
    };
    fix_table_layout = function() {
      'use strict';
      var arcolswidth, headcolwidth;
      headcolwidth = $('table.analysisrequest.add tr:first th').width();
      headcolwidth += $('table.analysisrequest.add tr:first td:first').width();
      $('table tr th input[id*="_toggle_cols"]').closest('th').css('width', 24);
      $('table tr th[id="foldercontents-Title-column"]').css('width', headcolwidth);
      $('table tr[id^="folder-contents-item-"] td[class*="Title"]').css('width', headcolwidth);
      arcolswidth = $('table.analysisrequest td[arnum]').width();
      $('table tr th[id^="foldercontents-ar."]').css({
        'width': arcolswidth,
        'text-align': 'center'
      });
      $('table tr[id^="folder-contents-item-"] td[class*="ar"]').css({
        'width': arcolswidth,
        'text-align': 'center'
      });
    };
    'use strict';
    that = this;
    that.load = function() {
      console.debug("*** LOADING AR FORM CONTROLLER ***");
      $('input[type=text]').prop('autocomplete', 'off');
      form_init();

      /*
       The state variable is fully populated when the form is submitted,
       but in many cases it must be updated on the fly, to allow the form
       to change behaviour based on some selection.  To help with this,
       there are some generic state-setting handlers below, but these must
       be augmented with specific handlers for difficult cases.
       */
      checkbox_change();
      referencewidget_change();
      rejectionwidget_change();
      select_element_change();
      textinput_change();
      textarea_change();
      copybutton_selected();
      client_selected();
      contact_selected();
      cc_contacts_deletebtn_click();
      spec_field_entry();
      spec_selected();
      samplepoint_selected();
      sampletype_selected();
      profile_selected();
      profile_unset_trigger();
      template_selected();
      drymatter_selected();
      sample_selected();
      singleservice_dropdown_init();
      singleservice_deletebtn_click();
      analysis_cb_click();
      category_header_clicked();
      form_submit();
      fix_table_layout();
      from_sampling_round();
    };

    /*
     * Exposes the filter_combogrid method publicly.
     * Accessible through window.bika.lims.AnalysisRequestAddByCol.filter_combogrid
     */
    that.filter_combogrid = function(element, filterkey, filtervalue, querytype) {
      filter_combogrid(element, filterkey, filtervalue, querytype);
    };
  };

}).call(this);
