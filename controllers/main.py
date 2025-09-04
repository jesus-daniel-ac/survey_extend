# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo.exceptions import UserError
from odoo.addons.survey.controllers.main import Survey as SurveyController

class SurveyLinkExt(SurveyController):

    @http.route('/survey/start/<int:psychologist_id>/<int:business_unit_id>/<string:survey_token>',
                type='http', auth='public', website=True)
    def survey_start_with_ctx(self, psychologist_id, business_unit_id, survey_token, answer_token=None, email=False, **post):
        """Arranque alterno con IDs embebidos en la ruta.
        Inyecta contexto y reutiliza el flujo estándar para crear/resolver la respuesta."""
        # Validaciones básicas
        User = request.env['res.users'].sudo().browse(psychologist_id)
        Company = request.env['res.company'].sudo().browse(business_unit_id)
        if not User or not User.exists() or not Company or not Company.exists():
            return request.redirect('/')

        # (Opcional) Garantiza que la company elegida está permitida al psicólogo
        if Company.id not in User.company_ids.ids:
            # 403 amigable
            return request.render("survey.survey_access_error", {'survey': request.env['survey.survey']})

        # 1) Reutiliza la resolución de acceso del core
        answer_from_cookie = False
        if not answer_token:
            answer_token = request.cookies.get('survey_%s' % survey_token)
            answer_from_cookie = bool(answer_token)

        access_data = self._get_access_data(survey_token, answer_token, ensure_token=False)
        if answer_from_cookie and access_data['validity_code'] in ('answer_wrong_user', 'token_wrong'):
            access_data = self._get_access_data(survey_token, None, ensure_token=False)

        if access_data['validity_code'] is not True:
            return self._redirect_with_error(access_data, access_data['validity_code'])

        survey_sudo, answer_sudo = access_data['survey_sudo'], access_data['answer_sudo']

        # 2) Si no hay respuesta, créala pasando contexto con los IDs
        if not answer_sudo:
            try:
                ctx = dict(request.env.context, psychologist_user_id=psychologist_id, business_unit_id=business_unit_id)
                # Muy importante: el contexto va en el env del survey para que llegue hasta user_input.create()
                answer_sudo = survey_sudo.with_context(ctx)._create_answer(user=request.env.user, email=email)
            except UserError:
                answer_sudo = False

        # 3) Igual que el core: si no se pudo crear, verifica acceso / muestra 403
        if not answer_sudo:
            try:
                survey_sudo.with_user(request.env.user).check_access('read')
            except Exception:
                return request.redirect("/")
            else:
                return request.render("survey.survey_403_page", {'survey': survey_sudo})

        # 4) Redirige al flujo normal de cumplimentación
        return request.redirect('/survey/%s/%s' % (survey_sudo.access_token, answer_sudo.access_token))
