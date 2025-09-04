from odoo import api, fields, models
import werkzeug

class SurveyInvite(models.TransientModel):
    _inherit = "survey.invite"

    psychologist_user_id = fields.Many2one(
        "res.users",
        string="Psicólogo",
        help="Psicólogo asignado a esta encuesta.",
        default=lambda self: self.env.user, 
    )
    
    company_id = fields.Many2one(
        "res.company",
        string="Unidad de Negocio",
        domain="[('id', 'in', allowed_company_ids)]"
    )

    allowed_company_ids = fields.Many2many(
        "res.company",
        compute="_compute_allowed_company_ids",
        string="Compañías Permitidas"
    )

    @api.depends("psychologist_user_id")
    def _compute_allowed_company_ids(self):
        for record in self:
            if record.psychologist_user_id:
                # Odoo ya trae campo company_ids en res.users (multi-compañía)
                record.allowed_company_ids = record.psychologist_user_id.company_ids
            else:
                record.allowed_company_ids = False

    @api.onchange('psychologist_user_id', 'company_id', 'survey_id')
    def _onchange_psychologist_user_id(self):
        for w in self:
            # limpiar siempre
            w.survey_start_url = False

            if (
                w.survey_id
                and getattr(w.survey_id, 'is_psychologist_survey', False)
                and w.psychologist_user_id
                and w.company_id
            ):
                base = w.survey_id.get_base_url()
                path = f"/survey/start/{w.psychologist_user_id.id}/{w.company_id.id}/{w.survey_id.access_token}"
                w.survey_start_url = werkzeug.urls.url_join(base, path.lstrip('/'))
