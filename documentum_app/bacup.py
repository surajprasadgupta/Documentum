import os
import sys
import documentum_app
from django.contrib.auth.models import User
from django.shortcuts import render,redirect
from documentum_app.forms import UploadFilesForm
from documentum_app.forms import PostContantForm
from documentum_app.models import DocumentumFiles
from django.core.paginator import Paginator
import pytesseract
from pytesseract import Output
from PIL import Image
from cv2 import cv2
from documentum_app.models import *

from django.contrib import messages
from django.http import HttpResponse, JsonResponse,HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate,login as login_orth,logout
import PyPDF2
from xlrd import open_workbook
import csv
import nltk
from nltk.corpus import stopwords
from stop_words import get_stop_words
from docx import Document
from nameparser.parser import HumanName
import re
# import spacy
# from spacy.matcher import Matcher
from nltk.corpus import stopwords
import operator
from django.db.models import Q
import sys
import os
import comtypes.client
from comtypes.client import CreateObject



# Create your views here.
def index(request):

    return render(request,'index1.html')

    
def login(request):

  return render(request,'index.html')

def dashboard(request):
  # print(request.POST)
  
  if request.method=='POST':
  
    company_code=request.POST.get('company_code')
    request.session['company_code']=company_code
    company=Company.objects.filter(company_code=company_code).first()

    return render(request,'dashboard.html',{'company':company})


  else:
    company_code=request.session['company_code']
    company=Company.objects.filter(company_code=company_code).first()
    users=Post.objects.filter(company_code=company_code)
    # for user in users:
    #   print(user.user)
    # print(users.distinct())
    return render(request,'dashboard.html',{'company':company})


  
def choose_company(request):

  return render(request,'choose_company.html')  

def user_register(request):
    print(request.POST)
    if request.method=='POST':
      username=request.POST.get("username")
      email=request.POST.get("email")
      password=request.POST.get("password")
      password2=request.POST.get("confirm-password")
      if password==password2:
        if User.objects.filter(username=username).exists():
          messages.success(request, 'User name already exist....')  
          return HttpResponseRedirect(reverse('documentum_app:login'))  
        elif User.objects.filter(email=email).exists():
          messages.success(request, 'Email already taken....')  
          return HttpResponseRedirect(reverse('documentum_app:login')) 

        else:
          user=User.objects.create_user(username=username,email=email,password=password)
          print("success")
          user.save()
          messages.success(request, ' User create Successfully .')  
          return HttpResponseRedirect(reverse('documentum_app:home'))  
      else:
        messages.success(request, 'Password does not match .')  
        return HttpResponseRedirect(reverse('documentum_app:home'))  

    else:
      print("elseeeeeeeeeeee")
      return render(request,"file_upload.html")

def account_login(request):

  # print(request.POST)
  username=request.POST.get('username')
  password=request.POST.get('password')
  print(username,password)
  user=authenticate(request,username=username,password=password)

  if user:
    login_orth(request, user)
    company=Company.objects.all()
    # for comp in company:
    #   print(comp.company_name)
    # messages.success(request, ' User login Successfully .')  
    # return HttpResponseRedirect(reverse('documentum_app:choose_company')) 
    return render(request,'choose_company.html',{'company':company})
  else:
    messages.success(request, 'Username or Password does not match .')  
    return HttpResponseRedirect(reverse('documentum_app:login'))


   

def account_logout(request):
  logout(request)
  return render(request,'index.html')     

  # *******************************************************ocr*******************************************************************      

