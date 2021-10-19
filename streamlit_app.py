import streamlit as st
import time
import requests
from random import random
import os.path
import base64
import datetime

# build country dicts
from country_list import countries
country_dict = {}
region_dict = {} #[{'None':{'None'}]
for c in countries:
    country_dict[c['name']]=c
    if not c['continent'] in region_dict:
        region_dict[c['continent']] = []
    region_dict[c['continent']].append(c)

def remove_html_tags(text):
    """Remove html tags from a string"""
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, ' ', text)

import sys
def execfile(filename, key, globals=None, locals=None):
    import vigenere
    #st.write("...here.."+filename)
    if globals is None:
        globals = sys._getframe(1).f_globals
    if locals is None:
        locals = sys._getframe(1).f_locals
    #st.write("...here 2..")
    if True: #os.path.exists(filename+'.pye'):
        with open(filename+'.pye', "r") as fh:
            # read the encrypted version if it exists
            base64_code = vigenere.translate(fh.read()+"\n",key,1)
            code = base64.b64decode(base64_code.encode('utf-8')).decode('utf-8') 
            #st.write(code)
    else:
        with open(filename+'.py', "r") as fh:
            code = fh.read()+"\n"
            # write the encrypted version if it doesn't exist
            with open(filename+'.pye', "w") as fhw:
                 base64_code = base64.b64encode(code.encode('utf-8')).decode('utf-8')
                 fhw.write(vigenere.translate(base64_code,key,0))
    #st.write('code ```'+code+"```")
    exec(code, globals, locals)

#####################################

def clear_session():
    if 'result' in st.session_state:
        del st.session_state['result']
    st.session_state['update_cache_state']=0

    #st.write('changed')
if 'update_cache_state' not in st.session_state:
    st.session_state['update_cache_state']=0

def update_cache_state():
    if 'update_cache_state' in st.session_state:
        st.session_state['update_cache_state']+=1
    if 'result' in st.session_state:
        del st.session_state['result']

