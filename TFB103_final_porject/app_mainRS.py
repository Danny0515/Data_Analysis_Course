from confluent_kafka import Producer
from app_accounting import conn_mysql, close_conn_mysql
import sys
import json
import ast
from pprint import pprint


goldStar = 'https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png'
grayStar = 'https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gray_star_28.png'

# Kafka information
def conn_kafka_producer(servers='localhost:9092'):
    # Catch Consumer instance Error
    def error_consumer(err):
        sys.stderr.write(f'Error: {err}')

    props = {
        'bootstrap.servers': servers,
        'error_cb': error_consumer,
        'max.in.flight.requests.per.connection': 1
    }
    producer = Producer(props)
    return producer

def kafka_producer(topic, user_id, *data):
    producer = conn_kafka_producer()
    producer.produce(topic, key=user_id, value=f'{data}')
    producer.poll(0)
    print(f'key = {user_id},\nvalue = {data}')
    producer.flush(10)

def get_questionnaire_data(user_id):
    conn, cursor = conn_mysql(host='localhost', user='testuser', pwd='qwe123456', db='tfb1031_project')
    sql = f'SELECT bnb_id, res_id, bnb_grouping, city FROM user_questionnaire WHERE user_id = "{user_id}";'
    cursor.execute(sql)
    result = cursor.fetchall()
    bnb_id = result[0][0]
    res_id = result[0][1]
    bnb_group = result[0][2]
    city = result[0][3]
    close_conn_mysql(conn, cursor)
    return bnb_id, res_id, bnb_group, city

def get_first_bnb_recommend_data(user_id):
    conn, cursor = conn_mysql(host='localhost', user='testuser', pwd='qwe123456', db='tfb1031_project')
    bnb_id, res_id, bnb_group, city = get_questionnaire_data(user_id)

    # Get bnb_w2v data
    sql_w2v = 'SELECT * FROM bnb_recommend_w2v WHERE bnb_id = %s;'
    cursor.execute(sql_w2v, (bnb_id))
    bnb_w2v = cursor.fetchall()[0]
    # Get bnb_cf data    #### 待確認 先tset用
    sql_cf = 'SELECT * FROM bnb_recommend_cf WHERE bnb_grouping = %s;'
    cursor.execute(sql_cf, (bnb_group))
    bnb_cf = cursor.fetchall()[0]
    close_conn_mysql(conn, cursor)
    return bnb_w2v, bnb_cf

def get_res_recommend_data(user_id, area):
    conn, cursor = conn_mysql(host='localhost', user='testuser', pwd='qwe123456', db='tfb1031_project')
    res_id = get_questionnaire_data(user_id)[1]
    # Get res_w2v data
    sql = 'SELECT * FROM res_recommend_w2v WHERE res_id = %s and area = %s;'
    cursor.execute(sql, (res_id, area))
    res_w2v = cursor.fetchall()[0]
    close_conn_mysql(conn, cursor)
    return res_w2v

def first_button_big(user_id):
    conn, cursor = conn_mysql(host='localhost', user='testuser', pwd='qwe123456', db='tfb1031_project')
    button = json.load(open('./line_bot_card/card_mainRS_button_big.json', 'r', encoding='utf-8'))
    global goldStar
    global grayStar
    bnb_w2v = get_first_bnb_recommend_data(user_id)[0]
    bnb_id, similarity = bnb_w2v[2:4]
    # Get bnb information from mysql
    sql = 'SELECT bnb_name, star, price, address, image_url FROM bnb WHERE bnb_id = %s;'
    cursor.execute(sql, (bnb_id))
    result = cursor.fetchall()[0]

    # Insert data to button
    button['hero']['url'] = ast.literal_eval(result[4])[0]      # hotel name
    button['body']['contents'][0]['text'] = result[0]           # hotel image url
    if result[1] != 0:
        star = result[1]
    else:
        star = 3
    button['body']['contents'][1]['contents'][5]['text'] = f"{star}星級"
    for i in range(0, star):
        button['body']['contents'][1]['contents'][i]['url'] = goldStar
    for i in range(star, 5):
        button['body']['contents'][1]['contents'][i]['url'] = grayStar
    button['body']['contents'][2]['contents'][0]['text'] = f'{str(similarity * 100)[:2]}% 適合您'   # similarity
    button['body']['contents'][2]['contents'][1]['contents'][1]['text'] = result[3]                # address
    button['body']['contents'][2]['contents'][2]['contents'][1]['text'] = f"{result[2]}"           # price
    button['footer']['contents'][0]['action']['data'] = 'like' + str(bnb_id)
    close_conn_mysql(conn, cursor)
    return button

def first_button_little(user_id):
    conn, cursor = conn_mysql(host='localhost', user='testuser', pwd='qwe123456', db='tfb1031_project')
    button = json.load(open('./line_bot_card/card_mainRS_button_little.json', 'r', encoding='utf-8'))
    global goldStar
    global grayStar
    data = get_first_bnb_recommend_data(user_id)
    bnb_id_list = [data[0][2], data[0][4], data[0][6], data[1][3], data[1][4], data[1][5]]

    # Insert data to button
    for i, bnb_id in enumerate(bnb_id_list[1:]):
        sql = 'SELECT bnb_name, star, price, address, image_url FROM bnb WHERE bnb_id = %s;'
        cursor.execute(sql, (bnb_id))
        result = cursor.fetchall()[0]
        button['contents'][i]['body']['contents'][0]['text'] = result[0]
        if result[1] != 0:
            star = result[1]
        else:
            star = 3
        button['contents'][i]['body']['contents'][1]['contents'][-1]['text'] = f"{star}星級"
        for j in range(0, star):
            button['contents'][i]['body']['contents'][1]['contents'][j]['url'] = goldStar
        for j in range(star, 5):
            button['contents'][i]['body']['contents'][1]['contents'][j]['url'] = grayStar
        try:
            button['contents'][i]['hero']['url'] = ast.literal_eval(result[4])[0]
        except IndexError:
            button['contents'][i]['hero']['url'] = 'https://cf.bstatic.com/xdata/images/hotel/max1024x768/99709614.jpg?k=96527e36238c1d3a42ba72a6365c80a2e4c40fb8ff566a9ec5ccff8c76e85cc5&o=&hp=1'
        if len(result[3]) < 18:
            button['contents'][i]['body']['contents'][2]['contents'][0]['contents'][0]['text'] = result[3]
        else:
            button['contents'][i]['body']['contents'][2]['contents'][0]['contents'][0]['text'] \
                = result[3][:17] + '...'
    close_conn_mysql(conn, cursor)
    return button

def like_button_little(user_id, bnb_id):
    conn, cursor = conn_mysql(host='localhost', user='testuser', pwd='qwe123456', db='tfb1031_project')
    button = json.load(open('./line_bot_card/card_mainRS_button_little.json', 'r', encoding='utf-8'))
    global goldStar
    global grayStar

    # Questionnaire date
    bnb_id, res_id, bnb_group, city = get_questionnaire_data(user_id)
    sql = 'SELECT area FROM bnb where bnb_id = %s ;'
    cursor.execute(sql, (user_id, area))



