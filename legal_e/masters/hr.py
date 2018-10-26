# -*- coding: utf-8 -*-
from odoo import fields, models, api

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    @api.onchange('user_id')
    def onchange_user(self):
        work_email, address_home_id = False, False
        if self.user_id:
            user_obj = self.env['res.users'].browse(self.user_id.id)
            address_home_id = (user_obj.partner_id and user_obj.partner_id.id or False)
        return {'value': {'work_email' : work_email,'address_home_id':address_home_id}}

    @api.onchange('name')
    def onchange_name(self):
        if not self.name:
            return {'value': {'city_code': False}}
        val = {
            'city_code': (self.name and len(self.name)>=3 and self.name[:3].upper() or False)
        }
        return {'value': val}

    tds= fields.Float('TDS Amount')
    pan_id=fields.Char('PAN No', size=10)
    code=fields.Char('Code', size=10)
    date_of_join=fields.Date('Date of Joining')
    street=fields.Char(realted='address_home_id.street',size=128, string='Street')
    street2=fields.Char(realted='address_home_id.street2',size=128, string='Street2')
    city=fields.Char(realted='address_home_id.city',size=128, string='City')
    state_id=fields.Many2one('res.country.state',related='address_home_id.state_id',string='State')
    zip=fields.Char(related='address_home_id.zip',size=24, string='Pin')
    country_id=fields.Many2one('res.country',related='address_home_id.country_id',string='Country')
    ho_branch_id=fields.Many2one('ho.branch','HO Branch', required=True)
    work_street=fields.Char('Street', size=128)
    work_street2=fields.Char('Street2', size=128)
    work_city=fields.Char('City', size=128)
    work_city=fields.Char('City', size=128)
    work_zip=fields.Char('Pin', size=24)
    work_district_id=fields.Many2one('district.district', 'District')
    work_state_id=fields.Many2one('res.country.state', 'State')
    work_country_id=fields.Many2one('res.country', 'Country')
    office_id= fields.Many2one('hr.office', 'Office')
    #department_id= fields.Many2one('hr.department', 'Department(Subdivision)')
    department_type= fields.Selection([('legal', 'Legal'),('non_legal', 'Non Legal')],'Department Type')
    client_service_admin= fields.Boolean('Client Service Admin')
    job_id= fields.Many2one('hr.job', 'Designation')
    parent_id= fields.Many2one('hr.employee', 'Reporting Head')

    
    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Code must be unique!'),
    ]

    @api.onchange('district_id')
    def onchange_district(self):
        if self.district_id:
            state_id = self.env['district.district'].browse(self.district_id).state_id.id
            country_id = self.env['res.country.state'].browse(self.state_id.id).country_id.id
            return {'value':{'work_country_id':country_id,'work_state_id':state_id}}
        return {}

    @api.onchange('state_id')
    def onchange_state(self):
        if self.state_id:
            country_id = self.env['res.country.state'].browse(self.state_id.id).country_id.id
            return {'value':{'work_country_id':country_id}}
        return {}        

    @api.model
    def create(self,vals):
        if self._context is None:
            context = {}
        if ('address_home_id' in vals) and vals['address_home_id']:
            self.env['res.partner'].browse(vals['address_home_id']).write({'street':vals.get('street',False), 'street2':vals.get('street2',False), 'city':vals.get('city',False), 'state_id':vals.get('state_id',False), 'zip':vals.get('zip',False), 'country_id':vals.get('country_id',False)})
            # self.env['res.partner'].write([vals['address_home_id']], {'street':vals.get('street',False), 'street2':vals.get('street2',False), 'city':vals.get('city',False), 'state_id':vals.get('state_id',False), 'zip':vals.get('zip',False), 'country_id':vals.get('country_id',False)})
        vals['code'] = self.env['ir.sequence'].get('hr.employee')
        retvals = super(HrEmployee, self).create(vals)
        return retvals
        