def log_data(context,data=None):
    try:
        with open("logs.txt","r") as fh:
            logstxt = fh.read()
    except:
        logstxt=""
        
    with open("logs.txt","w") as fh:
        fh.write('-----\n\n## %s\n\n'%datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S'))
        fh.write("```\n\n"+context+"\n\n```\n\n")
        if data is not None:
            fh.write('\n\n### Response\n\n')
            fh.write("```\n\n"+data+"\n\n```\n\n")
        fh.write(logstxt)
    with open("audit.txt","a") as fh:
        fh.write('-----\n\n## %s\n\n'%datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S'))
        fh.write("```\n\n"+context+"\n\n```\n\n")
        if data is not None:
            fh.write('\n\n### Response\n\n')
            fh.write("```\n\n"+data+"\n\n```\n\n")


def on_click_bad():
    log_data("Bad")

def on_click_good():
    log_data("Good")

def show_logs():
    with open("logs.txt","r") as fh:
        st.write("# Logs\n\n")
        st.write(fh.read())
        
#####################################
global get_news_feed,generate_ai_response

global conditioning

def main():
    st.set_page_config(  # Alternate names: setup_page, page, layout
        layout="wide",  # Can be "centered" or "wide". In the future also "dashboard", etc.
        initial_sidebar_state="expanded",  # Can be "auto", "expanded", "collapsed"
        page_title="AI Diplomatic Analysis Tool (Adat)",  # String or None. Strings get appended with "• Streamlit".
        page_icon=None,  # String, anything supported by st.image, or None.
    )

    query_params = st.experimental_get_query_params()
    if 'logs' in query_params:
        show_logs()
        return
    
    st.title("AI Tool for Examination of Diplomatic Senarios (AI-TEDS)")
    """This is a Beta Test of tool withich enables analaysis and examination of related diplomatic senarios. It can generate implications on a per country basis, propose (and cost projects) and generate tweets."""

    st.sidebar.text_input("Usage Key",key="usage_key", help="Please enter the TEDS keys. Contact ted@biometix.com if you need one.")
            
    #with st.expander("Options..."):
    length = 512
        #if 'key' not in st.session_state:
            #st.session_state.key=''
        
    if st.session_state.usage_key=='':
        return

    #global conditioning
    try:
        execfile("prompts",st.session_state.usage_key)
        execfile("generate",st.session_state.usage_key)
    except:
        st.error("Invalid key: contact ted@biometix.com for a usage key.")
        return

    temp = st.sidebar.selectbox('creativity',[0.5,0.8,1.0,1.1],2,format_func=lambda val : {0.5:'Low',0.8:'Medium',1.0:'Normal',1.1:'High'}[val],help="This will set how creative you would like the reponses.")
    
    st.info('This is a Beta Service. It has usage limitations which restrict its use to a maxium of 20 queries an hour (accross all users). Please test wisely.')
    #with st.sidebar.expander("Context..") as exp:
        #cols = st.sidebar.columns(2)
    countries = st.sidebar.multiselect("Choose countries", list(country_dict.keys()),['Singapore','Australia'])
    st.sidebar.button('Clear', on_click=clear_session, help='clear the results to regenerate')
    articles={}
    news_urls = []
    
    for country in countries:
        if 'news' in country_dict[country]:
            news_urls.extend(country_dict[country]['news'])
    
    st.sidebar.markdown('# ' + ' '.join([":flag-"+country_dict[country]['code']+': ' for country in countries]).lower())
    
    if len(news_urls)==0:
        news_urls = ['https://www.foreignpolicy.com/feed/','https://www.fpri.org/feed','https://www.medium.com/feed/tag/foreign-policy','https://www.theconversation.com/au/topics/foreign-policy-266/articles.atom','http://feeds.bbci.co.uk/news/world/rss.xml']
    for url in news_urls:
        articles = {**articles, **get_news_feed(url)}
    res=st.selectbox('articles',['None']+sorted(list(articles.keys())),on_change=clear_session)
            
    conditioning_type=st.selectbox('type',list(conditioning.keys()),on_change=clear_session)



    response = None
    expand_topic = 'None'
    article_text = "" if not res or res == 'None' else articles[res]
    inp = st.text_area(
                "Problem domain", article_text, max_chars=2000, height=150, on_change=clear_session
            )
    country_names = ' and '.join([country_dict[country]['name']+': ' for country in countries])

    query_string = f"Question: {inp}. List the top five {conditioning_type} for {country_names}.\n\nAnswer:\n\n1."
    alg_input  = conditioning[conditioning_type] + '\n\n'+ query_string

    warning = """The TEDS A.I. bot produced the following results. The results may be inaccurate, biased or otherwise incomplete. Please excerise appropriate caution before use."""

    done_query = False
    if  'result' not in st.session_state:
        with st.form(key="inputs"):

            submit_button = st.form_submit_button(label="Generate TEDS response")

            if submit_button:
                #st.write(inp)
        
                result="1. "+generate_ai_response(alg_input,length,temp,st.session_state['update_cache_state'])

                # log the data
                result = result.split('===')[0]
                log_data(alg_input.split('===')[-1],result)
                
                st.session_state.peice = []
                for r in result.split('\n')[0:10]:
                    if len(r)>0 and len(r.split('.'))>0:
                        st.session_state.peice.append(r)
                st.session_state.result = result
                #st.session_state.inp = inp
                st.info(warning)
                st.markdown('\n'.join(result.split('\n')[0:10]))
                done_query = True

    


   # st.write(st.session_state.peice)
    st.button('Run Again', on_click=update_cache_state, help='clear the results to regenerate')
        
        #st.write('- '+expand_topic)
    
    if  'result' in st.session_state:
        
        result = st.session_state.result 
        #inp = st.session_state.inp
        if not done_query:
            st.info(warning)
            st.markdown('\n'.join(result.split('\n')[0:10]))

        expand_topic=st.selectbox('Choose an option to recieve more information',['None']+st.session_state.peice)
        
        
        #with st.form(key="inputs2"):
        submit_button2 = st.button(label="Generate Extended TEDS response")
        if submit_button2:
            if expand_topic!='None':
                warning_extended= """Quotes and statistics used below may not be accurate or up to date. This response is a thought provoking opinion rather than fact."""
                st.info(warning_extended)
                expand_topic=expand_topic[3:]
                topics = expand_topic.split(':')
                if len(topics)==1:
                    topic='' 
                    topic_details=topics[0]
                else:
                    topic=topics[0]
                    topic_details=topics[1]
                expand_topic=expand_topic.replace(':','\n\n')
#                '\n\n' + expand_topic+
                query_string = inp + f'\n\n# {topic} \n\nThe following is a short summary of this issue.\n\n{topic_details}:\n\n1.'
                result=generate_ai_response(query_string,300,1.0,random())
                #st.markdown(query_string)
                #st.markdown('----')
                st.markdown(f'## {topic} \n\n{topic_details}:\n\n1. {result}')
        
    if True:
        col1, col2, *rest = st.columns([1, 1, 10, 10])

        col1.button("👍", on_click=on_click_good)
        col2.button("👎", on_click=on_click_bad)

    
    #st.text("App baked with ❤️ by @vicgalle")


if __name__ == "__main__":
    main()
