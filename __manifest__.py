# -*- coding: utf-8 -*-
{
    'name': "Mejoras a encuestas",
    'summary': "Extiende y modifica funcionalidades del módulo de encuestas en Odoo 18 Enterprise",
    'description': """
Este módulo permite modificar y extender las funcionalidades del módulo de encuestas (survey)
    """,
    'author': "Jesus Acosta",
    'website': "https://movilidad.odoo.com/",
    'category': 'Surveys',
    'version': '0.1',
    'depends': ['survey'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'security/ir_rules.xml',
        "report/survey_user_input_report_templates.xml",
        "report/survey_user_input_report_actions.xml",
        'views/survey_layout.xml',
        'views/survey_view.xml',
        'views/survey_user_input_view.xml',
        'wizard/survey_invite.xml',
    ],
}
