# -*- coding: utf-8 -*-
from odoo import api, fields, models,_
import datetime
from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar
from io import BytesIO,StringIO
import xlwt
import io
from base64 import b64decode
import base64
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import serialize_exception,content_disposition
from odoo.exceptions import ValidationError

class Binary(http.Controller):
 @http.route('/opt/download', type='http', auth="public")
 @serialize_exception
 def download_document(self,model,field,id,filename=None, **kw):
    """ Download link for files stored as binary fields.
    :param str model: name of the model to fetch the binary from
    :param str field: binary field
    :param str id: id of the record from which to fetch the binary
    :param str filename: field holding the file's name, if any
    :returns: :class:`werkzeug.wrappers.Response`
    """
    cr, uid, context = request.cr, request.uid, request.context
    env = api.Environment(cr, 1, {})  
    out_brw=env['output'].browse(int(id))
    filecontent = base64.b64decode(out_brw.xls_output or '')
    if not filecontent:
        return request.not_found()
    else:
       if not filename:
           filename = '%s_%s' % (model.replace('.', '_'), id)
       return request.make_response(filecontent,
                      [('Content-Type', 'application/octet-stream'),
                       ('Content-Disposition', content_disposition(filename))])


class DailyCollectionMReport(models.TransientModel):

    _name = "daily.collection.report"
    _description = "Daily Collection Report"
    
    today_date=fields.Date('Date',default=fields.Date.context_today)
    
    def print_excel_report(self):
        cr= self.env.cr
        workbook = xlwt.Workbook()
        inv_ids=self.env['account.invoice'].search([('date_invoice','=',self.today_date)])
        style1 = xlwt.easyxf('pattern: pattern solid, fore_colour ice_blue;alignment: horiz centre;font: bold on; borders: left medium, top medium, bottom medium,right medium')
        style2 = xlwt.easyxf('pattern: pattern solid, fore_colour ivory;alignment: horiz centre;font: bold on; borders: left medium, top medium, bottom medium,right medium')
        style3 = xlwt.easyxf('alignment: horiz centre;font: bold on; borders: left medium, top medium, bottom medium,right medium')
        Header_Text ='Daily Collection Report'
        sheet = workbook.add_sheet('Daily Collection Report')
        sheet.write_merge(0, 0,0,9,'Collection' ,style1)
        sheet.write_merge(1,2, 0,0,'RM',style1)
        sheet.write_merge(1,2, 1,1,'OFFICE',style1)
        sheet.write_merge(1,1, 2,5,'TODAY(DATE)',style2)
        sheet.write(2,2,"<30",style2)
        sheet.write(2,3,"30-90",style2)
        sheet.write(2,4,">90",style2)
        sheet.write(2,5,"TOTAL",style2)
        sheet.write_merge(1,1, 6,9,'AS ON DATE BILLING',style1)
        sheet.write(2,6,"<30",style1)
        sheet.write(2,7,"30-90",style1)
        sheet.write(2,8,">90",style1)
        sheet.write(2,9,"TOTAL",style1)
        sheet.write(3,0,"",style3)
        sheet.write(3,1,"",style3)
        sheet.write(3,2,"",style2)
        sheet.write(3,3,"",style2)
        sheet.write(3,4,"",style2)
        sheet.write(3,5,"",style2)
        sheet.write(3,6,"",style3)
        sheet.write(3,7,"",style3)
        sheet.write(3,8,"",style3)
        sheet.write(3,9,"",style3)
        sheet.write(4,0,"",style3)
        sheet.write(4,1,"",style3)
        sheet.write(4,2,"",style2)
        sheet.write(4,3,"",style2)
        sheet.write(4,4,"",style2)
        sheet.write(4,5,"",style2)
        sheet.write(4,6,"",style3)
        sheet.write(4,7,"",style3)
        sheet.write(4,8,"",style3)
        sheet.write(4,9,"",style3)
        sheet.write(5,0,"TOTAL",style1)
        sheet.write(5,1,"",style1)
        sheet.write(5,2,"",style2)
        sheet.write(5,3,"",style2)
        sheet.write(5,4,"",style2)
        sheet.write(5,5,"",style2)
        sheet.write(5,6,"",style1)
        sheet.write(5,7,"",style1)
        sheet.write(5,8,"",style1)
        sheet.write(5,9,"",style1)
        row=3
#        for inv_id in inv_ids:
#            sheet.write(row,0,inv_id.client_service_manager_id.name)
#            sheet.write(row,1,inv_id.branch_id.name)
#            sheet.write(row,2,inv_id.amount_total)
#            row+=1
        stream =BytesIO()
        workbook.save(stream)
        cr.execute(""" DELETE FROM output""")
        attach_id = self.env['output'].create({'name':Header_Text+'.xls', 'xls_output': base64.b64encode(stream.getvalue())})
        return {
             'type' : 'ir.actions.act_url',
             'url': '/opt/download?model=output&field=xls_output&id=%s&filename=Daily Collection Report.xls'%(attach_id.id),
             'target': 'new',
            } 
