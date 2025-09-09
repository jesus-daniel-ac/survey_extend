# -*- coding: utf-8 -*-
from odoo import models, fields, api
import werkzeug


class SurveySurvey(models.Model):
    _inherit = 'survey.survey'

    color = fields.Integer(
        string="Color",
        help="Index of the color (used with Odoo's predefined color list)."
    )
    hide_answers = fields.Boolean(
        string="No mostrar respuestas",
        help="Si está activado, las respuestas no se mostrarán al finalizar la encuesta."
    )
    hide_percentage = fields.Boolean(
        string='No mostrar porcentaje',
        help='Activa esta opción para ocultar el porcentaje de respuestas al finalizar la encuesta.'
    )
    hide_result_block = fields.Boolean(
        string="Ocultar bloque de resultados",
        help="Si está activado, se ocultará el bloque de felicitación/aprobación, certificado y botones."
    )
    is_psychologist_survey = fields.Boolean(
        string='Encuesta de psicólogo',
        help='Activa esta opción si la encuesta será realizada por un psicólogo.'
    )
    psychologist_ids = fields.Many2many(
        'res.users',
        'survey_psychologist_rel',  # nombre de la tabla rel
        'survey_id',
        'user_id',
        string="Psicólogos asignados",
        help="Usuarios psicólogos que tienen permiso de ver esta encuesta",
    )


    def _create_answer(self, **values):
        if self.is_psychologist_survey and self.env.context.get("psychologist_user_id"):
            values["psychologist_user_id"] = self.env.context["psychologist_user_id"]
        return super()._create_answer(**values)


    def action_survey_user_input_completed(self):
        self.ensure_one()
        if self.is_psychologist_survey:
            action = self.env["ir.actions.act_window"]._for_xml_id(
                "survey_extend.action_survey_user_input_psychologist"
            )
        else:
            action = self.env["ir.actions.act_window"]._for_xml_id(
                "survey.action_survey_user_input"
            )

        ctx = dict(self.env.context)
        ctx.update({
            "search_default_survey_id": self.id,
            "search_default_completed": 1,
        })
        action["context"] = ctx
        return action



class SurveyInvite(models.TransientModel):
    _inherit = "survey.invite"

    @api.depends("survey_id.access_token", "psychologist_user_id")
    def _compute_survey_start_url(self):
        for invite in self:
            if not invite.survey_id:
                invite.survey_start_url = False
                continue
            if invite.survey_id.is_psychologist_survey and not invite.psychologist_user_id:
                # Si es encuesta de psicologo y no se ha elegido no hay link
                invite.survey_start_url = False
            else:
                # Genera la URL normal
                invite.survey_start_url = werkzeug.urls.url_join(
                    invite.survey_id.get_base_url(),
                    invite.survey_id.get_start_url()
                )
