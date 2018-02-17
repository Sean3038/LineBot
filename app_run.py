import random
import re
from database import db
from models import User, DrawService, Film
from flask import Flask, request, abort
from flask_apscheduler import APScheduler
from flask_sslify import SSLify
from jobs import Config
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, StickerSendMessage, ButtonsTemplate,
    TemplateSendMessage, PostbackTemplateAction, URITemplateAction, PostbackEvent,
    ConfirmTemplate, FollowEvent, ImageCarouselTemplate, ImageCarouselColumn,ImageSendMessage,
    CarouselTemplate,CarouselColumn
)
from safefix import SaferProxyFix
from soup import gossip, lol, beauty, draw_beauty, search_video, search_video_detail, test_connect
import pytz
import threading


app = Flask(__name__)
tz=pytz.timezone('Asia/Taipei')
sslify = SSLify(app)
app.config.from_pyfile('config.cfg')
app.wsgi_app=SaferProxyFix(app.wsgi_app)
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
    check_uid(event.source.user_id)
    if event.message.text == '訂閱':
        reply_text_message(event.reply_token, subscribe_DService(event))
    elif event.message.text == 'Help':
        reply_menu_message(event)
    elif event.message.text == '退訂':
        unsubscribe(event)
    elif re.match(r'^搜尋', event.message.text):
        reply_text_message(event.reply_token, '我找找看喔，等我~~~')
        threading.Thread(target=search,name='search',args=[event]).start()
    elif event.message.text == '追蹤清單':
        reply_text_message(event.reply_token, get_chase_list(event.source.user_id))
    elif re.match(r'^取消',event.message.text):
        m=re.match(r'^取消(\d+)',event.message.text)
        if m:
            reply_text_message(event.reply_token,chase_cancel_film(event.source.user_id,m.group(1)))
        else:
            reply_text_message(event.reply_token,'請輸入"取消"+"影集id"~~')
    elif event.message.text == '嗨':
        reply_text_message(event.reply_token, '嗨~~')
    elif event.message.text == '照片':
        reply_text_message(event.reply_token, '等我一下喔，讓我找找')
        threading.Thread(target=draw_image,name='photo_crawl',args=[event]).start()
    elif event.message.text == '測試':
        reply_text_message(event.reply_token,test_connect())
    else:
        unsupported_message(event)


@handler.add(PostbackEvent)
def handle_postback(event):
    if event.postback.data == 'gossip':
        reply_text_message(event.reply_token, gossip())
    elif event.postback.data == 'lol':
        reply_text_message(event.reply_token, lol())
    elif re.match(r'unsubscribe',event.postback.data):
        if not check_contract_ds(event.source.user_id):
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    '您尚未訂閱'
                )
            )
            return
        if re.search(r'yes',event.postback.data):
            contract = db.session.query(DrawService).filter(
                DrawService.uid == event.source.user_id).one()
            contract.flag = False
            db.session.commit()
            line_bot_api.reply_message(
                event.reply_token,
                StickerSendMessage(
                    package_id='2',
                    sticker_id='32'
                )
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                StickerSendMessage(
                    package_id='2',
                    sticker_id='36'
                )
            )
    elif re.match(r'search',event.postback.data):
        m=re.match(r'search&(\S+)',event.postback.data)
        if m:
            reply_text_message(event.reply_token,chase_film(event.source.user_id,m.group(1)))


@handler.add(FollowEvent)
def handle_FollowEvent(event):
    line_bot_api.push_message(
        event.reply_token,
        [
            StickerSendMessage(
                package_id='1',
                sticker_id='2'
            ),
            TextSendMessage(
                text='我是Shotic,有任何的問題輸入"Help"我馬上來喔(hahaha),另外可以輸入"訂閱"早上會有驚喜喔!!,偷偷跟你說我有很多"照片"喔嘿嘿'
            )
        ]
    )


def subscribe_DService(event):
    check_contract(event.source.user_id)
    line_bot_api.push_message(
        event.source.user_id,
        StickerSendMessage(
            package_id='1',
            sticker_id='2'
        )
    )
    if check_contract_ds(event.source.user_id):
        return '已經訂閱囉'
    else:
        contract=db.session.query(DrawService).filter(DrawService.uid == event.source.user_id).first()
        contract.flag=True
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


def draw_image(event):
    check_contract(event.source.user_id)
    cal_d_count(event.source.user_id)
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
    line_bot_api.push_message(
        event.source.user_id,
        messages=message
    )


def cal_d_count(user):
    contract=db.session.query(DrawService).filter(DrawService.uid == user).first()
    if contract:
        contract.count=contract.count+1
        db.session.commit()


