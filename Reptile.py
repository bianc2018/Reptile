#-* -coding:GBK -* -
#����ע��ģ��
import requests
from requests import Timeout
from http import cookiejar
from urllib import request, error
from urllib.parse import urlparse
from urllib.parse import quote
import string
from bs4 import BeautifulSoup
import shutil
import os
import re
from multiprocessing import Process, Queue
from copy import deepcopy
from time import sleep

from lxml import etree
import time

used_url_index = []
class Reptile:
    def __init__(self,fr,headers=None,dir = r".\text"):
        self.used_url = []
        self.dir = dir
        self.root = ""
        self.datas = Queue()
        self.num = 0
        self.linkc = 0
        self.loadpro = []   
        self.downpro = []
        self.fr=None
        if os.path.exists(self.dir) is False:
            os.makedirs(self.dir)
        if headers == None: 
            self.headers ={
                            'Connection':'close',
                            'Cache-Control': 'max-age=0',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
                            'Accept-Encoding':'gzip, deflate',
                            'Accept-Language':'zh-CN,zh;q=0.9',
                            'If-None-Match':'90101f995236651aa74454922de2ad74',
                            'Referer':'http://m.xqishu.com', #'https://www.meitulu.com/',
                            'If-Modified-Since': 'Thu, 01 Jan 1970 00:00:00 GMT',
                            'Cookie':'UM_distinctid=16465f28788429-0fd68d048f20c2-454c092b-100200-16465f2878935c; CNZZDATA1776065=cnzz_eid%3D715763453-1530718604-null%26ntime%3D1530838479; Hm_lvt_5473ba66d3933b56f7003287f38c5db4=1530719294,1530762776,1530800508,1530842986; Hm_lpvt_5473ba66d3933b56f7003287f38c5db4=1530845949'
                            }
        else:
            self.headers = headers
        pass
    def craw(self,data):
        totle = 0
        for d in data:
            if d[0] == 'url':
                if d[2] not in self.used_url:
                    select = 0
                    size = 1000000
                    for i in range(0,self.loadpronum):
                        pro = self.loadpro[i]
                        if pro[1].qsize() <size:
                            select = i
                            size = pro[1].qsize()
                    self.loadpro[select][1].put(d[2])
                    print("׼�����棺url:%s,����:%d"%(d[2],select))
                    self.used_url.append(d[2])
                    self.linkc += 1
        for i in range(0,self.loadpronum):
            totle += self.loadpro[i][1].qsize()
        if totle==0:
            return 0
        return 1
        pass
    def download(self,url,rc = 5,data=None,proxies=None):
        try:
            rs = requests.request('GET', url, headers=self.headers,data=data)
            content = rs.content
            soup = BeautifulSoup(content,'lxml')
            if soup.has_attr('href'):
                if "��ҳδ�ҵ�" in soup.title.string :
                    if rc>0:
                        print("�Ҳ�����ҳ����������ҳ��:",url,rc)
                        soup = self.download(url, rc - 1)
                    else:
                        print("����ʧ�ܣ���������")
                        soup = None
        except Timeout as e:
            print('Downloader download ConnectionError or Timeout:' + str(e))
            soup = None
            if rc > 0:
                print("��ʱ,��������ҳ��:",url,rc)
                soup = self.download(url, rc - 1)
        except Exception as e:
            print('Downloader download Exception:' + str(e))
            soup = None
            if rc > 0:
                print("����,��������ҳ��:",url,rc)
                soup = self.download(url, rc - 1)
        return soup
        pass
    def loadMp(self,loadfile,id,rc=5):
        print("�����������,id:%d"%id)
        self.id = id
        while True:
            url = loadfile.get(True)
            if url == "kill":
                print("����",id,"���ؽ��̽���")
                return 0
            try:
                print("����ҳ��:",url,"���г���:",loadfile.qsize())
                s= time.time()
                rs = requests.request('GET', url, headers=self.headers)
                content = rs.content
                soup = BeautifulSoup(content,'lxml')
                if soup.has_attr('href'):
                    if "��ҳδ�ҵ�" in soup.title.string :
                        if rc>0:
                            print("�Ҳ�����ҳ����������ҳ��:",url,rc)
                            soup = self.download(url, rc - 1)
                        else:
                            print("����ʧ�ܣ���������")
                            soup = None
            except Timeout as e:
                print('Downloader download ConnectionError or Timeout:' + str(e))
                soup = None
                if rc > 0:
                    print("��ʱ,��������ҳ��:",url,rc)
                    soup = self.download(url, rc - 1)
            except Exception as e:
                print('Downloader download Exception:' + str(e))
                soup = None
                if rc > 0:
                    print("����,��������ҳ��:",url,rc)
                    soup = self.download(url, rc - 1)
            if soup:
                data = self.fr(self,soup)
                if data:
                    self.datas.put(data)
                    e= time.time()
                    print("����ҳ�����:",url,"��ʱ:%d S"%(e-s))
            pass
    def get(self,soup):
        data = self.fr(self,soup)
        return data
        pass
    def downloadMp(self,downfile,id):
        print("���ؽ�������,id:%d"%id)
        self.id = id
        while True:
            down_file = downfile.get(True)
            if down_file[0] == "kill":
                print("����",id,"���ؽ��̽���")
                return 0
            try:
                print("����",id,"��ʼ�����ļ�:",down_file[1],"url:",down_file[2])
                s = time.time()
                self.nowdown = down_file[1]
                self.num = downfile.qsize()
                url = quote(down_file[2],safe=string.printable)
                if os.path.exists(down_file[1]):
                    print('�����Ѿ����ڸ��ļ�:',down_file[1])
                    continue
                urllib.request.urlretrieve(url,down_file[1],self.callbackfunc)
                e = time.time()
                print("����",id,"�����ļ�����:",down_file[1],"url:",down_file[2],"��ʱ:%d S"%(e-s))
            except Exception as e:
                print("����",id,"#download# :",str(e))
        pass
    def callbackfunc(self,blocknum, blocksize, totalsize):
        percent = 100.0 * blocknum * blocksize / totalsize
        if percent > 100:
            percent = 100
            print("���ؽ��̣�%d,����%s��%.2f%%,�ȴ�����:%d"% (self.id,self.nowdown,percent,self.num))
    def saveMp(self,datas): #���������
        #q.full() 
        for d in datas:
            if d[0] == 'down':
                select = 0
                size = 100000
                for i in range(0,self.downpronum):
                    pro = self.downpro[i]
                    if pro[1].qsize() <size:
                        select = i
                        size = pro[1].qsize()
                self.downpro[select][1].put(d)
        pass
    def run(self,root,host,linkc = 10,downcount =5,loadcount =5):
        time_start=time.time()
        self.nurl=root
        self.root = host #root
        self.num = 0
        self.downpronum = downcount
        self.loadpronum = loadcount
        self.linkc = 0
        #����downcount��������������
        self.downpro = []
        for i in range(0,downcount):
            downfile = Queue()
            downprocess = Process(target=self.downloadMp, args=(downfile,i))
            downprocess.start()
            self.downpro.append([downprocess,downfile])
        #����loadcount���������ڻ�����ҳ
        self.loadpro = []
        for i in range(0,loadcount):
            loadfile = Queue()
            loadprocess = Process(target=self.loadMp, args=(loadfile,i))
            loadprocess.start()
            self.loadpro.append([loadprocess,loadfile])
        #��ѭ��
        self.loadpro[0][1].put(root)
        while self.linkc<=linkc:
            print(self.linkc,"find file:",self.num)
            data = self.datas.get(True)
            print("������ݴ�С:%d,ʣ�����ݶ��д�С:%d"%(len(data),self.datas.qsize()))
            self.saveMp(data)
            if self.craw(data) == 0 :
                break
        for i in range(0,loadcount):
            self.loadpro[i][1].put("kill")
            self.loadpro[i][0].join()
        for i in range(0,downcount):
            self.downpro[i][1].put(["kill",0,0])
            self.downpro[i][0].join()
        
        time_end=time.time()
        print("��ȡ����,��ʱ:%d s"%(time_end-time_start))
        print("��ȡURL��Ŀ:%d,�����ļ���Ŀ:%d"%(len(self.used_url),self.num))
        print("������",len(used_url_index))
        for uui in used_url_index:
            print("main:",uui)
        pass
    
