import requests
from .models import *

def test():
    test = requests.get('https://unhindled.herokuapp.com/service/allposts/', auth=('connectionsuperuser','404connection'), headers={'Referer': "http://127.0.0.1:8000/"})
    # test = requests.get('http://127.0.0.1:8000/service/allposts', auth=('q','q'), headers={'Referer': "http://127.0.0.1:8000/"})
    t = test.json()
    return t

def get_json_post(id):
    found_post = ''
    for post in get_foreign_posts_list():
        try:
            split = post['id'].split('/')[-1]
        except:
            split = ''
        if split == id:
            found_post = post

    return found_post
    
#get foreign posts
def get_foreign_posts_list():
    post_list=[]

    # foreign posts from team 3
    t3_req = requests.get('https://social-dis.herokuapp.com/posts?size=1000', auth=('socialdistribution_t03','c404t03'), headers={'Referer': "http://127.0.0.1:8000/%22%7D"})
    if t3_req.status_code == 500:
        pass
    else:
        js_req_3 = t3_req.json()['items']
        for post in js_req_3:
            post_list.append(post)


    #foreign posts from team 5
    t5_req = requests.get('https://cmput404-socialdist-project.herokuapp.com/post/request_post_list?size=1000', auth=('socialdistribution_t05','c404t05'), headers={'Referer': "http://127.0.0.1:8000/%22%7D"})
    if t5_req.status_code == 500:
        pass
    else:
        js_req_5 = t5_req.json()
        for post in js_req_5:
            post_list.append(post)

    #foreign posts from team 14
    t14_req = requests.get('https://linkedspace-staging.herokuapp.com/api/posts?size=1000', auth=('socialdistribution_t14','c404t14'), headers={'Referer': "http://127.0.0.1:8000/%22%7D"})
    if t14_req.status_code == 500:
        pass
    else:
        js_req_14 = t14_req.json()
        for post in js_req_14:
            post_list.append(post)

    return post_list

#get foreign authors
def get_foreign_authors_list():
    # foreign authors from team 3
    author_list=[]
    t3_req = requests.get('https://social-dis.herokuapp.com/authors', auth=('socialdistribution_t03','c404t03'), headers={'Referer': "http://127.0.0.1:8000/"})
    if t3_req.status_code == 500:
        pass
    else:
        js_req_3 = t3_req.json()['items']
        author_list.append(js_req_3)
    
    # foreign authors from team 5
    t5_req = requests.get('https://cmput404-socialdist-project.herokuapp.com/authors/', auth=('socialcircleauth','cmput404'), headers={'Referer': "http://127.0.0.1:8000/"})
    if t5_req.status_code == 500:
        pass
    else:
        js_req_5 = t5_req.json()['items']
        author_list.append(js_req_5)
    
    #foreign posts from team 14
    t14_req = requests.get('https://linkedspace-staging.herokuapp.com/api/authors', auth=('socialdistribution_t14','c404t14'), headers={'Referer': "http://127.0.0.1:8000/"})
    if t14_req.status_code == 500:
        pass
    else:
        js_req_14 = t14_req.json()['items']
        author_list.append(js_req_14)

    return author_list