def pdftotext(img_url):
  
  img_type=img_url.split(".")[1]
  APP_ROOT = os.path.abspath(documentum_app.__path__[0])
  file_path = os.path.join('C:/Users/ASUS/Desktop/project/documentum/'+str(img_url))
  stop_words = get_stop_words('english')

  if img_type=="pdf":
    # img = cv2.imread(file_path)
    # print(img)
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    pdf_file = open(file_path, 'rb')
    print("hello",pdf_file)
    
    read_pdf = PyPDF2.PdfFileReader(pdf_file)
    # print(read_pdf)
    number_of_pages = read_pdf.getNumPages()
    # print(number_of_pages)
    page_content=""
    for i in range(number_of_pages):

      page = read_pdf.getPage(i)
      content = page.extractText()
      page_content+=content
    # print(page_content)
    # print(page_content.encode('utf-8',errors='ignore'),"gggggggggggggggggg")
    text=page_content
    # print(text)
    text_list=page_content.split(" ")
    text_word= [word for word in text_list if word not in stop_words] 
    text_remove_rep=list(set(text_word))

    # print(text_remove_rep)
      


    return text


  elif img_type=="jpg" or img_type=="jpeg" or img_type=="png":

    img = cv2.imread(file_path)
    # print(img)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    print(pytesseract.image_to_data(Image.open(file_path)))
    tesseract_output = pytesseract.image_to_string(Image.fromarray(img),lang="eng")
    # print("insidetesseract",tesseract_output)
    text=tesseract_output

    return text

  elif img_type=="doc" or img_type=="docx":
    fullText=[]
    document = Document(file_path)

    for para in document.paragraphs:
        fullText.append(para.text)
    return '\n'.join(fullText)



  elif img_type=="txt":
    text_file=open(file_url,'r')
    content=text_fle.read()
    # print(content)
    return


  elif img_type=="csv":
    text=[]
    string_list=[]
    string_seq=""
    with open(file_path,'rt')as f:
      data = csv.reader(f)
      for row in data:
        text.append(row)
            # print(row)
      # text=row 
    
    for text_list in text:
      print(text)
      string_list=string_list + text_list
    print('suraj',string_list) 
    for string in string_list:
      string_seq+=string
    print('DDDDDDDDDDDDDDDDDDDDD',string_seq)  


    return string_seq


  elif img_type=="xlsx" or img_type=="xlsm" or img_type=="xls":  
    

    book = open_workbook(file_path)
    sheet = book.sheet_by_index(0)

    # read header values into the list    
    keys = [sheet.cell(0, col_index).value for col_index in range(sheet.ncols)]
  
    dict_list = []
    for row_index in range(1, sheet.nrows):
        d = {keys[col_index]: sheet.cell(row_index, col_index).value 
            for col_index in range(sheet.ncols)}
        dict_list.append(d)

    # print('ffffffff',dict_list)
    all_dict=[]
    for d in dict_list:
      for k, v in d.items():
        all_dict.append(k)
        all_dict.append(v)
    # print(all_dict)
      # print(d)
      # all_dict.update(d)
    if '' in all_dict:
      all_dict.remove('')
    else:
      pass
     
    string_list=""
    string_list=','.join(str(s) for s in all_dict)
    text=string_list
    return text
  else:
    text="file formate does not match"
    return text   

  # print('/home/finsq/Desktop/documentum/documentum/media/static',img_url)
  # print(img_url)
  APP_ROOT = os.path.abspath(documentum_app.__path__[0])
  file_path = os.path.join('/home/finsq/Desktop/documentum/documentum'+str(img_url))
  # print('ddddddddddd',file_path)
  # path="/home/finsq/Desktop/documentum/documentum"
  # img_path=os.path.join(path+img_url)
  # print('dddd',img_path)
  out = os.path.isdir(file_path) 
  # print(out) 
  # print(pytesseract.image_to_string(Image.open(file_path)))
  # tesseract_output = pytesseract.image_to_string(Image.fromarray(img_url))

  img = cv2.imread(file_path)
  # print(img)
  img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  print(pytesseract.image_to_data(Image.open(file_path)))
  tesseract_output = pytesseract.image_to_string(Image.fromarray(img),lang="eng")
  # print("insidetesseract",tesseract_output)

  return 


# def getname(textstring,debug=False):
#   word_tokenize = nltk.data.load('nltk:tokenizers/punkt/english.pickle')
#   lines=[el.strip() for el in textstring.split("\n") if len(el) > 0]
#   lines = [nltk.word_tokenize(el) for el in lines]
#   lines = [nltk.pos_tag(el) for el in lines]
#   grammar = r'NAME: {<NN.*>*}'
#   chunkParser = nltk.RegexpParser(grammar)
#   indianNames = open("/home/finsq/Desktop/documentum/documentum/static/upload_files/allNames.txt", "r",encoding = "ISO-8859-1").read().lower()
#   indianNames = set(indianNames.split())
#   nameHits = []
#   otherNameHits = []
#   name = None
#   for tagged_tokens in lines:

#     chunked_tokens = chunkParser.parse(tagged_tokens)
#     for subtree in chunked_tokens.subtrees():
#         if subtree.label() == 'NAME':
#             for ind, leaf in enumerate(subtree.leaves()):
#                 if leaf[0].lower() in indianNames and 'NN' in leaf[1]:
# #                    print(leaf)
# #                    for el in subtree.leaves()[ind:ind+3]:
# #                        print(el[0])
# #                        hit = " ".join(el[0])
#                     hit = " ".join([el[0] for el in subtree.leaves()[ind:ind+3]])
#                     nameHits.append(hit)
    
