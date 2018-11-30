
import json
import logging
import constants

import telepot
from django.template.loader import render_to_string
from django.http import HttpResponseForbidden, HttpResponseBadRequest, JsonResponse
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings

from .utils import parse_rss


TelegramBot = telepot.Bot(constants.token)


logger = logging.getLogger('telegram.bot')


def _display_help():
    return render_to_string('help.md')


def _display_feed():
    return render_to_string('feed.md', {'items': parse_rss()})


class CommandReceiveView(View):
    def post(self, request, bot_token):
        if bot_token != constants.token:
            return HttpResponseForbidden('Invalid token')

        commands = {
            '/start': _display_help,
            'help': _display_help,
            'feed': _display_feed,
        }

        raw = request.body.decode('utf-8')
        logger.info(raw)

        try:
            payload = json.loads(raw)
        except ValueError:
            return HttpResponseBadRequest('Invalid request')
        else:
            chat_id = payload['message']['chat']['id']
            cmd = payload['message'].get('text')  # command

            func = commands.get(cmd.split()[0].lower())
            if func:
                TelegramBot.sendMessage(chat_id, func(), parse_mode='Markdown')
            else:
                TelegramBot.sendMessage(chat_id, 'I do not understand you')

        return JsonResponse({}, status=200)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CommandReceiveView, self).dispatch(request, *args, **kwargs)