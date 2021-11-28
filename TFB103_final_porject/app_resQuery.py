import json
import os
from conn_mysql import *


# Create a directory to save json for LINE bot FlexSendMessage
def resQuery_mkdir():
    if not os.path.isdir('./line_bot_card'):
        os.makedirs('./line_bot_card')

# Get area from user where he/she had chosen
def get_restaurant_data(area):
    host, user, pwd, db = get_mysql_config()
    conn, cursor = conn_mysql(host=host, user=user, pwd=pwd, db=db)
    sql = f'''
    SELECT res_name, image_url, article_url, address FROM test_restaurant
        WHERE area = "{area}"
        ORDER BY score DESC
        LIMIT 5;'''
    cursor.execute(sql)
    result = cursor.fetchall()
    restaurant_dict = {key[0]: key[1:] for key in result}
    close_conn_mysql(conn, cursor)
    return restaurant_dict

def get_restaurant_query_button(area):
    resQuery_mkdir()
    button = json.load(open('./line_bot_card/card_restQuery_button.json', 'r', encoding='utf-8'))
    restaurant_dict = get_restaurant_data(area)
    for i, restaurant in enumerate(restaurant_dict.items()):
        # restaurant name
        button['contents'][i]['body']['contents'][0]['text'] = restaurant[0]
        # restaurant image_url
        button['contents'][i]['hero']['url'] = restaurant[1][0]
        # restaurant article_url
        button['contents'][i]['footer']['contents'][0]['action']['uri'] = restaurant[1][1]
        # restaurant address
        # If len(address) > 18, show "address..."
        if len(restaurant[1][2]) < 18:
            button['contents'][i]['body']['contents'][2]['contents'][0]['contents'][0]['text'] = restaurant[1][2]
        else:
            button['contents'][i]['body']['contents'][2]['contents'][0]['contents'][0]['text'] \
                = restaurant[1][2][:17] + '...'
    return button