#     print(nameHits) 
#     if len(nameHits) > 0:
#       name = " ".join([el[0].upper()+el[1:].lower() for el in nameHits[0].split() if len(el)>0])
   
#       print(name)
#   return     
# def get_name(text):
#   # load pre-trained model
#   nlp = spacy.load('en_core_web_sm')

#   # initialize matcher with a vocab
#   matcher = Matcher(nlp.vocab)
#   text_list=text.lower().split("\n")
#   nlp_text = nlp(str(text_list))
    
#   # First name and Last name are always Proper Nouns
#   pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]
  
#   matcher.add(' ', None, *pattern)
  
#   matches = matcher(nlp_text)
  
#   for match_id, start, end in matches:
#       span = nlp_text[start:end]

#   return span.text

                
def get_human_names(text):
  print(text)
  import nltk

   #read all lines
  sentences = nltk.sent_tokenize(text) #tokenize sentences
  nouns = [] #empty to array to hold all nouns

  for sentence in sentences:
       for word,pos in nltk.pos_tag(nltk.word_tokenize(str(sentence))):
           if (pos == 'NN' ):
               nouns.append(word)
  print('###########',nouns)             
 
  # person_list = []
  # person =[]
    
  # try:
  #   tokens = nltk.tokenize.word_tokenize(text)
  #   pos = nltk.pos_tag(tokens)
  #   sentt = nltk.ne_chunk(pos, binary = False)
  #   name = ""
  #   for subtree in sentt.subtrees(filter=lambda t: t.label() == 'PERSON'):
  #       for leaf in subtree.leaves():
  #           person.append(leaf[0])
  #       if len(person) > 1: #avoid grabbing lone surnames
  #           for part in person:
  #               name += part + ' '
  #           if name[:-1] not in person_list:
  #               person_list.append(name[:-1])
  #           name = ''
  #       person = []
  #   print(person_list)    
  #   return str(person_list)    
   
  # except Exception as e:
  #   print(e)
  # return person_list
  return nouns

def get_phone(text):
  text_list=text.lower().split("\n")
  while ' ' in text_list:
    text_list.remove(' ')
    # text_list.remove('')
    # text_list.remove(':')
  # print(text_list)
  # pattern=re.compile(r'(?:(?:\+?([1-9]|[0-9][0-9]|[0-9][0-9][0-9])\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([0-9][1-9]|[0-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?')
  pattern=re.compile('[^\d]\d{10}[^\d]')
  
  match = pattern.findall(str(text_list)) 
  # print(match)
  contact_no=match

  return contact_no

def get_email(text):
  email=None
  try:
    pattern = re.compile(r'\S*@\S*')
    matches = pattern.findall(text) # Gets all email addresses as a list
    email = matches
    # print(email)
  except Exception as e:
      print (e)
  return  email

def get_address(text):
  address=None
  try:
    pattern = re.compile(r'/\s+(\d{2,5}\s+)(?![a|p]m\b)(([a-zA-Z|\s+]{1,5}){1,2})?([\s|\,|.]+)?(([a-zA-Z|\s+]{1,30}){1,4})(court|ct|street|st|drive|dr|lane|ln|road|rd|blvd|collony)([\s|\,|.|\;]+)?(([a-zA-Z|\s+]{1,30}){1,2})([\s|\,|.]+)?\b(AK|AL|AR|AZ|CA|CO|CT|DC|DE|FL|GA|GU|HI|IA|ID|IL|IN|KS|KY|LA|MA|MD|ME|MI|MN|MO|MS|MT|NC|ND|NE|NH|NJ|NM|NV|NY|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VA|VI|VT|WA|WI|WV|WY)([\s|\,|.]+)?(\s+\d{5})?([\s|\,|.]+)/i')
    matches = pattern.findall(text) # Gets all email addresses as a list
    address = matches
  except Exception as e:
      print (e)

  return address