def qs_dfr(self,soup):
    txt = soup.find_all('a')
    data= []
    for tag in txt:
        #if "/xiazai/" in self.nurl:
            #print("tag:",tag)
        try:
            if tag.has_attr('href'):
                href = tag['href']
                if tag.string == "��������(TXT���������)":
                    print("get .txt",href)
                    #print(soup.prettify())
                    txtclass = soup.find_all('p',text=re.compile(r"���ࣺ"))[0]
                    classpath = self.dir+ os.path.sep+txtclass.string
                    if os.path.exists(classpath) is False:
                        os.makedirs(classpath)
                        print("��������",txtclass)
                    name = classpath+os.path.sep+href.split('/')[-1]
                    data.append(['down',name,href])
                    self.num+=1
                else :
                    url = href
                    if 'http:' not in href:
                        url = self.root+url
                        url = url.replace("//", "/")
                        url = "http://"+url
                        data.append(['url',None,url,self.nurl])
                        if "index_" in url:
                            max = soup.find_all('a',id=re.compile(r"pt_mulu"))[0]
                            maxsize = int(max.string.split("/")[-1])+1
                            url = url.split("index_")[0]
                            if url not in used_url_index:
                                used_url_index.append(url)
                                print("maxsize:%d,in %s,used_url_index size:%d"%(maxsize,url,len(used_url_index)))
                                for i in range(2,maxsize):
                                    sub_url = url+"index_%d.html"%i
                                    #print("add url",sub_url)
                                    data.append(['url',None,sub_url,self.nurl])

        except Exception as e:
            print("#dfr# :",str(e))
    return data

