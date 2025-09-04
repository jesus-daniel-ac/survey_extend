# -*- coding: utf-8 -*-
from odoo import models, fields, api
import unicodedata


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"


    is_psychologist_survey = fields.Boolean(
        related="survey_id.is_psychologist_survey",
        store=True,
        readonly=True
    )

    # Candidato
    business_unit_id = fields.Many2one(
        "res.company", 
        string="Unidad de Negocio"
    )
    candidate_name = fields.Char(
        string="Nombre del evaluado"
    )
    candidate_age = fields.Integer(
        string="Edad"
    )

    # Psicólogo evaluador
    psychologist_user_id = fields.Many2one(
        "res.users",
        string="Psicólogo",
        help="Psicólogo asignado."
    )
    psychologist_license = fields.Char(
        string="Cédula"
    )
    psychologist_signature = fields.Binary(
        string="Firma"
    )

    # Puntajes
    points_assit = fields.Float(string="Assist", compute="_compute_section_points")
    points_ders = fields.Float(string="Ders", compute="_compute_section_points")
    points_plutchik = fields.Float(string="Plutchik", compute="_compute_section_points")

    # Resultados
    risk_substance_use = fields.Selection(
        [
            ("low", "Bajo"),
            ("medium", "Medio"),
            ("high", "Alto"),
        ],
        string="Riesgo consumo de sustancias"
    )
    emotional_stability_summary = fields.Text(
        string="Resumen de estabilidad emocional"
    )
    evaluation_final_result = fields.Selection(
        [
            ("apto", "Apto"),
            ("no_apto", "No apto"),
        ],
        string="Resultado final de la evaluación"
    )
    recommendations = fields.Text(
        string="Recomendaciones"
    )


    def _norm(self,text):
        """Normaliza: quita acentos, trim y pone en minúsculas."""
        if not text:
            return ''
        txt = unicodedata.normalize('NFKD', text)
        txt = ''.join(c for c in txt if unicodedata.category(c) != 'Mn')
        return txt.strip().lower()
  

    def _compute_section_points(self):
        for rec in self:
            tot_assist = tot_ders = tot_plutchik = 0.0
            for line in rec.user_input_line_ids:
                if line.skipped:
                    continue
                score = line.answer_score or 0.0

                # Título de la sección: usa la página si existe; si no, la página de la pregunta
                page = line.page_id or (line.question_id and line.question_id.page_id)
                title = getattr(page, 'title', '') or ''
                section = self._norm(title)  # case/acentos-insensitive
    

                if section in ('assist', 'assit'):
                    tot_assist += score
                elif section == 'ders':
                    tot_ders += score
                elif section == 'plutchik':
                    tot_plutchik += score

            rec.points_assit = tot_assist
            rec.points_ders = tot_ders
            rec.points_plutchik = tot_plutchik

    
    @api.model_create_multi
    def create(self, vals_list):
        ctx = self.env.context
        for vals in vals_list:
            # Solo setea si no viene explícito en vals
            if ctx.get('psychologist_user_id') and not vals.get('psychologist_user_id'):
                vals['psychologist_user_id'] = ctx['psychologist_user_id']
            if ctx.get('business_unit_id') and not vals.get('business_unit_id'):
                vals['business_unit_id'] = ctx['business_unit_id']
        return super().create(vals_list)


    def action_print_psychological_report(self):
        """Generate the psychological aptitude PDF report."""
        self.ensure_one()
        return self.env.ref("survey_extend.action_report_psychological_aptitude").report_action(self)
