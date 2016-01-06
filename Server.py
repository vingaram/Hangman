#!/usr/bin/python
from http.server import BaseHTTPRequestHandler,HTTPServer
import urllib.request
import MySQLdb
import urllib
import json
import xml.etree.ElementTree as ET
with urllib.request.urlopen("http://flax.nzdl.org/greenstone3/flax?a=g&sa=FlaxWordQuery&s=FlaxWordList&rt=r&c=password&if=&s1.listType=1000&s1.sortBy=10&o=xml") as url:
    s = url.read()

root=ET.fromstring(s)
tag=root.find('pageResponse')
i=0
data=[]
for x in tag.iter():
    y=x.get('word')
    if(type(y) is not str):
        continue
    i+=1
    data.append(y)
wordList={}
wordList['word']=data;
wordList['count']=len(data);
wordList['type']=1;
wordList['scores']=[];
output1={}
output2={}
output1['output']='SUCCESS';
output2['output']='FAILURE';
SCORE_COUNT=10

PORT_NUMBER = 8080

# To handle requests 
class myHandler(BaseHTTPRequestHandler):



    def do_POST(self):
        print('POST')
        length = int(self.headers['Content-Length'])
        post_data=json.loads(self.rfile.read(length).decode('utf-8'))
        print(post_data['score'])
        user=post_data['user']
        with open('highscores.txt','r') as file:
            lines=json.load(file)
            count=0;
            curr_score=(int(post_data['score']))
            entered=False;
            scorelist=[]
            for line in lines:
                count=count+1
                if(count<=SCORE_COUNT):
                    if(int(post_data['score'])<=line[0] or entered):
                        scorelist.append(line)
                    else:
                        temp=[]
                        temp.append(int(post_data['score']))
                        temp.append((post_data['user']))
                        scorelist.append(temp)
                        count=count+1
                        entered=True
                        if(count<=SCORE_COUNT):
                            scorelist.append(line)
            if(count < SCORE_COUNT and not (entered)):
                temp=[]
                temp.append(int(post_data['score']))
                temp.append((post_data['user']))
                scorelist.append(temp)        
        with open('highscores.txt','w') as file:
            json.dump(scorelist,file)
        scorelist=[]
        output={}
        with open(user+'.json','a+') as file:
            file.seek(0)
            entered=False;
            count=0;
            result_list=[]
            user_data=json.load(file)
            for x in user_data['scores']:
                count=count+1
                if(count<=SCORE_COUNT):
                    if(curr_score<=x or entered):
                        scorelist.append(x)
                    else:
                        scorelist.append(curr_score)
                        count=count+1
                        entered=True
                        if(count<=SCORE_COUNT):
                            scorelist.append(x)
            if(count < SCORE_COUNT and not (entered)):
                scorelist.append(curr_score)
            print(scorelist)
            result_list=list(set(user_data['word']).difference(set(post_data['words'])))
            output['scores']=scorelist
            output['word']=result_list
            output['count']=-1*(len(post_data['words'])-int(user_data['count']))
            output['type']=user_data['type']
        with open(user+'.json','w') as file:
            json.dump(output,file)
        self.send_response(200)
        self.wfile.write(bytes("SUCCESSFULL",'utf-8'))  
    def do_GET(self):
        print   ('Get request received')
        print(self.path)
        if('login' in self.path):
            temp=self.path[2:]
            userSet=temp.split('&')
            user=userSet[0].split('=')[1]
            pwd=userSet[1].split('=')[1]
            
            self.send_response(200)
            print(user)
            flag=False
            print('LOGIN PAGE')
            db = MySQLdb.connect(host="localhost",
                     user="vinga",
                     passwd="vingaram",
                     db="vingadb")
            cur = db.cursor()
            select_stmt = "SELECT * FROM Login WHERE user = %(user)s AND pwd = %(pwd)s"
            cursor.execute(select_stmt, { 'user': user ,'pwd': pwd })
            if cur.rowcount>0:
                with open('main.html') as file:
                            string=file.read()
                            self.wfile.write(bytes(string,'utf-8'))
                        flag=True
                        break;
            if(not flag):
                self.wfile.write(bytes("FAILURE",'utf-8'))
            db.close()
            
        elif('from_signup' in self.path):
            temp=self.path[2:]
            userSet=temp.split('&')
            user={}
            key=userSet[0].split('=')[1]
            user[key]=userSet[1].split('=')[1]
            print(user)
            print('SIGNUP PAGE')
            db = MySQLdb.connect(host="localhost",
                     user="vinga",
                     passwd="vingaram",
                     db="vingadb")
            cur = db.cursor()
            queryData=(key,user[key])
            cur.execute("INSERT INTO Login VALUES(%s,%s)",queryData)
            db.close()
            self.wfile.write(bytes("SUCCESS",'utf-8'))

        elif('signup' in self.path):
            string=""
            with open('registration.html') as file:
                string=file.read()
            self.wfile.write(bytes(string,'utf-8'))
        elif('main' in self.path):
            string=""
            with open('main.html') as file:
                string=file.read()
            self.wfile.write(bytes(string,'utf-8'))
        elif('high' in self.path):
            print('HIGH SCORES PAGE')
            user=self.path.split("user=")[1]
            scores={}
            with open('highscores.txt','r') as file:
                scores['overall']=json.load(file)
            with open(user+'.json','r') as file:
                scores['user']=json.load(file)['scores']
            self.wfile.write(bytes(json.dumps(scores),'utf-8'))
        elif('hs' in self.path):
            string=""
            print("HS")
            with open('HIGHSCORES.html') as file:
                string=file.read()
                self.wfile.write(bytes(string,'utf-8'))            
        elif('favicon' in self.path):
                print('fav');
        elif('update' in self.path):
            print('UPDATE')
            print(self.path)
            user=self.path.split("user=")[1]
            print(user)
            with open(user+".json",'a+') as file:
                file.seek(0);

                user_json_data=json.load(file);
                
                if(user_json_data["count"]<100 and user_json_data['type']<5):
                    with urllib.request.urlopen("http://flax.nzdl.org/greenstone3/flax?a=g&sa=FlaxWordQuery&s=FlaxWordList&rt=r&c=password&if=&s1.listType="+str((user_json_data['type']+1)*1000)+"&s1.sortBy=10&o=xml") as url:
                        s = url.read()
    
                    root=ET.fromstring(s)
                    tag=root.find('pageResponse')
                    i=0
                    data=[]
                    for x in tag.iter():
                        y=x.get('word')
                        if(type(y) is not str):
                            continue
                        i+=1
                        data.append(y)
                    wl={}
                    wl['word']=data;
                    wl['count']=len(data);
                    wl['scores']=[0];
                    user_json_data['count']+=wl['count'];
                    user_json_data['word']+=wl['word']
                    user_json_data['type']+=1
                    with open(user+'.json','w') as outfile:
                        json.dump(user_json_data, outfile)
                self.wfile.write(bytes(json.dumps(user_json_data),'utf-8'))    
        elif('from_play' in self.path):
            data=""
            user=""
            for x in self.path.split('&'):
                if('score' in x):
                    print(x.split('=')[1])
                    data=(x.split('=')[1])
                    print(data)
                elif('user' in x):
                    user=x.split('=')[1]
                    print(user)
            with open(user+'.json','a+') as file:
                file.seek(0)
                file_data=json.load(file)
                print((data)-file_data['score'][0])
        elif('play' in self.path):
            string=""
            with open('HANGMAN.html') as file:
                string=file.read()
                self.wfile.write(bytes(string,'utf-8'))
        elif('instructions' in self.path):
            string=""
            with open('INSTRUCTIONS.html') as file:
                string=file.read()
                self.wfile.write(bytes(string,'utf-8'))
        else:
            string=""
            with open('login.html') as file:
                string=file.read()
                self.wfile.write(bytes(string,'utf-8'))
        return

try:
    # Create web server and define the handler to manage request
    server = HTTPServer(('127.0.0.1', PORT_NUMBER), myHandler)
    print ('Started httpserver on port ' , PORT_NUMBER)
    server.serve_forever()

except KeyboardInterrupt:
    print ('^C received, shutting down the web server')
    server.socket.close()
