import pandas as pd
import requests
from bs4 import BeautifulSoup
import wget
from tqdm import tqdm
import os

curr_dir = os.getcwd()
output_folder = curr_dir+ '/Downloaded pdfs'
if not os.path.exists(output_folder):
    os.mkdir(output_folder)

# Read the CSV file
df = pd.read_excel("sample.xlsx")

baseURL = 'https://sci-hub.se'
otherBaseURL = 'https://www.doi.org'

def getUrl(url,content):
    if content.startswith('/downloads'):
        return url + content
    elif content.startswith('/tree'):
        return url + content
    elif content.startswith('/uptodate'):
        return url + content
    else:
        return 'https:/' + content


def getContent(base_url):
    print("base_url::",base_url)
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content,'html.parser')
    content = soup.find('embed').get('src').replace('#navpanes=0&view=FitH','').replace('//','/')
    if not content:
        content = soup.find("a[href$='.pdf']").replace('//','/')
    print("content::",content)
    return content


def downloadPDFUsingWGET(pdf,fileName):
    destination = os.path.join(output_folder, fileName)
    print("File::",destination,fileName)
    srcFile = os.path.join(output_folder,pdf.split("/")[-1])
    if not os.path.exists(destination):
        wget.download(pdf,out=output_folder)
        print("\nRenaming::",srcFile,)
        os.rename(srcFile, destination)
        os.remove(srcFile)
    
def dowloadPDFUsingRequest(pdf,fileName):
    destination = os.path.join(output_folder, fileName)
    print("File::",destination)
    if not os.path.exists(destination):
        r = requests.get(pdf,stream=True)
        with open(destination,'wb') as file:
            file.write(r.content)

# Iterate over each row in the DataFrame
for index, row in df.iterrows():
    doi = str(row["DOI"])
    slno = str(row["S.No"])
    print("\n\n")
    print("start downloading.....",doi,slno)
    try:
        try:
            content = getContent(base_url=baseURL+'/'+doi.strip())
            pdf = getUrl(baseURL,content)
        except Exception as conErr:
            content = getContent(base_url=otherBaseURL+'/'+doi.strip())
            pdf = getUrl(otherBaseURL,content)
        try:
            downloadPDFUsingWGET(pdf,slno+"_"+doi.strip().replace('/','_')+".pdf")
            df.loc[index, "Downloaded"] = "Yes"
        except Exception as e:
            print("Fail to download pdf using WGET:",e)
            try:
                dowloadPDFUsingRequest(pdf,slno+"_"+doi.strip().replace('/','_')+".pdf")
                df.loc[index, "Downloaded"] = "Yes"
            except Exception as err:
                print('Fail to download',err)
                df.loc[index, "Downloaded"] = "No"
    except Exception as error:
        print("Fail to get content and pdf",error)
        df.loc[index, "Downloaded"] = "No"

# Update the CSV file with the download status
df.to_excel("Downloaded_papers.xlsx", index=False)