
# coding: utf-8

# In[ ]:

#12/24 URLpicture
import requests
from bs4 import BeautifulSoup
import MySQLdb as sql
from selenium import webdriver 
import time

db = sql.connect(host = '140.136.148.212',user='sa',passwd='root', db ='test',charset='utf8')
cursor = db.cursor()

urlhome  = 'https://www.urcosme.com'
url_pdc  = '/find-product/'  

page    =  1
href = {'is_ajax':'ture','page':'%s'%page}

id_num = 1

url_page = 2
end      = 2
#####################################

createquery =("CREATE TABLE IF NOT EXISTS `otherlip` (`id` int(10) NOT NULL,`name` char(150) NOT NULL,`brand` char(150) NOT NULL,`img` char(150) NOT NULL,`point` char(150) NOT NULL,`price` char(150) NOT NULL) ENGINE=InnoDB  DEFAULT CHARSET=utf8 ;")
query = ("Insert into otherlip (id,name,brand,img,point,price) VALUES (%s,%s,%s,%s,%s,%s)")

creatquery_ingredient=("CREATE TABLE IF NOT EXISTS `otherlip_ingredient` (`name` char(150) NOT NULL,`Eingredient` char(150) NOT NULL,`Cingredient` char(150) NOT NULL,`function` char(150) NOT NULL,`safety` char(150) NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8;")
query1 = ("select name from otherlip")
query2 = ("Insert into otherlip_ingredient(name,Eingredient,Cingredient,function,safety) VALUES (%s,%s,%s,%s,%s)")

#####################################
cursor.execute(createquery)

while url_page <  end+1 :
    href = {'is_ajax':'ture','page':'%s'%page}
    res = requests.get('%s%s%s' % (urlhome,url_pdc,url_page), params=href)
    soup = BeautifulSoup(res.text)
#    print ('loc: %s%s%s%s' % (urlhome,url_pdc,url_page,href))
    while len(soup.find_all(rel = 'next')) > 0:
        print ("---------[%s]---------" %page)
        for item in soup.select('.item-info'):
            #print item.select('.item-name')[0].text, item.select('.item-brand')[0].text
            
            img = item.select('img')[0].get('src')
            
#            print img
            
            upoint = item.select('.uc-point')[0].text
            point = upoint.split(' ')
#            print point[1]
            
            data =(id_num,
                   item.select('.item-name')[0].text, 
                   item.select('.item-brand')[0].text,
                   img,
                   point[1],
                   item.select('.price')[0].text)
            cursor.execute(query,data)
            db.commit()
            id_num+=1
        page += 1
        
        href = {'is_ajax':'ture','page':'%s'%page}
        res = requests.get('%s%s%s' % (urlhome,url_pdc,url_page), params=href)
        soup = BeautifulSoup(res.text)
        
        print  ('%s%s%s%s' % (urlhome,url_pdc,url_page,href))  
    print ("---------[last_page]---------" )
           
    for item in soup.select('.item-info'):
        #print item.select('.item-name')[0].text, item.select('.item-brand')[0].text
              
        img = item.select('img')[0].get('src')
        
        upoint = item.select('.uc-point')[0].text
        point = upoint.split(' ')
        
        data =( id_num,   
                item.select('.item-name')[0].text, 
                item.select('.item-brand')[0].text,
                img,
                point[1],
                item.select('.price')[0].text)
        
        cursor.execute(query,data)
        db.commit()
    
    id_num = 1
    page = 1
    url_page += 1

##########   ingredient    ##########

cursor.execute(creatquery_ingredient)

cursor.execute(query1)
results = cursor.fetchall()

url ='http://www.cosdna.com/cht/'

i =0
count =0
browser = webdriver.Chrome()
for record in results:
    count += 1
    browser.get('%sproduct.php'%url)
    browser.find_element_by_id("q").send_keys(u"%s" % record)
    browser.find_element_by_id("b").click()
    try:
        browser.find_element_by_partial_link_text(u"%s"%record).click() 
#        print record
        time.sleep(1)
        soup = BeautifulSoup(browser.page_source)
    except:
        try:
            browser.find_element_by_class_name('Keyword2').click()
            time.sleep(1)
            soup = BeautifulSoup(browser.page_source)
        except:
            continue

    for item in soup('tr',{'valign':'top'}):
        Etitle =item.select('.iStuffETitle')[0].text
        Ctitle =item.select('.iStuffCTitle')[0].text
        try:
            usage = item.select('.iStuffChar')[0].text
            usage = usage.replace(u'‧',' ')
            usage = usage.replace(u'.',' ')
        except:
            usage = "unknown"
        
        try:
            safetyL =item.select('.SafetyL')[0].text
        except:    
            safetyL = "unknown"
            
        try:
            safetyM =item.select('.SafetyM')[0].text
        except:    
            safetyM = 0
            
        try:
            safetyH =item.select('.SafetyM')[0].text
        except:    
            safetyH = 0
        
        if(safetyH > 0):
#            print("%s %s %s %s" % (Etitle,Ctitle,usage,safetyH))
            data =(record[i],Etitle,Ctitle,usage,safetyH)
        elif(safetyM > 0):
#            print("%s %s %s %s" % (Etitle,Ctitle,usage,safetyM))
            data =(record[i],Etitle,Ctitle,usage,safetyM)
        else :
#            print("%s %s %s %s" % (Etitle,Ctitle,usage,safetyL))
            data =(record[i],Etitle,Ctitle,usage,safetyL)
        cursor.execute(query2 , data)
        db.commit() 
    print count," ",  

db.close()

