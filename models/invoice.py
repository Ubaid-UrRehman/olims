from openerp.tools.translate import _
from datetime import date
from openerp import fields, models, api
from base_olims_model import BaseOLiMSModel
from fields.string_field import StringField
from fields.text_field import TextField
from fields.boolean_field import BooleanField
from fields.date_time_field import DateTimeField
from fields.file_field import FileField
from fields.reference_field import ReferenceField
from fields.widget.widget import StringWidget, TextAreaWidget, BooleanWidget, FileWidget, DateTimeWidget
import datetime

schema = (StringField(string='title',required=1),
    StringField(string='InvoiceNumber',
                compute='_ComputeInvoiceId',
                required=0),
    fields.Many2one(string='Client',
        required=0,
        comodel_name='olims.client',
    ),
    DateTimeField('Invoice Date',
    ),

    DateTimeField('StartDate',
        required=1,
        default_method='current_date',
        widget=DateTimeWidget(
            label=_("Date"),
        ),
    ),
    DateTimeField('EndDate',
        required=1,
        default_method='end_date',
        widget=DateTimeWidget(
            label=_("End Date"),
        ),
    ),
    TextField('Remarks',
        searchable=True,
        widget=TextAreaWidget(
            label=_("Remarks"),
            append_only=True,
        ),
    ),

    fields.Float(string='Subtotal',
        compute='_getSubtotal'
    ),
    fields.Float(string='VAT',
        compute='_getVATAmount',
    ),
    fields.Float('Total',
        compute='_getTotal',
    ),
    fields.Many2one(string='Order_id',
        comodel_name='olims.supply_order',
    ),
)

class Invoice(models.Model, BaseOLiMSModel):
    _name='olims.invoice'
    _rec_name = 'title'

    def _ComputeInvoiceId(self):
        for record in self:
            invoiceid = 'I-0' + str(record.id)
            record.InvoiceNumber = invoiceid
    @api.model
    def create(self, values):
        order_date1 = datetime.datetime.strptime(values.get('StartDate'), "%Y-%m-%d %H:%M:%S")
        order_date2 = datetime.datetime.strptime(values.get('EndDate'), "%Y-%m-%d %H:%M:%S")

        stringdate1 = order_date1.strftime("%Y-%m-%d %H:%M:%S")
        stringdate2 = order_date2.strftime("%Y-%m-%d %H:%M:%S")
        order_object = self.env['olims.supply_order']

        order_object_ids = order_object.search([('DateDispatched', '>=', stringdate1),('DateDispatched', '<=', stringdate2)])
        if order_object_ids:
            for obj in order_object_ids:
                line = order_object.browse(obj.id)
                client_id = line.Client.id #.encode('ascii','ignore')
                supply_order_value_dict = {'Invoice Date': datetime.datetime.now(),
                                           'Client': client_id,
                                           'Order_id' : line.id
                                           }
                values.update(supply_order_value_dict)
                res = super(Invoice, self).create(values)
            return res
        else:
            res = super(Invoice, self).create(values)
            return res

    _at_rename_after_creation = True


    def _getSubtotal(self):
        """ Compute Subtotal """
        for record in self:
            total = record.Order_id.SubTotal
            record.Subtotal = total

    def _getVATAmount(self):
        """ Compute VAT """
        for record in self:
            
            record.VAT = record.Order_id.VAT


    def _getTotal(self):
        """ Compute Total """
        for record in self:
            record.Total = record.Order_id.Total

class ARInvoice(models.Model):
    _name = "olims.ar_invoice"

    name = fields.Char(string="Invoice Id", compute="_compute_invoice_id",
        store=True)
    receipt_number = fields.Char(string="Receipt Number", compute="_compute_receipt_number",
        store=True)
    client_id = fields.Many2one(string="Client",comodel_name="olims.client")
    analysis_request_id = fields.Many2many(string="Analysis Request ID",
        comodel_name="olims.analysis_request")
    start_date = fields.Datetime(string="Start Date")
    end_date = fields.Datetime(string="Start Date")
    sub_total = fields.Float(string="Sub Total", compute='_get_subtotal', store=True)
    total = fields.Float(string="Total Amount", compute='_get_total', store=True)

    @api.depends("client_id")
    def _compute_invoice_id(self):
        for record in self:
            if record.id < 10:
                record.name = "INV-0"+str(record.id)
            else:
                record.name = "INV-"+str(record.id)

    @api.depends("client_id")
    def _compute_receipt_number(self):
        for record in self:
            record.receipt_number = "1000"+str(record.id)

    @api.depends("client_id","analysis_request_id")
    def _get_subtotal(self):
        for record in self:
            for ar_record in record.analysis_request_id:
                record.sub_total += ar_record.Subtotal

    @api.depends("analysis_request_id")
    def _get_total(self):
        for record in self:
            for ar_record in record.analysis_request_id:
                record.total += ar_record.Total

    @api.model
    def create(self, values):
        res = super(ARInvoice,self).create(values)
        if values.get('analysis_request_id',None):
            analysis_request = values.get('analysis_request_id')[0]
            ar_object = self.env["olims.analysis_request"].search([('id', 'in', analysis_request[2])])
            ar_object.write({'ar_invoice_id': res.id})
        return res

Invoice.initialze(schema)