def get_skill(text):
  skill=open("/home/finsq/Desktop/documentum/documentum/static/upload_files/skill.txt", "r",encoding = "ISO-8859-1").read().lower()
  
  text_list=text.lower().split("\n")
  skill_list=skill.split(" ")
  skills=list(set(skill_list) & set(text_list))
  while '' in skills:
    skills.remove('')
  # print(skills)

  # skills=[skill for skill in skill_list if skill in text_list]
  # print(skills)
  # file1 = set(line.strip() for line in open('/home/finsq/Desktop/documentum/documentum/static/upload_files/allNames.txt'))
  # file2 = set(line.strip() for line in open('file2.txt'))

  # for line in file1 & file2:
  #     if line:
  #         print line
  
  return skills

def get_city(text):
  city_list=open("/home/finsq/Desktop/documentum/documentum/static/upload_files/city_name.txt", "r",encoding = "ISO-8859-1").read().lower()
  text_list=text.lower().split("\n")
  city_name=list(set(city_list) & set(text_list))
  # print(city_name)


  return

# def get_educations(text):
#   EDUCATION = [
#             'BE','B.E.', 'B.E', 'BS', 'B.S', 
#             'ME', 'M.E', 'M.E.', 'MS', 'M.S', 
#             'BTECH', 'B.TECH', 'M.TECH', 'MTECH', 
#             'SSC', 'HSC', 'CBSE', 'ICSE', 'X', 'XII'
#         ]
#   nlp = spacy.load('en_core_web_sm')

#   # Grad all general stop words
#   STOPWORDS = set(stopwords.words('english'))
#   nlp_text = nlp(text)

#   # Sentence Tokenizer
#   nlp_text = [sent.string.strip() for sent in nlp_text.sents]
#   print(nlp_text)
#   edu = {}
#   # Extract education degree
#   for index, text in enumerate(nlp_text):
#       for tex in text.split():
#           # Replace all special symbols
#           tex = re.sub(r'[?|$|.|!|,]', r'', tex)
#           if tex.upper() in EDUCATION and tex not in STOPWORDS:
#               edu[tex] = text + nlp_text[index + 1]
#   # Extract year
#   education = []
#   for key in edu.keys():
#       year = re.search(re.compile(r'(((20|19)(\d{2})))'), edu[key])
#       if year:
#           education.append((key, ''.join(year[0])))
#       else:
#           education.append(key)

#   return education
            



