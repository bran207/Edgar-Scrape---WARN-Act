import requests
from bs4 import BeautifulSoup


class EdgarAPI:
    baseURL = "https://www.sec.gov/"
    session = requests.session()
    
    def __init__(self):
        pass

    def returnCompanies8ks(self,cik,startNumber=0):
        results = []
        url = self.baseURL + "cgi-bin/browse-edgar?action=getcompany&CIK="+cik+"&type=8-k&dateb=&owner=exclude&start="+str(startNumber)+"&count=100"
        r = self.session.get(url)
        soup = BeautifulSoup(r.content, "lxml")
        resultsTable = soup.find("table", {"class":"tableFile2"}).find_all("tr")
        for item in resultsTable:
            columns = item.find_all("td")
            if len(columns) == 5:
                documentType = columns[0].text
                documentLink = columns[1].find("a")['href']
                date = columns[3].text
                results.append({"Document Type":documentType,"Document Link": documentLink,"Date":date})
                
        if "Next 100" in r.text:
            results += self.returnCompanies8ks(cik,startNumber=startNumber+100)
        return results

    def getIndivdual8KData(self,href):
        try:
            url = self.baseURL + href
            r = self.session.get(url)
            soup = BeautifulSoup(r.content, "lxml")

            periodOfReport = soup.find("div",{"id":"formDiv"}).find_all("div",{"class":"formGrouping"})[1].find("div",{"class":"info"}).text
            numberofDocuments = soup.find("div",{"id":"formDiv"}).find_all("div",{"class":"formGrouping"})[0].find_all("div",{"class":"info"})[2].text
            items = soup.find("div",{"id":"formDiv"}).find_all("div",{"class":"formGrouping"})[2].find("div",{"class":"info"}).text
            numberOfItems = items.count("Item")
            NineZeroOneExists = ('9.01' in items)
            fiveZeroTwoExists = ('5.02' in items)
            TwoZeroFiveExists = ('2.05' in items)
            SevenZeroOneExists = ('7.01' in items)
            documents = soup.find("table",{'summary':"Document Format Files"}).find_all('tr')
            EXNineNineOneExists = False
            for document in documents:
                columns = document.find_all('td')
                if '8-K' in str(document):
                    documentLink = columns[2].find("a")['href']
                if 'Complete submission text file' in str(document):
                    documentSize = columns[4].text
                if 'EX-99.1' in str(document):
                    EXNineNineOneExists = True
            result = {
                    "periodOfReport":periodOfReport,
                    "numberOfDocuments":numberofDocuments,
                    "NumberOfItems":numberOfItems,
                    "9.01 Exists":NineZeroOneExists,
                    "5.02 Exists":fiveZeroTwoExists,
                    "2.05 Exists":TwoZeroFiveExists,
                    "7.01 Exists":SevenZeroOneExists,
                    "EXNineNineOneExists":EXNineNineOneExists,
                    "Document Link":documentLink,
                    "Document Size":documentSize,
                    "Text File Contents":self.getTextFile(documentLink)
                }
            return result
        except:
            pass

    def getTextFile(self,href):
        url = self.baseURL + href
        r = self.session.get(url)
        return r.text.lower()