#https://www.baidu.com/s?wd=hi
def baidu_dfr(self,soup):
    txt = soup.find_all('a')
    data= []
    for tag in txt:
        try:
            if tag.has_attr('href'):
                href = tag['href']
                if tag.string == "��������(TXT���������)":
                    print("get .txt",href)
                    #print(soup.prettify())
                    txtclass = soup.find_all('p',text=re.compile(r"���ࣺ"))[0]
                    classpath = self.dir+ os.path.sep+txtclass.string
                    if os.path.exists(classpath) is False:
                        os.makedirs(classpath)
                        print("��������",txtclass)
                    name = classpath+os.path.sep+href.split('/')[-1]
                    data.append(['down',name,href])
                    self.num+=1
                else :
                    url = href
                    if 'http:' not in href:
                        url = self.root+url
                        url = url.replace("//", "/")
                        url = "http://"+url
                        data.append(['url',None,url,self.nurl])
                        if "index_" in url:
                            max = soup.find_all('a',id=re.compile(r"pt_mulu"))[0]
                            maxsize = int(max.string.split("/")[-1])+1
                            url = url.split("index_")[0]
                            if url not in used_url_index:
                                used_url_index.append(url)
                                print("maxsize:%d,in %s,used_url_index size:%d"%(maxsize,url,len(used_url_index)))
                                for i in range(2,maxsize):
                                    sub_url = url+"index_%d.html"%i
                                    #print("add url",sub_url)
                                    data.append(['url',None,sub_url,self.nurl])

        except Exception as e:
            print("#dfr# :",str(e))
    return data
if __name__ == "__main__":
    r = Reptile(fr =baidu_dfr,dir=r".\newtxt")
    r.run(r"http://m.xqishu.com","m.xqishu.com",100000,downcount =5,loadcount =5)
    #r.run(r"http://m.xqishu.com/",100000)