def file_upload(request):
    print(request.POST)
 
    if request.method=='POST':
     
        uploaded_filelist=request.FILES.getlist("file_upload")
        no_offile_uploaded=len(uploaded_filelist)
        if uploaded_filelist!='':
          # print(uploaded_filelist)
          form=UploadFilesForm(request.POST,request.FILES)
          if form.is_valid():
              for file_name in uploaded_filelist:
                instance=DocumentumFiles(file_upload=file_name)
                instance.save()
        
              # last = QuerySet[len(uploaded_filelist) - 1] if QuerySet else None
              files = DocumentumFiles.objects.all().order_by('-id')[:no_offile_uploaded]
            
              
              text=[]
              tag_list=[]
              file_urls=[]
              for data in files:
                print(data.file_upload.url.split(".")[-1])
                file_type=data.file_upload.url.split(".")[-1]
                if file_type=='doc'or file_type=='docx':
                  print("hello")
                  import win32com.client
                  import time
                  import pythoncom
                  pythoncom.CoInitialize()
                  in_file = os.path.join('C:/Users/ASUS/Desktop/project/documentum/'+str(data.file_upload.url))
                  # in_file=str(data.file_upload.url)
                  out_file = in_file
                  word = win32com.client.Dispatch("Word.Application")
                  time.sleep(3)
                  new_name = in_file.replace(".docx", r".pdf")
                  worddoc = word.Documents.Open(in_file)

                  worddoc.SaveAs(new_name, FileFormat = 17)
                  print(new_name )
                  file_urls.append(new_name.split("//")[-1])
                  # worddoc.Close()
                  # word.Quit()
                elif file_type=='xlsx' or file_type=='xls':
                  import win32com.client
                  import time
                  import pythoncom
                  pythoncom.CoInitialize()
                  # in_file = os.path.join('C:/Users/ASUS/Desktop/project/documentum/'+str(data.file_upload.url))
                  in_file = os.path.join('C:\\Users\\ASUS\\Desktop\\project\\documentum\\'+str(data.file_upload.url))
                  # in_file=str(data.file_upload.url)
                  # out_file = in_file
                  print(in_file)
                  from win32com import client

                  xlApp = client.Dispatch("Excel.Application")
                
                  new_name = in_file.replace(".xlsx"or ".xls", r".xlsx.pdf")
                  
                  books = xlApp.Workbooks.Open(in_file)
                  
                  # books.SaveAs(new_name, FileFormat = 51)
                  ws = books.Worksheets[0]
                  
                  ws.Visible = 1
                  ws.ExportAsFixedFormat(0, in_file)
                  
                  # ws.SaveAs(new_name, FileFormat=57)
                  # print('ggggggggggggggggggggggg',new_name )
                  file_urls.append(new_name.split("\/")[-1])

                elif file_type=="csv":
                  from win32com import client
                  in_file = os.path.join('C:\\Users\\ASUS\\Desktop\\project\\documentum\\'+str(data.file_upload.url))
                  csvApp = client.Dispatch("Excel.Application")
                  new_name=in_file.replace(".csv" , r".csv.pdf")
                  books=csvApp.workbooks.open(in_file)
                  ws = books.Worksheets[0]
                  print("4")
                  ws.Visible = 1
                  ws.ExportAsFixedFormat(0, in_file)
                  file_urls.append(new_name.split("\/")[-1])

                else:
                  print("fail buddy")
                  file_urls.append(data.file_upload.url)
                  

            
                # file_urls.append(data.file_upload.url)
                path=data.file_upload.url
                doc_list=pdftotext(path)
                print(doc_list)
                tags=get_human_names(doc_list)
                # tags="suraj"
                # print(tags)
                text_list=text.append(doc_list)
                tag_list.append(tags)
                # tag_list="suraj"

                # tags=get_human_names(text)

              items=list(zip(file_urls,text,tag_list))
              item_list=[]
              for item in items:
                item_list.append(list(item))
            
              

              # ______________________________pagination_______________________________

              paginator = Paginator(item_list, 1) # Show 1 contacts per page
              page = request.GET.get('page')
              item_list = paginator.get_page(page)


              # ______________________________pagination_______________________________



                # print(text)

              # print(files.file_upload)
              # path=files.file_upload.url
              # print(path.split(".")[1])
              # text=pdftotext(path)
              # print(text)
              # name=get_name(text)
              # print(name)
              # tags=get_human_names(text)
              # print(tags)
              # contact_no=get_phone(text)
              # print('contact number',contact_no)
              # email=get_email(text)
              # print('email',email)
              # address=get_address(text)
              # print('address',address)
              # skill=get_skill(text)
              # city_name=get_city(text)
              # education=get_educations(text)
              # print(education)
              
              return render(request,"file_upload.html",{'file':files,'text':text,'file_name':file_name,'no_offile_uploaded':no_offile_uploaded,'item_list':item_list} )
          else:
            messages.success(request, 'files Not Choosen .')  
            return HttpResponseRedirect(reverse('documentum_app:file_upload'))

        else:
            print(form.errors) 
            files = DocumentumFiles.objects.all().order_by('-id')[:no_offile_uploaded]  
            text=[]
            tag_list=[]
            file_urls=[]
            for data in files:
              file_urls.append(data.file_upload.url)
              path=data.file_upload.url
              doc_list=pdftotext(path)
              tags=get_human_names(doc_list)
              text_list=text.append(doc_list)
              tag_list.append(tags)
              
              # tags=get_human_names(text)

            items=list(zip(file_urls,text,tag_list))
            item_list=[]
            for item in items:
              item_list.append(list(item))

            # ______________________________pagination_______________________________

            paginator = Paginator(item_list, 1) # Show 1 contacts per page
            page = request.GET.get('page')
            item_list = paginator.get_page(page)

            # ______________________________pagination_______________________________

            return render(request,"file_upload.html",{'file':files,'file_name':file_name,'item_list':item_list,'no_offile_uploaded':no_offile_uploaded} )
    else:

      if request.GET.get('page') !=None:
        no_offile_uploaded=int(request.GET.get('count'))
        files = DocumentumFiles.objects.all().order_by('-id')[:no_offile_uploaded]
        
        text=[]
        tag_list=[]
        file_urls=[]
        for data in files:
          file_urls.append(data.file_upload.url)
          path=data.file_upload.url
          doc_list=pdftotext(path)
          
          tags=get_human_names(doc_list)
          text_list=text.append(doc_list)
          tag_list.append(tags)
          
          # tags=get_human_names(text)

        items=list(zip(file_urls,text,tag_list))
        item_list=[]
        for item in items:
         
          item_list.append(list(item))

            # ______________________________pagination_______________________________

        paginator = Paginator(item_list, 1) # Show 1 contacts per page
        page = request.GET.get('page')
        item_list = paginator.get_page(page)

            # ______________________________pagination_______________________________



        return render(request,"file_upload.html",{'file':files,'item_list':item_list,'no_offile_uploaded':no_offile_uploaded} )

      return render(request,'file_upload.html')

