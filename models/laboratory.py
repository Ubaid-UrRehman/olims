from openerp import fields, models, api
from base_olims_model import BaseOLiMSModel
from fields.string_field import StringField
from fields.integer_field import IntegerField
from fields.boolean_field import BooleanField
from fields.file_field import FileField
from fields.widget.widget import StringWidget, BooleanWidget, IntegerWidget, FileWidget
from dependencies.dependency import safe_unicode
from openerp.tools.translate import _

schema = (

     StringField('Name',
        required = 1,
        searchable = True,
        validators = ('uniquefieldvalidator',),
        widget = StringWidget(
            label=_("Name"),
        ),
    ),
    StringField('TaxNumber',
        widget = StringWidget(
            label=_("VAT number"),
        ),
    ),
    StringField('Phone',
        widget = StringWidget(
            label=_("Phone"),
        ),
    ),
    StringField('Fax',
        widget = StringWidget(
            label=_("Fax"),
        ),
    ),
    StringField('Email Address',
        schemata = 'Address',
        widget = StringWidget(
            label=_("Email Address"),
        ),
        validators = ('isEmail',)
    ),
          
    # # ~~~~~~~~~~ PhysicalAddress behavior in Odoo is as selection field ~~~~~~~~~~~
    fields.Many2one(comodel_name='olims.country',string='physical_country',default=lambda self: self.env['olims.country'].search([('name','=','United States')]).id),
    fields.Many2one(comodel_name='olims.state',string='physical_state', domain="[('Country', '=', physical_country)]"),
    fields.Many2one(comodel_name='olims.district',string='physical_district', domain="[('State', '=', physical_state)]"),
    fields.Char(string='physical_city'),
    fields.Char(string='physical_postalcode'),
    fields.Char(string='physical_address'),
    fields.Selection([('postal', 'Postal Address'),('billing','Billing Address')],string='physical_copy_from'),
                 
    # # ~~~~~~~~~~ PostalAddress behavior in Odoo is as selection field ~~~~~~~~~~~
    fields.Many2one(comodel_name='olims.country',string='postal_country',default=lambda self: self.env['olims.country'].search([('name','=','United States')]).id),
    fields.Many2one(comodel_name='olims.state',string='postal_state', domain="[('Country', '=', postal_country)]"),
    fields.Many2one(comodel_name='olims.district',string='postal_district', domain="[('State', '=', postal_state)]"),
    fields.Char(string='postal_city'),
    fields.Char(string='postal_postalcode'),
    fields.Char(string='postal_address'),
    fields.Selection([('physical', 'Physical Address'),('billing','Billing Address')],string='postal_copy_from'),
                
       # # ~~~~~~~~~~ BillingAddress behavior in Odoo is as selection field ~~~~~~~~~~~
    fields.Many2one(comodel_name='olims.country',string='billing_country',default=lambda self: self.env['olims.country'].search([('name','=','United States')]).id),
    fields.Many2one(comodel_name='olims.state',string='billing_state', domain="[('Country', '=', billing_country)]"),
    fields.Many2one(comodel_name='olims.district',string='billing_district', domain="[('State', '=', billing_state)]"),
    fields.Char(string='billing_city'),
    fields.Char(string='billing_postalcode'),
    fields.Char(string='billing_address'),
    fields.Selection([('physical','Physical Address'),('postal', 'Postal Address')],string='billing_copy_from'),
    StringField('AccountType',
        schemata = 'Bank details',
        widget = StringWidget(
            label=_("Account Type"),
        ),
    ),
    StringField('AccountName',
        schemata = 'Bank details',
        widget = StringWidget(
            label=_("Account Name"),
        ),
    ),
    StringField('AccountNumber',
        schemata = 'Bank details',
        widget = StringWidget(
            label=_("Account Number"),
        ),
    ),
    StringField('BankName',
        schemata = 'Bank details',
        widget = StringWidget(
            label=_("Bank name"),
        ),
    ),
    StringField('BankBranch',
        schemata = 'Bank details',
        widget = StringWidget(
            label=_("Bank branch"),
        ),
    ),

    StringField('LabURL',
        schemata = 'Address',
        #write_permission = ManageBika,
        widget = StringWidget(
            size = 60,
            label=_("Lab URL"),
            description=_("The Laboratory's web address"),
        ),
    ),
    IntegerField('Confidence',
        default=100,
        schemata = 'Accreditation',
        widget = IntegerWidget(
            label=_("Confidence Level %"),
            description=_("This value is reported at the bottom of all published results"),
        ),
    ),
    BooleanField('LaboratoryAccredited',
        default = False,
        schemata = 'Accreditation',
        #write_permission = ManageBika,
        widget = BooleanWidget(
            label=_("Laboratory Accredited"),
            description=_("Check this box if your laboratory is accredited"),
        ),
    ),
    StringField('AccreditationBody',
        schemata = 'Accreditation',
        #write_permission = ManageBika,
        widget = StringWidget(
            label=_("Accreditation Body Abbreviation"),
            description=_("E.g. SANAS, APLAC, etc."),
        ),
    ),
    StringField('AccreditationBodyURL',
        schemata = 'Accreditation',
        #write_permission = ManageBika,
        widget = StringWidget(
            label=_("Accreditation Body URL"),
            description=_("Web address for the accreditation body"),
        ),
    ),
    StringField('Accreditation',
        schemata = 'Accreditation',
        #write_permission = ManageBika,
        widget = StringWidget(
            label=_("Accreditation"),
            description=_("The accreditation standard that applies, e.g. ISO 17025"),
        ),
    ),
    StringField('AccreditationReference',
        schemata = 'Accreditation',
        #write_permission = ManageBika,
        widget = StringWidget(
            label=_("Accreditation Reference"),
            description=_("The reference code issued to the lab by the accreditation body"),
        ),
    ),
# ~~~~~~~ To be implemented ~~~~~~~
    
    FileField('AccreditationBodyLogo',
              help="Please upload the logo you are authorised to use on your "+
                "website and results reports by your accreditation body. "+
                "Maximum size is 175 x 175 pixels.",
        widget = FileWidget(
            label = _("Accreditation Logo"),
        ),
    ),
          
    
    fields.Text('AccreditationPageHeader', size=10, help="Enter the details of your lab`s service accreditations "+
                "here.  The following fields are available:  lab_is_accredited, "+
                "lab_name, lab_country, confidence, accreditation_body_name, "+
                "accreditation_standard, accreditation_reference<br/>"
    ),

)


