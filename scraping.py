#This is for scaping top 250 movies on the douban website
#Yihui created by 12/25/2022


#analyse web and get data
from bs4 import BeautifulSoup
#do regex match
import re
#make url to get web data
import urllib.request,urllib.error
import xlwt #excel
import sqlite3 #database

#get a specific url data
def askUrl(url):
    #pretend to be browser to send requests
    head = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
    }#user agent: let server knows that what kinds of files we can recieve

    #make a object req
    req = urllib.request.Request(url=url,headers=head)
    data = ""
    try:
        #open the object
        resp = urllib.request.urlopen(req)
        #decode the data from site
        data = resp.read().decode("utf-8")
       # print(data)
    except urllib.error.URLError as err:
        if hasattr(err,"code"):  #if it has attribute "code"
            print(err.code)
        if hasattr(err,"reason"):   #if it has attribute "reason"
            print(err.reason)
    return data

def main():
    baseurl= "https://movie.douban.com/top250?start="
    #1.scraping the data
    datalist = getData(baseurl)
    savepath = "doubantop250movies.xls"
    #3.store the data
    saveData(datalist,savepath)

#create a object of regex, which is the pattern of regex 
#This is what the link looks like: <a href="https://movie.douban.com/subject/1291546/">
findlink = re.compile(r'<a href="(.*?)">')

#find the regex of image src
#EX. <img alt="怦然心动" class="" src="https://img1.doubanio.com/view/photo/s_ratio_poster/public/p501177648.jpg" width="100"/>
findImgSrc = re.compile(r'<img.*src="(.*?)"',re.S)#re.S include line break

#find regex of movie's title
#Ex. <span class="title">怦然心动</span>
findTitle = re.compile(r'<span class="title">(.*)</span>')

#find the regex of movie's rate 
#Ex. <span class="rating_num" property="v:average">9.1</span>
findRate = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')

#find the regex of movie's intro 
#Ex. <span class="inq">真正的幸福是来自内心深处。</span>
findIntro = re.compile(r'<span class="inq">(.*)</span>')

#find the regex of movie's related content
#Ex. <p class="">
#     导演: 奥利维·那卡什 Olivier Nakache / 艾力克·托兰达 Eric Toledano   主...<br/>
#    2011 / 法国 / 剧情 喜剧
#</p>
findContent = re.compile(r'<p class="">(.*?)</p>',re.S)


def getData(baseurl):
    print("Start scraping data...")
    datalist = []

  #ALL the pages
    for i in range(0,10):  
        # get different url for each page
        url = baseurl + str(i*25)
        #store each page's data
        htmlData = askUrl(url)

        #2.analyze the data
        
        soup = BeautifulSoup(htmlData,"html.parser")
        #find all the part meets the needs, then make a list
        for item in soup.find_all('div',class_="item"):
            data = [] #store the info for ONE movie
            item = str(item)#convert it to string
            
            #find the FIRST thing matches "findlink" in "item"
            #which is the link of movie's description
            link = re.findall(findlink,item)[0]
            data.append(link)#add link

            imgLink = re.findall(findImgSrc,item)[0]#find the first img link in item
            data.append(imgLink)#add image link

            titles = re.findall(findTitle,item) # find all titles(CN/Other)
            if(len(titles) == 2):#if find multiple titles
                CNtitle = titles[0]
                data.append(CNtitle)
                Otitle = titles[1].replace("/","")#get rid of /
                data.append(Otitle)
            else:#only ONE title
                data.append(titles[0])
                data.append(' ')#reserve the place

            Rate = re.findall(findRate,item)[0]
            data.append(Rate)#add rating

            intro = re.findall(findIntro,item)#MAYBE Empty
            if len(intro) != 0:
                intro = intro[0].replace(". ","")#delete .
                data.append(intro)
            else:
                data.append(" ")#reserve the place

            relatedCon = re.findall(findContent,item)[0]#get movie's related content
            relatedCon = re.sub('<br(\s+)?/>(\s+)?'," ",relatedCon) #delete <br/>
            data.append(relatedCon.strip()) #strip(): remove spaces

            #THEN, add ONE movie's info into datalist
            datalist.append(data)
    print("Scrabing Finished!")
    return datalist


def saveData(datalist,path):
    print("Save data...")
    #create excel obj
    workbook = xlwt.Workbook(encoding="utf-8",style_compression=0)
    #create sheet
    worksheet = workbook.add_sheet('Top250Info',cell_overwrite_ok=True)
    col = ("Link of description","Iamge link","Title(CN)","Title(Other)","Rating","Intro","Related Content")
    #write the heading(first column)
    for i in range(0,7):
        worksheet.write(0,i,col[i])

    #write in the info
    for i in range(0,250):
        print("LINE: %d" %(i+1))
        tmpdata = datalist[i]
        for j in range(0,7):
            worksheet.write(i+1,j,tmpdata[j])
    
    workbook.save(path)
    print("Save finished!")

if __name__ == "__main__":
    main()