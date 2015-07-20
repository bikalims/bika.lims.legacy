from bika.lims import bikaMessageFactory as _, t
from bika.lims import logger
from bika.lims.browser import BrowserView
from bika.lims.config import POINTS_OF_CAPTURE
from bika.lims.idserver import renameAfterCreation
from bika.lims.interfaces import IResultOutOfRange
from bika.lims.utils import isnumber
from bika.lims.utils import to_utf8, encode_header, createPdf, attachPdf
from bika.lims.utils import to_utf8, formatDecimalMark, format_supsub
from bika.lims.utils.analysis import format_uncertainty
#from bika.lims.vocabularies import getARReportTemplates
from DateTime import DateTime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.Utils import formataddr
from operator import itemgetter
from os.path import join
from plone.resource.utils import iterDirectoriesOfType, queryResourceDirectory
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFPlone.utils import safe_unicode, _createObjectByType
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from smtplib import SMTPServerDisconnected, SMTPRecipientsRefused
from zope.component import getAdapters, getUtility
from plone.registry.interfaces import IRegistry

import App
import glob, os, sys, traceback
import Globals
import re
import tempfile
import urllib2

class OrderPublishView(BrowserView):
    template = ViewPageTemplateFile("templates/order_publish.pt")
    _products = []
    _current_product_index = 0
    _publish = False

    def __init__(self, context, request, publish=False):
        super(OrderPublishView, self).__init__(context, request)
        self._publish = publish
        self._products = [self.context]

    @property
    def _DEFAULT_TEMPLATE(self):
        registry = getUtility(IRegistry)
        return registry.get(
            'bika.lims.order.default_order_template', 'default.pt')

    def __call__(self):
        if self.context.portal_type == 'Order':
            self._products = [self.context]
        elif self.context.portal_type == 'OrderFolder' \
            and self.request.get('items',''):
            uids = self.request.get('items').split(',')
            uc = getToolByName(self.context, 'uid_catalog')
            self._products = [obj.getObject() for obj in uc(UID=uids)]
        else:
            #Do nothing
            self.destination_url = self.request.get_header("referer",
                                   self.context.absolute_url())

        # Do publish?
        if self.request.form.get('publish', '0') == '1':
            self.publishFromPOST()
        else:
            return self.template()

    def showOptions(self):
        """ Returns true if the options top panel will be displayed
            in the template
        """
        return self.request.get('pub', '1') == '1';

    def getOrderTemplate(self):
        templates_dir = 'templates/sheets'
        embedt = self.request.form.get('template', self._DEFAULT_TEMPLATE)
        if embedt.find(':') >= 0:
            prefix, template = embedt.split(':')
            templates_dir = queryResourceDirectory('sheets', prefix).directory
            embedt = template
        embed = ViewPageTemplateFile(os.path.join(templates_dir, embedt))
        reptemplate = ""
        try:
            reptemplate = embed(self)
        except:
            tbex = traceback.format_exc()
            arid = self._products[self._current_product_index].id
            reptemplate = "<div class='error-report'>%s - %s '%s':<pre>%s</pre></div>" % (arid, _("Unable to load the template"), embedt, tbex)
        self._nextProduct()
        return reptemplate

    def getOrderSheetStyle(self):
        """ Returns the css style to be used for the current template.
            If the selected template is 'default.pt', this method will
            return the content from 'default.css'. If no css file found
            for the current template, returns empty string
        """
        template = self.request.form.get('template', self._DEFAULT_TEMPLATE)
        content = ''
        if template.find(':') >= 0:
            prefix, template = template.split(':')
            resource = queryResourceDirectory('sheets', prefix)
            css = '{0}.css'.format(template[:-3])
            if css in resource.listDirectory():
                content = resource.readFile(css)
        else:
            this_dir = os.path.dirname(os.path.abspath(__file__))
            templates_dir = os.path.join(this_dir, 'templates/sheets/')
            path = '%s/%s.css' % (templates_dir, template[:-3])
            with open(path, 'r') as content_file:
                content = content_file.read()
        return content

    def getProducts(self):
        """ Returns a dict with the order entries
        """
        return self._products;

    def getProductsCount(self):
        """ Returns the number of product orders to manage
        """
        return len(self._products);

    def getOrderObj(self):
        """ Returns the order obj
        """
        return self._products[self._current_product_index]

    def getOrder(self):
        """ Returns the dict for the current product
        """
        return self._order_data(self._products[self._current_product_index])

    def _nextProduct(self):
        """ Move to the next product
        """
        if self._current_product_index < len(self._products):
            self._current_product_index += 1

    def _order_data(self, order, excludearuids=[]):
        """ Creates an order dict, accessible from the view and from each
            specific template.
        """
         
        data = {'obj': order,
                'id': order.getId(),
                'order_number': order.getOrderNumber(),
                'title': order.Title(),
                'description': order.Description(),
                'supplier_id': order.getSupplierUID(),
                'date_dispatched': self.ulocalized_time(order.getDateDispatched(), long_format=1),
                'remarks': order.getRemarks(),
                'date_published': self.ulocalized_time(DateTime(), long_format=1),
                'subtotal': order.getSubtotal(),
                'vat_amount': order.getVATAmount(),
                'url': order.absolute_url(),
                'remarks': to_utf8(order.getRemarks()),
                'footer': to_utf8(self.context.bika_setup.getResultFooter()),
                }

        data['supplier'] = self._supplier_data(order)

        # Get the Product List for the Order
        # print order.order_lineitems
        items = order.order_lineitems
        products = order.aq_parent.objectValues('Product')
        item_list = []
        grand_total = 0.00
        for item in items:
            withvat_price = 0.00
            prodid = item['Product']
            product = [pro for pro in products if pro.getId() == prodid][0]
            price = float(item['Price'])
            vat = float(item['VAT'])
            qty = float(item['Quantity'])
            withvat_price = price * qty * ((vat /100) + 1)
            item_list.append({
                'title': product.Title(),
                'description': product.Description(),
                'unit': product.getUnit(),
                'price': price,
                'vat': '%s%%' % vat,
                'quantity': qty,
                'subtotal': '%.2f' % (price * qty),
                'withvat' : '%.2f' % (withvat_price)
            })
            grand_total += withvat_price
        item_list = sorted(item_list, key = itemgetter('title'))

        data['products'] = item_list
        data["grandTotal"] = '%.2f' % grand_total
        return data

    def _supplier_data(self, order):
        data = {}
        supplier = order.aq_parent
        if supplier:
            data['obj'] = supplier
            data['id'] = supplier.id
            data['title'] = supplier.Title()
            data['url'] = supplier.absolute_url()
            data['name'] = to_utf8(supplier.getName())
            data['phone'] = to_utf8(supplier.getPhone())
            data['fax'] = to_utf8(supplier.getFax())

            supplier_address = supplier.getPostalAddress()
            if supplier_address:
                _keys = ['address', 'city', 'state', 'zip', 'country']
                _list = ["<div>%s</div>" % supplier_address.get(v) for v in _keys
                         if supplier_address.get(v)]
                supplier_address = "".join(_list)
            else:
                supplier_address = ''
            data['address'] = to_utf8(supplier_address)
            data['email'] = to_utf8(supplier.getEmailAddress())
        return data


    def localise_images(self, htmlreport):
        """WeasyPrint will attempt to retrieve attachments directly from the URL
        referenced in the HTML report, which may refer back to a single-threaded
        (and currently occupied) zeoclient, hanging it.  All "attachments"
        using urls ending with at_download/AttachmentFile must be converted
        to local files.

        Returns a list of files which were created, and a modified copy
        of htmlreport.
        """
        cleanup = []

        _htmltext = to_utf8(htmlreport)
        # first regular image tags
        for match in re.finditer("""http.*at_download\/AttachmentFile""", _htmltext, re.I):
            url = match.group()
            att_path = url.replace(self.portal_url+"/", "")
            attachment = self.portal.unrestrictedTraverse(att_path)
            af = attachment.getAttachmentFile()
            filename = af.filename
            extension = "."+filename.split(".")[-1]
            outfile, outfilename = tempfile.mkstemp(suffix=extension)
            outfile = open(outfilename, 'wb')
            outfile.write(str(af.data))
            outfile.close()
            _htmltext.replace(url, outfilename)
            cleanup.append(outfilename)
        return cleanup, _htmltext

    def publishFromPOST(self):
        html = self.request.form.get('html')
        style = self.request.form.get('style')
        uid = self.request.form.get('uid')
        reporthtml = "<html><head>%s</head><body><div id='report'>%s</body></html>" % (style, html);
        return self.publishFromHTML(uid, safe_unicode(reporthtml).encode('utf-8'));

    def publishFromHTML(self, prouid, results_html):

        uc = getToolByName(self.context, 'uid_catalog')
        pros = uc(UID=prouid)
        if not pros or len(pros) != 1:
            return []

        pro = pros[0].getObject();
        
        # HTML written to debug file
        debug_mode = App.config.getConfiguration().debug_mode
        if debug_mode:
            tmp_fn = tempfile.mktemp(suffix=".html")
            logger.debug("Writing HTML for %s to %s" % (pro.Title(), tmp_fn))
            open(tmp_fn, "wb").write(results_html)

        # Create the pdf report (will always be attached to the Order)
        # we must supply the file ourself so that createPdf leaves it alone.
        # This version replaces 'attachment' links; probably not required,
        # so it's repeated below, without these localise_images.
        # cleanup, results_html_for_pdf = self.localise_images(results_html)
        # pdf_fn = tempfile.mktemp(suffix=".pdf")
        # pdf_report = createPdf(htmlreport=results_html_for_pdf, outfile=pdf_fn)
        # for fn in cleanup:
        #     os.remove(fn)

        
        pdf_fn = tempfile.mktemp(suffix=".pdf")
        pdf_report = createPdf(htmlreport=results_html, outfile=pdf_fn)

        # PDF written to debug file
        if debug_mode:
            logger.debug("Writing PDF for %s to %s" % (pro.Title(), pdf_fn))
        else:
            os.remove(pdf_fn)

        recipients = []
        

        # Send report to supplier
        supplier_data = self._supplier_data(pro)
        title = encode_header(supplier_data.get('title', ''))
        email = supplier_data.get('email')
        formatted = formataddr((title, email))

        # Create the new mime_msg object
        mime_msg = MIMEMultipart('related')
        mime_msg['Subject'] = self.get_mail_subject(pro)
        """
        	Edit this to change the From address
        	mime_msg['From'] = formataddr(
        	(encode_header(lab.getName()), lab.getEmailAddress()))
        """
        mime_msg['From'] = formataddr(("BIKA IMM", "imm@bika.com"))
        mime_msg.preamble = 'This is a multi-part MIME message.'
        msg_txt = MIMEText(results_html, _subtype='html')
        mime_msg.attach(msg_txt)
        mime_msg['To'] = formatted

        # Attach the pdf to the email if requested
        if pdf_report:
            attachPdf(mime_msg, pdf_report, pdf_fn)

        msg_string = mime_msg.as_string()

        # content of outgoing email written to debug file
        if debug_mode:
            tmp_fn = tempfile.mktemp(suffix=".email")
            logger.debug("Writing MIME message for %s to %s" % (pro.Title(), tmp_fn))
            open(tmp_fn, "wb").write(msg_string)

        try:
            host = getToolByName(pro, 'MailHost')
            host.send(msg_string, immediate=True)
        except SMTPServerDisconnected as msg:
            logger.warn("SMTPServerDisconnected: %s." % msg)
        except SMTPRecipientsRefused as msg:
            raise WorkflowException(str(msg))

        pro.setDateDispatched(DateTime())
        return [pro]

    def publish(self):
        """ Publish the Order. Generates a results pdf file
            associated, sends an email with the report to
            the lab manager and sends a notification (usually an email
            with the PDF attached) to the Supplier's contact and CCs.
            
        """
        if len(self._products) > 1:
            published_products = []
            for pro in self._products:
                propub = OrderPublishView(pro, self.request, publish=True)
                pro = propub.publish()
                published_products.extend(pro)
            published_products = [ppro.id for ppro in published_products]
            return published_products

        results_html = safe_unicode(self.template()).encode('utf-8')
        return self.publishFromHTML(results_html)


    def get_mail_subject(self, ar):
        """ Returns the email subject
        """
        supplier = ar.aq_parent
        subject ="Order Details: %s" % (ar.getDateDispatched())
        return subject
