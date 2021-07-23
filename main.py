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
            resp = { 'text': '{} 당첨!'.format(random.choice(self.members)) }
            self.members = []
            self.state = 'IDLE'
            return resp
        return self.coffee_card(update=True)

    def coffee_card(self, update=False):
        buttons = [
            { 'textButton': { 'text': '참가', 'onClick': { 'action': { 'actionMethodName': 'join' } } } },
            { 'textButton': { 'text': '참가취소', 'onClick': { 'action': { 'actionMethodName': 'cancel' } } } }
        ]
        if self.members:
            buttons.append({ 'textButton': { 'text': '시작!', 'onClick': { 'action': { 'actionMethodName': 'start' } } } })
        return {
            'actionResponse': { 'type': 'UPDATE_MESSAGE' if update else 'NEW_MESSAGE' },
            'cards': [{
                'header': { 'title': '커피내기' },
                'sections': [{
                    'widgets': [
                    {
                        'textParagraph': { 'text': '{}'.format(' '.join(self.members)) }
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
