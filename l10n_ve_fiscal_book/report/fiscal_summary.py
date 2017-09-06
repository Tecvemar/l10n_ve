# -*- encoding: utf-8 -*-
##############################################################################
#    Company: Tecvemar, c.a.
#    Author: Juan V. Márquez L.
#    Creation Date:
#    Version: 0.0.0.0
#
#    Description: Report parser for: fiscal_summary
#
#
##############################################################################
#~ import time
#~ import pooler
from report import report_sxw
#~ from tools.translate import _


class parser_fiscal_summary(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        context = context or {}
        super(parser_fiscal_summary, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            })
        self.context = context

report_sxw.report_sxw('report.fiscal.summary.report',
                      'fiscal.summary',
                      'addons/l10n_ve_fiscal_book/report/fiscal_summary.rml',
                      parser=parser_fiscal_summary,
                      header=False
                      )