class Laboratory(models.Model, BaseOLiMSModel):
    _name='olims.laboratory'
    _rec_name = 'Name'

    def getSchema(self):
        return self.schema

    def Title(self):
        title = self.getName() and self.getName() or _("Laboratory")
        return safe_unicode(title).encode('utf-8')

    @api.onchange('physical_copy_from')
    def _onchange_physical(self):
        # set auto-changing field
        if self.physical_copy_from:
            setattr(self, 'physical_country', getattr(self,self.physical_copy_from+'_country'))
            setattr(self, 'physical_state', getattr(self,self.physical_copy_from+'_state'))
            setattr(self, 'physical_district', getattr(self,self.physical_copy_from+'_district'))
            setattr(self, 'physical_city', getattr(self,self.physical_copy_from+'_city'))
            setattr(self, 'physical_postalcode', getattr(self,self.physical_copy_from+'_postalcode'))
            setattr(self, 'physical_address', getattr(self,self.physical_copy_from+'_address'))

    @api.onchange('postal_copy_from')
    def _onchange_postal(self):
        # set auto-changing field
        if self.postal_copy_from:
            setattr(self, 'postal_country', getattr(self,self.postal_copy_from+'_country'))
            setattr(self, 'postal_state', getattr(self,self.postal_copy_from+'_state'))
            setattr(self, 'postal_district', getattr(self,self.postal_copy_from+'_district'))
            setattr(self, 'postal_city', getattr(self,self.postal_copy_from+'_city'))
            setattr(self, 'postal_postalcode', getattr(self,self.postal_copy_from+'_postalcode'))
            setattr(self, 'postal_address', getattr(self,self.postal_copy_from+'_address'))

    @api.onchange('billing_copy_from')
    def _onchange_billing(self):
        # set auto-changing field
        if self.billing_copy_from:
            print "billing running"
            setattr(self, 'billing_country', getattr(self,self.billing_copy_from+'_country'))
            setattr(self, 'billing_state', getattr(self,self.billing_copy_from+'_state'))
            setattr(self, 'billing_district', getattr(self,self.billing_copy_from+'_district'))
            setattr(self, 'billing_city', getattr(self,self.billing_copy_from+'_city'))
            setattr(self, 'billing_postalcode', getattr(self,self.billing_copy_from+'_postalcode'))
            setattr(self, 'billing_address', getattr(self,self.billing_copy_from+'_address'))


Laboratory.initialze(schema)