import random
import re
from database import db
from models import User, Observable
from flask import Flask, request, abort
from flask_apscheduler import APScheduler
from jobs import Config
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, StickerSendMessage, ButtonsTemplate, \
    TemplateSendMessage, PostbackTemplateAction, URITemplateAction, PostbackEvent, ConfirmTemplate, FollowEvent, ImageCarouselTemplate, ImageCarouselColumn,ImageSendMessage
from soup import gossip, lol, beauty, draw_beauty
import threading


app = Flask(__name__)
app.config.from_pyfile('config.cfg')
db.init_app(app)
db.app = app

line_bot_api = LineBotApi(
    "ktZx2BhmTCfUsnUjNbgN9rD8Tfj9Q0+Gbg3cVbD4x2BhYNlQEZ5EEBu1wmmtzOhVKYx73k8INzAElVAdDJMyiM9FDaF6"
    "tghWuX1iBGTKH2numVXgFKEf68g69e31cPgz3GWsL773JCoItMRGJEbScgdB04t89/1O/w1cDnyilFU=")
handler = WebhookHandler('57b5c6c6c5556eb8d98e4836704c79a9')


@app.route('/')
def index():
    return "<p>Hello World</p>"


@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body:" + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'ok'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text == '訂閱':
        reply_text_message(event.reply_token, interval_news(event))
    elif event.message.text == 'Help':
        reply_menu_message(event)
    elif event.message.text == '退訂':
        desubscribe(event)
    elif re.match(r'^追蹤\s', event.message.text):
        reply_text_message(event.reply_token, subscribe(event))
    elif event.message.text == '嗨':
        reply_text_message(event.reply_token, '嗨~~~帥哥')
    elif event.message.text == '照片':
        threading.Thread(target=reply_image,name='photo_crawl',args=[event]).start()
    else:
        unsupported_message(event)


@handler.add(PostbackEvent)
def handle_postback(event):
    if event.postback.data == 'gossip':
        reply_text_message(event.reply_token, gossip())
    elif event.postback.data == 'lol':
        reply_text_message(event.reply_token, lol())
    elif event.postback.data == 'describe':
        user = db.session.query(User).filter(
            User.user == event.source.user_id).one()
        db.session.delete(user)
        db.session.commit()
        line_bot_api.reply_message(
            event.reply_token,
            StickerSendMessage(
                package_id='2',
                sticker_id='32'
            )
        )
    elif event.postback.data == 'not_describe':
        line_bot_api.reply_message(
            event.reply_token,
            StickerSendMessage(
                package_id='2',
                sticker_id='36'
            )
        )


@handler.add(FollowEvent)
def handle_FollowEvent(event):
    reply_text_message(
        event.reply_token,
        '我是Shotic,有任何的問題輸入"Help"我馬上來喔(hahaha)')


def interval_news(event):
    line_bot_api.push_message(
        event.source.user_id,
        StickerSendMessage(
            package_id='1',
            sticker_id='2'
        )
    )
    app.logger.info("User :" + event.source.user_id)
    if db.session.query(User).filter(User.user == event.source.user_id).all():
        return '已經訂閱囉'
    user = User(user=event.source.user_id)
    db.session.add(user)
    db.session.commit()
    return '開始訂閱'


def reply_text_message(reply_token, text):
    line_bot_api.reply_message(
        reply_token,
        TextSendMessage(text=text))


def reply_menu_message(event):
    template = ButtonsTemplate(
        text='想知道些什麼嗎',
        title='萬能的汪',
        thumbnail_image_url='https://cdn2.ettoday.net/images/2168/2168292.jpg',
        actions=[
            PostbackTemplateAction(label='看些有的沒的', data='gossip'),
            PostbackTemplateAction(label='爛遊戲近況', data='lol'),
            URITemplateAction(label='去蝦皮晃晃', uri='https://shopee.tw/')
        ]
    )
    message = TemplateSendMessage(
        alt_text='message',
        template=template
    )
    line_bot_api.reply_message(
        event.reply_token,
        message
    )


def reply_image(event):
    imgs = beauty()
    columns = []
    for img in imgs:
        columns.append(
            ImageCarouselColumn(
                img['img'],
                URITemplateAction(
                    label='learn more',
                    uri=img['target']
                )
            )
        )
    message=[
        TemplateSendMessage(
            alt_text='photolist',
            template=ImageCarouselTemplate(
                columns=columns
            )
        )
    ]
    bottle_message=[
        [
            StickerSendMessage(
                sticker_id=522,
                package_id=2
            ),
            TextSendMessage(
                text='快收好!!別說是我給的!!'
            )
        ],
        [
            StickerSendMessage(
                sticker_id=178,
                package_id=2
            ),
            TextSendMessage(
                text='不錯吧 嘿嘿'
            )
        ],
        [
            StickerSendMessage(
                sticker_id=156,
                package_id=2
            ),
            TextSendMessage(
                text='朋友就是要互相分享，不用謝了'
            )
        ],
    ]
    message.extend(random.choice(bottle_message))
    line_bot_api.reply_message(
        event.reply_token,
        messages=message
    )


def unsupported_message(event):
    try:
        line_bot_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(text="抱歉!!我不知道你在說甚麼"),
                StickerSendMessage(package_id=1, sticker_id=108)
            ]
        )
    except LineBotApiError:
        app.logger.info(
            "LineBotApiError:" +
            '無法辨識的reply_token' +
            event.reply_token)


def notice():
    img=draw_beauty()
    for row in db.session.query(User).all():
        user = row.user
        messages = [
            ImageSendMessage(img[0]['img'],img[0]['img']),
            StickerSendMessage(
                package_id=2,
                sticker_id=22
            )
        ]
        line_bot_api.push_message(
            user,
            messages=messages
        )


def check_noticed(user):
    if db.session.query(User).filter(User.user == user).all():
        return True
    else:
        return False


def subscribe(event):
    m = re.match(r'^追蹤\s(\w+)', event.message.text)
    if check_noticed(event.source.user_id):
        if m:
            user = db.session.query(User).filter(
                User.user == event.source.user_id).one()
            sub = Observable(name=m.group(1), user_id=user.user)
            app.logger.info("subscribe:" + user + " " + sub)
            db.session.add(sub)
            db.session.commit()
            line_bot_api.push_message(
                event.source.user_id,
                TextSendMessage(
                    text=m.group(1)
                )
            )
        return '成功追蹤'
    else:
        return '請先訂閱喔'


def desubscribe(event):
    if check_noticed(event.source.user_id):
        template = ConfirmTemplate(
            text='真的要退訂嗎',
            actions=[
                PostbackTemplateAction(label='退!!!', data='describe'),
                PostbackTemplateAction(label='算了', data='not_describe')
            ]
        )
        message = TemplateSendMessage(
            alt_text='退訂',
            template=template
        )
        line_bot_api.reply_message(event.reply_token, message)


if __name__ == "__main__":
    scheduler = APScheduler()
    app.config.from_object(Config)
    scheduler.init_app(app)
    scheduler.start()
    app.run(debug=True, use_reloader=False)