def search_keyword(request):
  # print(request.POST)
  tags=request.POST.get('tags')

  startdate=request.POST.get('startdate')
  enddate=request.POST.get('enddate')
  emp_name=request.POST.get('emp_name')
  file_name=request.POST.get('file_name')
  company_code=request.session['company_code']

  
  if request.method=='POST' and tags!=None:
   
    search_keyword=request.POST.get('tags')
    search_list=search_keyword.split(',')
    
    # q_object=""
    q_object = Q(content__icontains=search_list[0]) & Q(content__icontains=search_list[0])
    
    for item in search_list:
        q_object.add((Q(content__icontains=item) & Q(content__icontains=item)), q_object.connector)
   
    posts = Post.objects.filter(q_object ).filter(company_code=company_code).order_by('-id')
   
    # for post in posts:
    #   print(post.file_url)
    return render(request,'search_keyword.html',{'posts':posts})  
  elif request.method=='POST'and startdate!=None:
    posts = Post.objects.filter(company_code=company_code,created_on__range=(startdate,enddate) ).order_by('-id')
    
    return render(request,'search_keyword.html',{'posts':posts}) 


  elif request.method=='POST'and emp_name!=None:
    doc_list=Post.objects.filter(company_code=company_code,user=emp_name).order_by('-id')
   

    return render(request,'search_keyword.html',{'posts':doc_list})

  elif request.method=='POST' and file_name!=None:

    doc_list=Post.objects.filter(company_code=company_code,file_name__icontains=file_name).order_by('-id')


    return render(request,'search_keyword.html',{'posts':doc_list})   
  else:
  
    return render(request,'search_keyword.html')

def searchby_name(request):
  users_temp = User.objects.all()
  users = []
  for user in users_temp:
    users.append([user.id, user.username])


  return JsonResponse({'error': "False",'users':users})

  

def create_contant(request):
  print(request.POST)
  if request.method=='POST':
   
    file_name=request.POST.get('file_name').split("/")[-1]
  
    file_url=request.POST.get('uploaded_file')
    
    # if "tags" in request.POST:
    #   tags=request.POST['tags']
    #   tag_list=[Tags.objects.get_or_create(name=tag)[0] for tag in tags.split(',')]
    # company_code=request.session['company_code']
    company_code=request.POST.get('company_code')
    request.session["company_code"] = company_code


    form=PostContantForm(request.POST)

    if form.is_valid():
      form_contant = form.save(commit = False)
      form_contant.company_code=Company.objects.filter(company_code=company_code).first()
      form_contant.user=request.POST.get('user')
      form_contant.file_url=file_url
      form_contant.content=request.POST.get('content')
      form_contant.file_name=file_name
      form_contant.is_private=request.POST.get('is_private')
      # for tags in tag_list:
      #   form_contant.tags.add(tags)
     
      form_contant.save()
      if request.POST.get('tags', ''):
    
        tags = request.POST.get("tags")
        splitted_tags = tags.split(",")
        for t in splitted_tags:
            tag = Tags.objects.filter(name=t)
            if tag:
                tag = tag[0]
            else:
                tag = Tags.objects.create(name=t)
            form_contant.tags.add(tag)
            print(form_contant)
          
      # return render(request,'search_keyword.html')
      # messages.success(request, ' Data Save Successfully .')  
      return HttpResponseRedirect(reverse('documentum_app:file_upload')) 
    else:
  
      print(form.errors)



  else:
    print("false") 
   
  return render(request,'search_keyword.html',{'comany_code':company_code})  

def searchfor_modal(request):
  print(request.POST)
  post_item=[]
  id=request.POST.get("id")
  post=Post.objects.filter(id=id).first()
  print(post.tags.all())
  for ts in post.tags.all():
 
    post_item.append(str(ts))
  print(post_item)  

  # for item in post.tags.all:
  #   print(item)
    # post_item.append([item.id,item.file_url,item.file_name,item.tags.all()])
  # print('hhhhhhhhhhh',post_item)  
  
  return JsonResponse({'error': "False",'post':post_item})