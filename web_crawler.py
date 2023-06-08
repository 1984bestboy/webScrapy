import time
import urllib.parse

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import requests as request
import pandas as pd
# from tabulate import tabulate
import os
import json

# 開始的url
url = "https://faq.wistronits.com/redmine/projects/portaltp/wiki"
# 用chrome
with webdriver.Chrome(service=ChromeService(ChromeDriverManager().install())) as driver:
    driver.implicitly_wait(30)
    driver.get(url)

    # 開始時要先登入
    user = driver.find_element(By.XPATH, "//input[@id='username']")
    user.send_keys("")
    psw = driver.find_element(By.XPATH, "//input[@id='password']")
    psw.send_keys("")
    login_btn = driver.find_element(By.XPATH, "//input[@id='login-submit']")  # login btn click
    login_btn.click()  # click login btn link
    # 等待時間
    time.sleep(2)
    # 空白最後要輸出的list
    datalist = []
    promptlist = []
    qalist = []
    # Selenium目前第一個頁面的內容給BS 轉成html
    soup_firstPage = BeautifulSoup(driver.page_source, 'lxml')
    need_html = soup_firstPage.find("div", {"class": "wiki wiki-page"})
    # 將class_title提取
    h2_titles = need_html.find_all("h2")
    # print(h2_titles)
    # 類標題的list
    class_text_list = []
    for h2_title in h2_titles:
        string_h2_title = h2_title.get_text()
        class_text_list.append(string_h2_title)
    # 加工刪除；新人專區
    class_text_list.pop(0)
    # print(list_class)
    uls = need_html.find_all('ul')
    # 找出所有ul內容
    for i in range(len(uls)):
        # 找出該ul下的所有li
        class_string = ""
        lis = uls[i].find_all('li')
        # 第1個ul List第一個要放"人事行政" 第2個ul List第一個要放"費用報銷"第3個ul List第一個要放"資訊設備"
        if i == 0:
            class_string = str(class_text_list[0])
        if i == 1:
            class_string = str(class_text_list[1])
        if i == 2:
            class_string = str(class_text_list[2])
        # python 變數不能重複使用
        new_class_string = class_string.replace('¶', '')
        # 標題連結列表
        q_title_link_list = []
        # 找出每個li，並獲取其文本内容
        for li in lis:
            string_a_tag = li.get_text()
            # 用requests 拿 li中的url 拿下個頁面的html
            test_string = "{}/{}".format(url, string_a_tag)
            print(test_string)
            # 用 format 方法拼接字串
            next_page_in_li = request.get(test_string)
            driver.get(test_string)
            # 下個頁面html bs4試做
            next_soup = BeautifulSoup(driver.page_source, 'lxml')
            # 取得對應文字區域
            third_page_html = next_soup.find("div", {"class": "wiki wiki-page"})
            # 取得文字區理的連結文字及連結資訊
            third_page_a_tags = third_page_html.find_all("a", {"class": "wiki-page"})
            about_q_text_list = []
            for a_tag in third_page_a_tags:
                # 取得內容
                about_q_text = a_tag.get_text()
                # print(about_q_text)
                about_q_text_list.append(about_q_text)
                # 用 format 方法拼接字串
                about_q_link = "{}/{}".format(url, about_q_text)
                # 進入最後一頁取資料
                print(about_q_link)
                # 將特殊符號轉成可用方式成功轉導
                # 使用 urllib.parse.quote() 函數將全形特殊符號轉換為百分比編碼
                encoded_url = urllib.parse.quote(about_q_link, safe=":/?&=")
                driver.get(encoded_url)
                try:
                    # 取得div內容
                    last_soup = BeautifulSoup(driver.page_source, 'lxml')
                    # 找div class="wiki wiki-page"
                    last_page_html = last_soup.find("div", {"class": "wiki wiki-page"})
                    keyword = last_soup.find("em")
                    keyword_edit_text = keyword.get_text()
                    # print(keyword_edit_text)
                    keyword_sec = keyword_edit_text.replace("Keyword:", "")
                    keyword_done = keyword_sec.replace("、", ";")
                    # 處理div內容
                    last_page_html.a.decompose()  # 刪除其中的第一個a tag
                    last_page_html.h1.decompose()  # 刪除其中的h1 tag
                    last_page_html.em.decompose()  # 刪除em
                    # for p in last_page_html.find_all('p'):
                    #     children = p.findChild()
                    # if children is None and p.get_text().strip() == "":
                    # p.extract()
                    last_page_html.a.decompose()  # 刪除其中的第2個a tag
                    # 移除指定 class 屬性的標籤
                    for tag in last_page_html.find_all(class_='wiki-anchor'):
                        tag.decompose()
                    for a in last_page_html.find_all('a'):
                        if len(a.get_text(strip=True)) == 0 and a.name not in ['br', 'img']:
                            a.extract()

                    new_last_page_html = str(last_page_html).replace('¶', '')

                    # extract_div_tag_html = last_soup.find("div", {"class": "wiki wiki-page"})
                    # 資料處理加工關鍵字
                    removed_last_html = str(new_last_page_html).replace('<div class="wiki wiki-page">', '') \
                        .replace('</div>', '') \
                        .replace('<p>', '') \
                        .replace('</p>', '') \
                        .replace('<pre>', '') \
                        .replace('</pre>', '') \
                        .replace('<h2>', '') \
                        .replace('</h2>', '') \
                        .replace('<strong>', '') \
                        .replace('</strong>', '') \
                        .replace('\n\n', '') \
                        .replace('"', '')

                    # 假設我們有一段文字
                    prompt_text = about_q_text
                    # 將文字轉換成 Python dict
                    one_data = {"prompt": str(prompt_text), "completation": removed_last_html.strip()}
                    # 放入list
                    promptlist.append(one_data)
                    # 放入datalist
                    datalist.append(
                        (new_class_string, li.get_text(), about_q_text, removed_last_html, keyword_done))
                    qalist.append((about_q_text, removed_last_html))
                except TypeError:
                    print('型別發生錯誤')
                except AttributeError:
                    print('使用不存在的屬性')
                except Exception as e:
                    print('其他問題' + str(e))
    # 將資料塞進pandas 準備輸出成excel
    df = pd.DataFrame(datalist, columns=["大類", "問題小類", "標題", "內容", "keyword "])
    df2 = pd.DataFrame(qalist, columns=["question", "answer"])
    # 匯出Excel檔案(不寫入資料索引值)
    df.to_excel("faq.xlsx", sheet_name="faq_sheet", index=False)
    df2.to_csv('qa.csv', encoding='utf-8-sig', index=False)
    # 將字典轉換成 JSON 格式
    json_data = json.dumps(promptlist, ensure_ascii=False)
    # 目前專案路徑
    file_path = os.path.dirname(os.path.abspath(__file__))
    # 切換目前os路徑
    os.chdir(file_path)
    # os新增並編輯檔案
    with open('prompt.json', 'w') as outfile:
        outfile.write(json_data)
