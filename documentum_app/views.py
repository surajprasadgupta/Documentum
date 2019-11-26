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
from django.conf import settings
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
import comtypes.client
from comtypes.client import CreateObject
import win32com.client
import time
import pythoncom
from django.contrib.auth.decorators import login_required

# Create your views here.
def index(request):

    return render(request,'index1.html')

    
def login(request):

  return render(request,'index.html')
@login_required
def dashboard(request):
  
  if request.method=='POST':
    company_code=request.POST.get('company_code')
    request.session['company_code']=company_code
    company=Company.objects.filter(company_code=company_code).first()

    return render(request,'dashboard.html',{'company':company})


  else:
    company_code=request.session['company_code']
    company=Company.objects.filter(company_code=company_code).first()
    users=Post.objects.filter(company_code=company_code)

    return render(request,'dashboard.html',{'company':company})


@login_required 
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
          return HttpResponseRedirect(reverse('documentum_app:login'))  
      else:
        messages.success(request, 'Password does not match .')  
        return HttpResponseRedirect(reverse('documentum_app:login'))  

    else:
      print("elseeeeeeeeeeee")
      return HttpResponseRedirect(reverse('documentum_app:login'))

def account_login(request):


  username=request.POST.get('username')
  password=request.POST.get('password')
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

def getrootpath(file_url):
  head, tail = os.path.split(settings.MEDIA_ROOT)
  final = os.path.join(head +str(file_url))
  file_path=final.replace(os.sep, '/')
  return file_path
   

@login_required
def account_logout(request):

  # for sesskey in request.session.keys():
  #   del request.session[sesskey]
  logout(request)
  # logout(request)
  return render(request,'index.html')     

  # *******************************************************ocr*******************************************************************      