#     
#     def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
#         if not args:
#             args = []
#         if context is None:
#             context = {}
#         ids = []
#         employee_ids = []
#         if name:
#             if context.get('dept_employes', False):
#                 dept_obj = self.pool.get('hr.department').browse(cr, user, context['dept_employes'], context=context)
#                 employee_ids = [dept.id for dept in dept_obj.employee_ids]
#                 args += [('id', 'in', employee_ids)]
#                 
#                 ids = self.search(cr, user, [('name',operator,name)] + args, limit=limit, context=context)
#             else:
#                 ids = self.search(cr, user, [('name',operator,name)] + args, limit=limit, context=context)
#         if not ids:
#             if employee_ids:
#                 ids = employee_ids
#             else:
#                 ids = self.search(cr, user, [('name',operator,name)] + args, limit=limit, context=context)
#         return self.name_get(cr, user, ids, context)
#     
#     def search(self, cr, uid, args, offset=0, limit=None, order=None,
#             context=None, count=False):
#         if context is None:
#             context = {}
#         if context.get('dept_employes', False):
#             dept_obj = self.pool.get('hr.department').browse(cr, uid, context['dept_employes'], context=context)
#             return [dept.id for dept in dept_obj.employee_ids]
#                 
#         return super(hr_employee, self).search(cr, uid, args, offset, limit,
#                 order, context=context, count=count)

    @api.model
    def name_search(self, name, args=None, operator='ilike',limit=100):
        if not args:
            args = []
        if self._context is None:
            context = {}
        if self._context.get('dept_manager', False):
            dept_obj = self.env['hr.department'].browse(self._context['dept_manager'])
            employee_ids = [dept_obj.manager_id.id]
            args += [('id', 'in', employee_ids)]
            
        if self._context.get('dept_employes', False):
            dept_obj = self.env['hr.department'].browse(self._context['dept_employes'])
            employee_ids = [emp.id for emp in dept_obj.employee_ids]
            args += [('id', 'in', employee_ids)]
        
        return super(HrEmployee, self).name_search(name, args, operator=operator, limit=limit)
    
HrEmployee()


class HrOffice(models.Model):
    _description="HR Office"
    _name = 'hr.office'

    name= fields.Char('Name', size=64, required=True)
    state_id=fields.Many2one('res.country.state','State', required=True)
    parent_office=fields.Many2one('hr.office','Parent Office')

    
HrOffice()


class HrDepartment(models.Model):
    _inherit = "hr.department"

    office_id=fields.Many2one('ho.branch','Office')
    litigation=fields.Boolean('Litigation')
    non_litigation=fields.Boolean('Non Litigation')
    function_head= fields.Many2one('hr.employee','Function Head')
    reporting_head= fields.Many2one('hr.employee','Reporting Head')
    #legal= fields.Boolean('Legal'),
    #non_legal=fields.Boolean('Non Legal'),
    type=fields.Selection([('legal', 'Legal'),('non_legal', 'Non Legal')],'Type')
    # Add Type of work in hr department // Sanal Davis // 5-6-15
    work_type=fields.Selection([
        ('civillitigation', 'Civil Litigation'),
        ('criminallitigation', 'Criminal Litigation'),
        ('non_litigation', 'Non Litigation'),
        ('arbitration', 'Arbitration'),
        ('execution', 'Execution'),
        ('mediation', 'Mediation')
    ], 'Type of Work', track_visibility='onchange')
    employee_ids=fields.Many2many('hr.employee', 'employee_department_rel', 'emp_id', 'dept_id', 'Employees')
    child_id=fields.One2many('hr.department', 'parent_id', string='Child Departments')
    exclude_dashboard=fields.Boolean('Exclude From Dashboard')
    cost_id=fields.Many2one('legal.cost.center', 'Cost Center')

    
    
#     def get_parent_records(self, cr, uid, ids, grp_id, context=None):
#         res = []     
#         grp_obj = self.pool.get('res.groups')
#         grp = grp_obj.browse(cr, uid, grp_id)
#         if grp.implied_ids:
#             for parent_grp in grp.implied_ids:
#                 res.append(parent_grp.id)            
#                 if parent_grp.implied_ids:
#                     parent_ids = self.get_parent_records(cr, uid, ids, parent_grp.id)
#                     for parent_id in parent_ids:
#                         res.append(parent_id)
#         return res
    @api.multi
    def get_parent_records(self, dep_obj, res):
        if not res:
            res = [] 
        if dep_obj.parent_id:
                res.append(dep_obj.parent_id.id)            
                if dep_obj.parent_id.parent_id:
                    res.append(dep_obj.parent_id.parent_id.id)
                    self.get_parent_records(dep_obj.parent_id.parent_id, res)
        return res

    @api.multi
    def name_get(self):
        if self._context is None:
            context = {}
        if not self.ids:
            return []
        reads = self.read(['name','parent_id'])
        res = []
        for record in reads:
            name = record['name']
#             if record['parent_id']:
#                 name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res
        
HrDepartment()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: