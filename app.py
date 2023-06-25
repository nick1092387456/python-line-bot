# 運行以下程式需安裝模組: line-bot-sdk, flask, pyquery
# 安裝方式，輸入指令: pip install 模組名稱

# 引入os模組
import os

# 引入flask模組
from flask import Flask, request, abort
# 引入linebot相關模組
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)

# 如需增加其他處理器請參閱以下網址的 Message objects 章節
# https://github.com/line/line-bot-sdk-python
from linebot.models import (
    MessageEvent,
    TextMessage,
    StickerMessage,
    TextSendMessage,
    StickerSendMessage,
    LocationSendMessage,
    ImageSendMessage,
    TemplateSendMessage,
    ButtonsTemplate,
    PostbackAction,
    MessageAction,
    ImageMessage,
    URIAction,
    CarouselTemplate,
    CarouselColumn
)

# from modules.reply import faq, menu
# from modules.currency import get_exchange_table

# table = get_exchange_table()
# print(table)

# 定義應用程式是一個Flask類別產生的實例
app = Flask(__name__)

# 引入環境變數
from dotenv import load_dotenv
load_dotenv()

# LINE的Webhook為了辨識開發者身份所需的資料
# 相關訊息進入網址(https://developers.line.me/console/)
CHANNEL_ACCESS_TOKEN = os.getenv('CHANNEL_ACCESS_TOKEN')
CHANNEL_SECRET = os.getenv('CHANNEL_SECRET')

# ********* 以下為 X-LINE-SIGNATURE 驗證程序 *********
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)
@app.route("/", methods=['POST'])
def callback():
    # 當LINE發送訊息給機器人時，從header取得 X-Line-Signature
    # X-Line-Signature 用於驗證頻道是否合法
    signature = request.headers['X-Line-Signature']

    # 將取得到的body內容轉換為文字處理
    body = request.get_data(as_text=True)
    print("[BODY]")
    print(body)

    # 一但驗證合法後，將body內容傳至handler
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'
# ********* 以上為 X-LINE-SIGNATURE 驗證程序 *********


# 圖片訊息傳入時的處理器
from pyzbar.pyzbar import decode

from PIL import Image
@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    # 當有圖片訊息傳入時
    print('*'*30)
    print('[使用者傳入圖片訊息]')
    print(str(event))

    # 下載圖片
    message_content = line_bot_api.get_message_content(event.message.id)
    image_folder = 'image'
    if not os.path.exists(image_folder):
        os.makedirs(image_folder)
    image_path = os.path.join(image_folder, event.message.id + '.jpg')
    with open(image_path, 'wb') as file:
        for chunk in message_content.iter_content():
            file.write(chunk)
   
    # 解析圖片
    qr_data = decode(Image.open(image_path))        

     # 準備要回傳的訊息
    if qr_data:
        # 若成功解析到 QR 碼
        qr_content = qr_data[0].data.decode('utf-8')
        reply_message = TextSendMessage(text=qr_content)
    else:
        # 若未解析到 QR 碼
        reply_message = TextSendMessage(text='未能解析到 QR 碼')

    # 回傳訊息
    line_bot_api.reply_message(event.reply_token, reply_message)
    



if __name__ == "__main__":
    print('[伺服器開始運行]')
    # 取得遠端環境使用的連接端口，若是在本機端測試則預設開啟於port=5500
    port = int(os.environ.get('PORT', 5500))
    # 使app開始在此連接端口上運行
    print(f'[Flask運行於連接端口:{port}]')
    # 本機測試使用127.0.0.1, debug=True
    
    # Heroku部署使用
    if 'DYNO' in os.environ:
        # Heroku部署使用 0.0.0.0
        host = '0.0.0.0'
    else:
        # 本機測試使用
        host = '127.0.0.1'

    app.run(host=host, port=port, debug=True)
