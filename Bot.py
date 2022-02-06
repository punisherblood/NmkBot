from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from apscheduler.schedulers.blocking import BlockingScheduler
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import vk_api
import datetime
import requests


vk_session = vk_api.VkApi(token = '3bc699d3cda7db8d3529e6426703c9a1d914fe1812d2fc5d41f61f5b87703a7db9c697694e2edd53f749a')
longpoll = VkBotLongPoll(vk_session,209960585)
url  = 'http://www.nmt.edu.ru/html/cg.htm'
maindict = {}
scheduler = BlockingScheduler()

def src(url):
    ua = UserAgent()
    s = requests.Session()
    response = s.get( url = url, headers = {'user-agent': f'{ua.random}'})
    response.encoding = response.apparent_encoding
    src = BeautifulSoup(response.text, 'lxml')
    return src

def get_href(src):
    for cell in src.find_all("tr"):
        try:
            d ={"http" : "http://www.nmt.edu.ru/html/"+cell.find("a",class_='z0').get("href")}
            maindict[cell.find("a",class_="z0").text] = d
        except Exception:
            pass

def get_lesson(group,src):
    group_dict = {}

    for cell in src.find("table",class_='inf').find_all('tr')[3:]:
        try:
            data = cell.find('td',class_='hd',rowspan = '8').text[:5]
            group_lession_dict = {}
            number = 1

        except Exception:
            pass
        try:
# 2 подгруппы
            if cell.find('td', class_="ur").get('colspan') == '1':
                lesson = []
                for K in cell.find_all('td')[1:]:
                    try:
                        lesson.append(K.find('a', class_='z1').text + '  |  ' + K.find('a', class_='z2').text) #+ '  |   '+ K.find('a', class_='z3').text
                    except Exception:
                        lesson.append('Нет пары')
                group_lession_dict[str(number)+' Пара'] = '1ПГ: ' + lesson[-2]+' 2ПГ: ' + lesson[-1] + ' \n'
# 1 подгруппа
            else:
                lesson = cell.find('a', class_='z1').text + '  |  ' +  cell.find('a', class_='z2').text #+ '  |   '+ item.find('a', class_='z3').text
                group_lession_dict[str(number)+' Пара'] = lesson + '\n'
        except Exception:
            lesson = 'Нет пары'
            group_lession_dict[str(number)+' Пара'] = lesson + '\n'
        number += 1
        if number == 8:
            group_dict.update({data:group_lession_dict})
    maindict[group].update({"Раписание":group_dict})

def parser():
    get_href(src('http://www.nmt.edu.ru/html/cg.htm'))
    for group in maindict:
        print(group)
        get_lesson(group,src(maindict.get(group).get("http")))
    return maindict

def sender(id,text):
    vk_session.method('messages.send', {'chat_id': id, 'message': text, 'random_id':0})

def BotVK(dict):
    today = datetime.date.today()
    tomorow = today + datetime.timedelta(days=1)
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
                if event.from_chat:
                    if event.object.message['text'][:1] == '!':
                        msg = event.object.message['text'][1:].upper()
                        id = event.chat_id
                        print(msg)
                        gift = ''

                        try:
                            if msg == "741963ПЕРЕЗАПУСК":
                                return True
                            msg = msg.split(' ')
                            if len(msg)==1:
                                msg.append(today.strftime('%d.%m'))
                                gift = 'Раписание на: ' + today.strftime('%d.%m')+'\n'
                            if msg[1] == 'ЗАВТРА':
                                gift = 'Раписание на: ' + tomorow.strftime('%d.%m')+'\n'
                                msg[1] = tomorow.strftime('%d.%m')
                            else:
                                gift = 'Раписание на: ' + msg[1]+'\n'
                            for i in range(1,7):

                                gift += str(i)+'&#8419;'+'  '+dict.get(msg[0]).get("Раписание").get(msg[1]).get( str(i)+ " Пара")

                            sender(id,gift)
                        except Exception:
                            sender(id, 'Неверный запрос!')
@scheduler.scheduled_job('interval',seconds=5)
def main():
    print("Бот был запущен/перезапущен")
    BotVK(parser())

if __name__ == '__main__':
    scheduler.start()
