import requests
from bs4 import BeautifulSoup
import os
import pandas as pd
import json
import re
import matplotlib.pyplot as plt
import seaborn as sns
import time


# create dir
if not os.path.exists('./work104'):
    os.mkdir('./work104')

# create empty dataFrame for final_data & final_skill
final_data_columns = ['Job', 'Company', 'Content', 'Skills', 'Salary', 'WorkExp', 'Url']
final_data = pd.DataFrame(columns=final_data_columns)
tmpData = list()
tmpskill = list()


# information for session
keyword = input('Search job from 104: ').replace(' ', '%20')
page = 1
url = "https://www.104.com.tw/jobs/search/?ro=0&kwop=7&keyword={}&expansionType=area%2Cspec%2Ccom%2Cjob%2Cwf%2Cwktm&order=15&asc=0&page={}&mode=s&jobsource=2018indexpoc".format(keyword, page)
# url = "https://www.104.com.tw/jobs/search/list?ro=0&kwop=7&keyword=Data%20Engineer&expansionType=job&order=15&asc=0&page=10&mode=s&jobsource=2018indexpoc"

userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
Referer = "https://www.104.com.tw/jobs/search/list?ro=0&kwop=7&keyword={}r&expansionType=job&order=15&asc=0&page=10&mode=s&jobsource=2018index".format(keyword)

headers = {
    "user-Agent": userAgent,
    "Referer": Referer
}

headers_forJobPage = {
    "user-Agent": userAgent,
    "Referer": Referer
}


# create session
ss = requests.session()

# crawler for __ Page
for i in range(0,10):
    res_work104 = ss.get(url, headers=headers)
    work104_soup = BeautifulSoup(res_work104.text, 'html.parser')

    data = work104_soup.select('div[class="b-block__left"]')[3:]
    for dataSoup in data:
        job = dataSoup.select('a')[0].text
        company = dataSoup.select('a')[1].text.split('\n')[0]
        content = dataSoup.select('p')[0].text
        jobUrl = 'https:' + dataSoup.select('a')[0]['href']
        jobPage_id = re.findall('job/(.*)\?', dataSoup.select('a')[0]['href'])
        jobPage_url = "https://www.104.com.tw/job/ajax/content/{}".format(jobPage_id[0])

        # request for single job Page
        res_jobPage = ss.get(jobPage_url, headers=headers_forJobPage)
        jobData = json.loads(res_jobPage.text)

        skill = [i['description'] for i in jobData['data']['condition']['specialty']]
        salary = jobData['data']['jobDetail']['salary']
        # if workExp is empty
        try:
            workExp = int(re.findall('\d', jobData['data']['condition']['workExp'])[0])
        except IndexError:
            workExp = 0
        # add to tmpData
        tmpData.append(pd.Series([job, company, content, skill, salary, workExp, jobUrl], index=final_data.columns))

        # under 3 line only for test
        # print(job, '\n', company, '\n', content, '\n', skill, '\n', workExp)
        # print('==========================================================================')
        # break
    page += 1
    print("finish page {}".format(page))
    # sleep 10 seconds for every 10 Pages
    if (i % 10 == 0):
        time.sleep(20)

# create final_data DataFrame
final_data = final_data.append(tmpData, ignore_index=True)

# create final_skill DataFrame
final_skill_columns = list()
for skill_list in final_data['Skills']:
    for skill in skill_list:
        # get first 20 skill only
        if len(final_skill_columns) == 20:
            break
        elif skill in final_skill_columns:
            pass
        else:
            final_skill_columns.append(skill)
final_skill = pd.DataFrame(columns=final_skill_columns)


# one-hot-encoding for skill & plot
for skill_list in final_data['Skills']:
    skill_ohe = [1 if skill in skill_list else 0 for skill in final_skill_columns]
    tmpskill.append(pd.Series(skill_ohe, index=final_skill_columns))

final_skill = final_skill.append(tmpskill, ignore_index=True)


# get skill bar
fig = plt.figure(figsize=(25, 5))
sns.barplot(data=final_skill, ci=None);
plt.savefig('./work104/skill_for_{}.jpg'.format(keyword).replace('%20', '_'))
# gte workExp bar
fig = plt.figure(figsize=(5, 5))
sns.countplot(x='WorkExp', data=final_data);
plt.savefig('./work104/workExp_for_{}.jpg'.format(keyword).replace('%20', '_'))

# save final_data to CSV
final_data = final_data.drop('Skills', axis=1)
final_data = pd.concat([final_data, final_skill], axis=1)
final_data.to_csv('./work104/work104_for_{}.csv'.format(keyword).replace('%20', '_'), encoding='utf-8-sig')