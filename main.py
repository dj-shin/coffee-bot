from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build

from flask import Flask, request, json
import random


app = Flask(__name__)


class ChatEvent:
    def __init__(self, event):
        _type = event.get('type')
        if _type == 'ADDED_TO_SPACE':
            pass
        elif _type == 'REMOVED_FROM_SPACE':
            pass
        elif _type == 'MESSAGE':
            pass


class CoffeeBot:
    def __init__(self):
        self.state = 'IDLE'
        self.members = []
        keyfile_name = 'hh-chatbot-1627002332577-c286cd8c2af4.json'
        scopes = 'https://www.googleapis.com/auth/chat.bot'
        credentials = ServiceAccountCredentials.from_json_keyfile_name(keyfile_name, scopes)
        self.chat = build('chat', 'v1', http=credentials.authorize(Http()))

    def handle_added_to_space(self, event):
        return { 'text': '안녕하세요! 커피봇입니다' }

    def handle_message(self, event):
        if event.get('message', {}).get('text') == '@Coffee':
            if self.state == 'IDLE':
                self.state = 'PREPARE_MEMBERS'
                self.members = []
                return self.coffee_card()
            else:
                return { 'text': '이미 참여가 진행 중입니다! 로그를 확인하세요' }

    def handle_card_clicked(self, event):
        if event.get('action', {}).get('actionMethodName') == 'join':
            name = event.get('user', {}).get('displayName')[1:]
            if name and name not in self.members:
                self.members.append(name)
        elif event.get('action', {}).get('actionMethodName') == 'cancel':
            name = event.get('user', {}).get('displayName')[1:]

            if name and name in self.members:
                self.members.remove(name)
        elif event.get('action', {}).get('actionMethodName') == 'start':
            # Run game
            space = event['space']['name']
            resp = { 'text': '{} 당첨!'.format(random.choice(self.members)) }
            self.chat.spaces().messages().create(parent=space, body=resp).execute()
            message = self.coffee_card(update=True, done=True)
            self.members = []
            self.state = 'IDLE'
            return message
        return self.coffee_card(update=True)

    def coffee_card(self, update=False, done=False):
        buttons = [
            { 'textButton': { 'text': '참가', 'onClick': { 'action': { 'actionMethodName': 'join' } } } },
            { 'textButton': { 'text': '참가취소', 'onClick': { 'action': { 'actionMethodName': 'cancel' } } } }
        ]
        if len(self.members) > 0:
            buttons.append({ 'textButton': { 'text': '시작!', 'onClick': { 'action': { 'actionMethodName': 'start' } } } })
        if done:
            buttons = []
        return {
            'actionResponse': { 'type': 'UPDATE_MESSAGE' if update else 'NEW_MESSAGE' },
            'cards': [{
                'header': { 'title': '커피내기' },
                'sections': [{
                    'widgets': [
                    {
                        'textParagraph': { 'text': '{}명: {}'.format(len(self.members), ' '.join(self.members)) }
                    }, {
                        'buttons': buttons
                    }]
                }]
            }]
        }


bot = CoffeeBot()


@app.route('/', methods=['POST'])
def on_event():
    event = request.get_json()
    t = event['eventTime']
    sender = event.get('user', {}).get('displayName')
    action = event['type']
    detail = event.get('action')
    print('{}\t{} | {} | {}'.format(t, sender, action, detail))
    resp = None
    if event['type'] == 'ADDED_TO_SPACE':
        resp = bot.handle_added_to_space(event);
    elif event['type'] == 'MESSAGE':
        resp = bot.handle_message(event);
    elif event['type'] == 'CARD_CLICKED':
        resp = bot.handle_card_clicked(event);

    if not resp:
        return '', 204
    return json.jsonify(resp)


if __name__ == '__main__':
    app.run(port=23589, debug=True)