def pdftotext(img_url):
  
  img_type=img_url.split(".")[1]
  APP_ROOT = os.path.abspath(documentum_app.__path__[0])
  file_path=getrootpath(img_url)
  print('ddddddddddddddddddrrrrrrrrrrrrrrr',file_path)
  # file_path = os.path.join('C:/Users/ASUS/Desktop/project/documentum/'+str(img_url))
  stop_words = get_stop_words('english')

  if img_type=="pdf":    
    pdf_file = open(file_path, 'rb')
    read_pdf = PyPDF2.PdfFileReader(pdf_file)
    number_of_pages = read_pdf.getNumPages()
    page_content=""
    for i in range(number_of_pages):
      page = read_pdf.getPage(i)
      content = page.extractText()
      page_content+=content
    text=page_content
    text_list=page_content.split(" ")
    text_word= [word for word in text_list if word not in stop_words] 
    text_remove_rep=list(set(text_word))

    return text


  elif img_type=="jpg" or img_type=="jpeg" or img_type=="png":
    img = cv2.imread(file_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    tesseract_output = pytesseract.image_to_string(Image.fromarray(img),lang="eng")
    text=tesseract_output

    return text

  elif img_type=="doc" or img_type=="docx":
    fullText=[]
    document = Document(file_path)

    for para in document.paragraphs:
        fullText.append(para.text)
    return '\n'.join(fullText)



  elif img_type=="txt":
    text_file=open(file_path,'r')
    text=text_file.read()
    return text


  elif img_type=="csv":
    text=[]
    string_list=[]
    string_seq=""
    with open(file_path,'rt')as f:
      data = csv.reader(f)
      for row in data:
        text.append(row)
    
    for text_list in text:
      string_list=string_list + text_list
    for string in string_list:
      string_seq+=string

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

    all_dict=[]
    for d in dict_list:
      for k, v in d.items():
        all_dict.append(k)
        all_dict.append(v)

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
 
  # file_path = os.path.join('/home/finsq/Desktop/documentum/documentum'+str(img_url))
  file_path=getrootpath(img_url)
  img = cv2.imread(file_path)
  img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  tesseract_output = pytesseract.image_to_string(Image.fromarray(img),lang="eng")
  return 
                
def get_human_names(text):

   #read all lines
  sentences = nltk.sent_tokenize(text) #tokenize sentences
  nouns = [] #empty to array to hold all nouns

  for sentence in sentences:
       for word,pos in nltk.pos_tag(nltk.word_tokenize(str(sentence))):
           if (pos == 'NN' or pos == 'NNP' or pos == 'NNS' or pos == 'NNPS' ):
               nouns.append(word)            
  return nouns

def get_address(text):
  address=None
  try:
    pattern = re.compile(r'/\s+(\d{2,5}\s+)(?![a|p]m\b)(([a-zA-Z|\s+]{1,5}){1,2})?([\s|\,|.]+)?(([a-zA-Z|\s+]{1,30}){1,4})(court|ct|street|st|drive|dr|lane|ln|road|rd|blvd|collony)([\s|\,|.|\;]+)?(([a-zA-Z|\s+]{1,30}){1,2})([\s|\,|.]+)?\b(AK|AL|AR|AZ|CA|CO|CT|DC|DE|FL|GA|GU|HI|IA|ID|IL|IN|KS|KY|LA|MA|MD|ME|MI|MN|MO|MS|MT|NC|ND|NE|NH|NJ|NM|NV|NY|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VA|VI|VT|WA|WI|WV|WY)([\s|\,|.]+)?(\s+\d{5})?([\s|\,|.]+)/i')
    matches = pattern.findall(text) # Gets all email addresses as a list
    address = matches
  except Exception as e:
      print (e)

  return address





            



@login_required
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
                file_type=data.file_upload.url.split(".")[-1]
                if file_type=='doc'or file_type=='docx':
                  import win32com.client
                  import time
                  import pythoncom
                  pythoncom.CoInitialize()
                  
                  in_file=getrootpath(data.file_upload.url)
              
                  # in_file = os.path.join('C:/Users/ASUS/Desktop/project/documentum/'+str(data.file_upload.url))
                  
                  word = win32com.client.Dispatch("Word.Application")
                  time.sleep(3)
                  new_name = in_file.replace(".docx", r".pdf")
                  worddoc = word.Documents.Open(in_file)

                  worddoc.SaveAs(new_name, FileFormat = 17)
                
                  print("xxxxxxx",new_name)
                  file_urls.append(new_name.split("documentum")[-1])
                  print("xxxxxxx",new_name)
                  # worddoc.Close()
                  # word.Quit()
                elif file_type=='xlsx' or file_type=='xls':
                  import win32com.client
                  import time
                  import pythoncom
                  pythoncom.CoInitialize()
                 
                  in_file=getrootpath(data.file_upload.url)
                  # in_file = os.path.join('C:/Users/ASUS/Desktop/project/documentum/'+str(data.file_upload.url))
                
                  from win32com import client

                  xlApp = client.Dispatch("Excel.Application")
                  if file_type=='xlsx':
                    new_name = in_file.replace(".xlsx", r".xlsx.pdf")
                  else:
                    new_name = in_file.replace(".xls", r".xls.pdf")

                  
                  
                  books = xlApp.Workbooks.Open(in_file)
                  
                  # books.SaveAs(new_name, FileFormat = 51)
                  ws = books.Worksheets[0]
                  
                  ws.Visible = 1
                  ws.ExportAsFixedFormat(0, in_file)
                  
                  # ws.SaveAs(new_name, FileFormat=57)
                  # print('ggggggggggggggggggggggg',new_name )
                  file_urls.append(new_name.split("documentum")[-1])

                elif file_type=="csv":
                  print('::::::::::',data.file_upload)
                  from win32com import client
                  in_file=getrootpath(data.file_upload.url)
                  # in_file = os.path.join('C:\\Users\\ASUS\\Desktop\\project\\documentum\\'+str(data.file_upload.url))
                  csvApp = client.Dispatch("Excel.Application")
                  new_name=in_file.replace(".csv" , r".csv.pdf")
                  books=csvApp.workbooks.open(in_file)
                  ws = books.Worksheets[0]
                  ws.Visible = 1
                  ws.ExportAsFixedFormat(0, in_file)
                  file_urls.append(new_name.split("documentum")[-1])

                else:
                  print("fail buddy")
                  file_urls.append(data.file_upload.url)
                  

            
                # file_urls.append(data.file_upload.url)
                path=data.file_upload.url
                doc_list=pdftotext(path)
                print("#####",doc_list)
                tags=get_human_names(doc_list)
                # tags="suraj"
                # print(tags)
                text_list=text.append(doc_list)
                tag_list.append(tags)
              items=list(zip(file_urls,text,tag_list))
              item_list=[]
              for item in items:
                item_list.append(list(item))
            
              

              # ______________________________pagination_______________________________

              paginator = Paginator(item_list, 1) # Show 1 contacts per page
              page = request.GET.get('page')
              item_list = paginator.get_page(page)


              # ______________________________pagination_______________________________


              
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
          file_type=data.file_upload.url.split(".")[-1]
          if file_type=='doc'or file_type=='docx':

            # print("hello")
            import win32com.client
            import time
            import pythoncom
            pythoncom.CoInitialize()
            print('sssssssssssssssssss',data.file_upload)
            in_file=getrootpath(data.file_upload.url)
            # in_file = os.path.join('C:/Users/ASUS/Desktop/project/documentum/'+str(data.file_upload.url))
            
            out_file = in_file
            word = win32com.client.Dispatch("Word.Application")
            time.sleep(3)
            new_name = in_file.replace(".docx", r".pdf")
            worddoc = word.Documents.Open(in_file)

            worddoc.SaveAs(new_name, FileFormat = 17)
            print(new_name )
            file_urls.append(new_name.split("documentum")[-1])
           
          elif file_type=='xlsx' or file_type=='xls':
            import win32com.client
            import time
            import pythoncom
            pythoncom.CoInitialize()
            
            in_file=getrootpath(data.file_upload.url)
            # in_file = os.path.join('C:/Users/ASUS/Desktop/project/documentum/'+str(data.file_upload.url))
           
            print(in_file)
            from win32com import client

            xlApp = client.Dispatch("Excel.Application")
            if file_type=='xlsx':
              new_name = in_file.replace(".xlsx", r".xlsx.pdf")
            else:
              new_name = in_file.replace(".xls", r".xls.pdf")

            
            
            books = xlApp.Workbooks.Open(in_file)
            
            # books.SaveAs(new_name, FileFormat = 51)
            ws = books.Worksheets[0]
            
            ws.Visible = 1
            ws.ExportAsFixedFormat(0, in_file)
            
            # ws.SaveAs(new_name, FileFormat=57)
            # print('ggggggggggggggggggggggg',new_name )
            file_urls.append(new_name.split("documentum")[-1])

          elif file_type=="csv":
            from win32com import client
            print('ssssssssssssssss',data.file_upload)
            in_file=getrootpath(data.file_upload.url)
            # in_file = os.path.join('C:\\Users\\ASUS\\Desktop\\project\\documentum\\'+str(data.file_upload.url))
            csvApp = client.Dispatch("Excel.Application")
            new_name=in_file.replace(".csv" , r".csv.pdf")
            books=csvApp.workbooks.open(in_file)
            ws = books.Worksheets[0]
            print("4")
            ws.Visible = 1
            ws.ExportAsFixedFormat(0, in_file)
            file_urls.append(new_name.split("documentum")[-1])

          else:
            print("fail buddy")
            file_urls.append(data.file_upload.url)
                  
          # file_urls.append(data.file_upload.url)
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
@login_required
def search_keyword(request):
  print(request.POST)
  tags=request.POST.get('tags')

  startdate=request.POST.get('startdate')
  enddate=request.POST.get('enddate')
  emp_name=request.POST.get('emp_name')
  file_name=request.POST.get('file_name')
  company_code=request.session['company_code']

  
  if request.method=='POST' and tags!= '' and tags!=None:
    print("1")
    search_keyword=request.POST.get('tags')
    search_list=search_keyword.split(',')
    
    
    # q_object=""
    q_object = Q(content__icontains=search_list[0]) & Q(content__icontains=search_list[0])
    
    for item in search_list:
        q_object.add((Q(content__icontains=item) & Q(content__icontains=item)), q_object.connector)
    pub_list=Post.objects.filter(q_object,).filter(company_code=company_code,is_private=False)
    posts = Post.objects.filter(q_object ).filter(company_code=company_code,user=emp_name).order_by('-id').union(pub_list)
    # for post in posts:
    #   print(post.file_url)
    return render(request,'search_keyword.html',{'posts':posts})  
  elif request.method=='POST'and startdate!=None and startdate!='':
    print("2")
    pub_list=Post.objects.filter(company_code=company_code,created_on__range=(startdate,enddate),is_private=False)
    posts = Post.objects.filter(company_code=company_code,created_on__range=(startdate,enddate),user=emp_name).order_by('-id').union(pub_list) 
    return render(request,'search_keyword.html',{'posts':posts}) 
  elif request.method=='POST'and emp_name!=None:
    print("3")
    pub_list=Post.objects.filter(company_code=company_code,is_private=False)
    print('xxxx',pub_list)
    doc_list=Post.objects.filter(company_code=company_code,user=emp_name).order_by('-id').union(pub_list)
    return render(request,'search_keyword.html',{'posts':doc_list})
  elif request.method=='POST' and file_name!=None:
    print("4")
    pub_list=Post.objects.filter(company_code=company_code,file_name__icontains=file_name,is_private=False)
    doc_list=Post.objects.filter(company_code=company_code,file_name__icontains=file_name,user=emp_name).order_by('-id').union(pub_list)
    return render(request,'search_keyword.html',{'posts':doc_list})   
  else:
    print("5")
    return render(request,'search_keyword.html')

# **********************************extract user from post*******************************
@login_required
def searchby_name(request):
  company_code=request.session['company_code']
  users_temp = Post.objects.filter(company_code=company_code).values_list('user', flat=True).distinct()
  users = []
  for user_id in users_temp:
    user=User.objects.filter(id=user_id)
    for v in user:
      # user=v
      print(v)   
    users.append([v.id, v.username])
  return JsonResponse({'error': "False",'users':users})

#     **********************SAVE POST*******************************
@login_required
def create_contant(request):
  # print(request.POST)
  if request.method=='POST':
    file_name=request.POST.get('file_name').split("/")[-1]
    file_url=request.POST.get('uploaded_file')
    user_id=request.POST.get('user')
   
    company_code=request.POST.get('company_code')
    request.session["company_code"] = company_code
    form=PostContantForm(request.POST)
    if form.is_valid():
      form_contant = form.save(commit = False)
      form_contant.company_code=Company.objects.filter(company_code=company_code).first()
      form_contant.user=User.objects.filter(id=user_id).first()
      form_contant.file_url=file_url
      form_contant.content=request.POST.get('content')
      form_contant.file_name=file_name
      form_contant.is_private=request.POST.get('is_private')     
      form_contant.save()
      if request.POST.get('tags', ''):
        tags = request.POST.get("tags")
        # tag=[Tags.objects.get_or_create(name=tag)[0] for tag in tags.split(',')]
        splitted_tags = tags.split(",")
        for t in splitted_tags:
            tag = Tags.objects.filter(name=t)
            if tag:
                tag = tag[0]
            else:
                tag = Tags.objects.create(name=t)
                form_contant.tags.add(tag)
      return HttpResponseRedirect(reverse('documentum_app:file_upload')) 
    else:
  
      print(form.errors)



  else:
    print("false") 
   
  return render(request,'search_keyword.html',{'comany_code':company_code})  
@login_required
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