def search(event):
    m=re.match(r'^搜尋(\S+)',event.message.text)
    if m:
        ary=search_video(m.group(1))
        if len(ary) > 0:
            columns=[]
            for i in ary:
                actions=[
                    PostbackTemplateAction('開始追!!!','search&'+i['url']),
                    URITemplateAction('讓我看看',i['url'])
                ]
                columns.append(CarouselColumn(text=i['name'],thumbnail_image_url=i['img'],actions=actions))
            message=TemplateSendMessage(
                    alt_text='playlist',
                    template=CarouselTemplate(
                        columns=columns
                    )
                )
            line_bot_api.push_message(
                event.source.user_id,
                messages=message,
                timeout=50
            )
        else:
            line_bot_api.push_message(
                event.source.user_id,
                messages=TextSendMessage(
                    text='抱歉找不到你說的影片'
                )
            )
    else:
        line_bot_api.push_message(
            event.source.user_id,
            messages=TextSendMessage(
                text='請輸入影集名稱'
            )
        )


def chase_film(user,url):
    film=check_film(url)
    u=query_user(user)
    if u in film.users.all():
        return '之前就在追了'
    else:
        u.films.append(film)
        db.session.commit()
        return '是的!!!馬上追!!!'


def chase_cancel_film(user,fid):
    film=db.session.query(Film).join(User.films).filter(User.uid == user , Film.id == fid).first()
    if film:
        q_user=db.session.query(User).filter(User.uid == user).first()
        q_user.films.remove(film)
        db.session.commit()
        return '成功取消追蹤'
    else:
        return '並未找到所輸入的id，請確認"追蹤清單"'


def check_film(url):
    film=db.session.query(Film).filter(Film.url == url).first()
    if not film:
        info=search_video_detail(url)
        n_film=Film(film=info['film'],episode=info['episode'],update_time=info['update_time'],url=info['url'])
        db.session.add(n_film)
        db.session.commit()
        return n_film
    return film


def get_chase_list(user):
    u=db.session.query(User).filter(User.uid == user).first()
    l=[]
    for film in u.films:
        l.append("\n"+str(film.id)+"|"+film.film+" "+film.episode)
    if len(l) > 0:
        s=""
        return 'id|名稱'+s.join(l)
    else:
        return '您目前沒有追蹤任何影集'


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

"""The job will execute at 7:00AM """
def d_service():
    img=draw_beauty()
    for row in db.session.query(DrawService).all():
        if row.flag:
            user = row.uid
            messages = [
                ImageSendMessage(img[0]['img'],img[0]['img']),
                StickerSendMessage(
                    package_id=2,
                    sticker_id=22
                ),
                TextSendMessage(
                    text="早安您好XDD"
                )
            ]
            line_bot_api.push_message(
                user,
                messages=messages
            )


def chase_job():
    films=db.session.query(Film).all()
    for film in films:
        if len(film.users.all()) == 0:
            print('刪除'+film.film)
            db.session.delete(film)
            db.session.commit()
        else:
            detail=search_video_detail(film.url)
            if detail['update_time'] > film.update_time:
                print(film.film+' 更新了')
                film.film=detail['film']
                film.episode=detail['episode']
                film.update_time=detail['update_time']
                db.session.commit()
                for user in film.users:
                    film_update_notify(user.uid,detail)
            else:
                print(film.film+' 尚未更新')


def film_update_notify(user,film):
    message=TextSendMessage(
        text=film['film']+" 已經更新到 "+film['episode'] +"\n快去看看吧"
    )
    line_bot_api.push_message(user,TextSendMessage(message))


"""Make sure that user contract was created"""
def check_contract(user):
    result=db.session.query(DrawService).filter(DrawService.uid == user).first()
    if not result:
        user=db.session.query(User).filter(User.uid == user).first()
        user.d_service = DrawService()
        db.session.add(user)
        db.session.commit()


"""This method use in recording user id and checking the record existed"""
def check_uid(user):
    result=db.session.query(User).filter(User.uid == user).first()
    if not result:
        n_user=User(uid=user)
        db.session.add(n_user)
        db.session.commit()


"""check user contract whether the service activated or not, return Boolean"""
def check_contract_ds(user):
    result = db.session.query(DrawService).filter(DrawService.uid == user).first()
    return result.flag


"""get user object from database"""
def query_user(user):
    return db.session.query(User).filter(User.uid == user).first()


"""This method will return a template message to confirm unsubscribe"""
def unsubscribe(event):
    if check_contract_ds(event.source.user_id):
        template = ConfirmTemplate(
            text='真的要退訂嗎',
            actions=[
                PostbackTemplateAction(label='退!!!', data='unsubscribe&yes'),
                PostbackTemplateAction(label='算了', data='unsubscribe&no')
            ]
        )
        message = TemplateSendMessage(
            alt_text='退訂',
            template=template
        )
        line_bot_api.reply_message(event.reply_token, message)
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage('您尚未訂閱'))


if __name__ == "__main__":
    scheduler = APScheduler(timezone=tz)
    app.config.from_object(Config)
    scheduler.init_app(app)
    scheduler.start()
    app.run(debug=True, use_reloader=False)
