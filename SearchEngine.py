
# coding: utf-8

# In[2]:

#!/usr/bin/env python

from flask import Flask, request, render_template, jsonify, json
from SolrClient import SolrClient
from spell import correction
import codecs
from bs4 import BeautifulSoup
#from flask.ext.sqlalchemy import SQLAlchemy


# In[3]:


app = Flask(__name__)
#db = SQLAlchemy(app,use_native_unicode="utf8")
 
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:cacti@localhost/web12306'
 
 
 
 
# class session(db.Model):
#   __tablename__ = 'web12306'
#   user_id = db.Column(db.String(100), primary_key = True)
#   user_email = db.Column(db.String(100))
#   user_pass = db.Column(db.String(100))
#   user_nic = db.Column(db.String(100))
#   user_phone = db.Column(db.String(100))
#   user_name = db.Column(db.String(100))
 
@app.route('/suggest', methods=['GET'])
def suggest():
    query_key = request.args.get('query')
    solr = SolrClient('http://localhost:8983/solr')
    res = solr.query('myexample',{
            'q':query_key,
        },'suggest')
    return json.dumps(res.data['suggest']['suggest'][query_key]['suggestions'])

 
 
 
@app.route('/scan', methods=['GET'])
def scan():
    # Get search result
    #print(parameters)
    # query_key, page_rank = parameters.split('&')
    # query_key = query_key.split('=')[1]
    # page_rank = page_rank.split('=')[1]
    query_key = request.args.get('query')
    page_rank = request.args.get('pagerank')
    # print(query_key)
    # print(page_rank)
    solr = SolrClient('http://localhost:8983/solr')
    if page_rank == '1':
        #print('exe1')
        res = solr.query('myexample',{
            'q':query_key,
            'sort':'pageRankFile desc',
        })
    else:
        #print('exe0')
        res = solr.query('myexample',{
            'q':query_key,
            })
    if res is None:
        json_result = {'query':None}
        return json.dumps(json_result, ensure_ascii=False)
    else:
        #print(res)
        for value in res.docs:
            #print(value['id'])

            # Add snippets
            snippet = get_snippet(value['id'], query_key)
            value['snippet'] = snippet

            if 'description' not in value:
                value['description']='NULL'
            if 'og_url' not in value:
                with open('./mapNBCNewsDataFile.csv') as f:
                    key = value['id'].split('/')[-1]
                    for line in f:
                        if line.split(',')[0] == key:
                            value['og_url'] = (line.split(',')[-1])
                            break

        # Use Norvig's result to replace the Solr suggestion
        # correct_res = res.data['spellcheck']
        # if correct_res.get('suggestions'):
        #     correct_word = correction(query_key)
        #     res.data['spellcheck']['suggestions'][1]['suggestion'][0]=correct_word
        correct_res = res.data['spellcheck']
        correct_word_list=[]
        if correct_res.get('suggestions'):
            query_key_list = query_key.split()
            
            for i in query_key_list:
                # correct_word = correction(query_key)
                correct_word_list.append(correction(i))
            res.data['spellcheck']['collations'][1]=' '.join(correct_word_list)


        return json.dumps(res.data, ensure_ascii=False,indent=4)
    
#      result = session.query.filter_by(user_id=user_id).first()
#      if result is None:
#             json_result={'user_id':None}
#             return json.dumps(json_result,ensure_ascii=False)
#      else:
#             json_result = {'user_id': result.user_id, 'user_email': result.user_email, 'user_pass': result.user_pass, 'user_nic': result.user_nic, 'user_phone': result.user_phone, 'user_name': result.user_name}
#             print json_result
#             return json.dumps(json_result,ensure_ascii=False)
        
def get_snippet(filename, query_key):
    f = codecs.open(filename,'r','windows-1255')
    soup = BeautifulSoup(f.read())
    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()    # rip it out

    # get text
    text = soup.get_text()

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)

    #print(text.split('\n'))
    for x in text.split('\n'):
        if x.lower().find(query_key.lower())!=-1:
            return x
    return None
                
             
@app.route('/')
def index():
    return render_template('./index.html')
 
 
 
if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 51245, debug=True)


# In[ ]:



