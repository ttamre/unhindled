from datetime import datetime
import json
from logging import raiseExceptions
import uuid
from django.contrib import auth
from .models import User
from .serializers import UserSerializer
import requests
import logging

from unhindled.serializers import UserSerializer


servers = [
        ('social-dis.herokuapp.com', ('socialdistribution_t03','c404t03')),
        ('cmput404-socialdist-project.herokuapp.com', ('socialcircleauth','cmput404')),
        ('linkedspace-staging.herokuapp.com/api', ('socialdistribution_t14','c404t14'))
    ]

def test():
    test = requests.get('https://unhindled.herokuapp.com/service/allposts/', auth=('connectionsuperuser','404connection'), headers={'Referer': "http://127.0.0.1:8000/"})
    # test = requests.get('http://127.0.0.1:8000/service/allposts', auth=('q','q'), headers={'Referer': "http://127.0.0.1:8000/"})
    if test.status_code == 500:
        pass
    else:
        t = test.json()
    return t

def get_json_post(id):
    found_post = ''
    for post in get_foreign_posts_list():
        try:
            split = post['id'].split('/')[-1]
            if split == '':
                split = post['id'].split('/')[-2]
        except:
            split = ''
        if split == id:
            found_post = post

    return found_post
    
#get our own authors
def test_authors():
    test = requests.get('https://unhindled.herokuapp.com/service/authors/', auth=('connectionsuperuser','404connection'), headers={'Referer': "http://127.0.0.1:8000/"})
    if test.status_code == 500:
        pass
    else:
        t = test.json()
    return t  

def get_json_authors(id):
    found_authors = ''
    for authors in get_foreign_authors_list():
        try:
            split = authors['id'].split('/')[-1]
            if split == '':
                split = authors['id'].split('/')[-2]
        except:
            split = ''
        if split == id:
            found_authors = authors
    return found_authors
    


    
#get foreign posts
def get_foreign_posts_list():
    post_list=[]

    # foreign posts from team 3
    t3_req = requests.get('https://social-dis.herokuapp.com/posts?size=10000', auth=('socialdistribution_t03','c404t03'), headers={'Referer': "http://127.0.0.1:8000/"})
    if t3_req.status_code == 500:
        pass
    else:
        js_req_3 = t3_req.json()['items']
        for post in js_req_3:
            post_list.append(post)

       
    # #foreign posts from team 5
    # t5_req = requests.get('https://cmput404-socialdist-project.herokuapp.com/post/request_post_list?size=10000', auth=('socialcircleauth','cmput404'), headers={'Referer': "http://127.0.0.1:8000/"})

    # if t5_req.status_code == 500:
    #     pass
    # else:
    #     js_req_5 = t5_req.json()
    #     for post in js_req_5:
    #         post_list.append(post)

    #foreign posts from team 14
    t14_req = requests.get('https://linkedspace-staging.herokuapp.com/api/posts?size=10000', auth=('socialdistribution_t14','c404t14'), headers={'Referer': "http://127.0.0.1:8000/"})

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
        for author in js_req_3:
            author_list.append(author)

    # foreign authors from team 5
    t5_req = requests.get('https://cmput404-socialdist-project.herokuapp.com/authors/', auth=('socialcircleauth','cmput404'), headers={'Referer': "http://127.0.0.1:8000/"})
    if t5_req.status_code == 500:
        pass
    else:
        js_req_5 = t5_req.json()
        for author in js_req_5:
            author_list.append(author)
    
    #foreign authors from team 14
    t14_req = requests.get('https://linkedspace-staging.herokuapp.com/api/authors', auth=('socialdistribution_t14','c404t14'), headers={'Referer': "http://127.0.0.1:8000/"})
    if t14_req.status_code == 500:
        pass
    else:
        js_req_14 = t14_req.json()['items']
        for author in js_req_14:
            author_list.append(author)
            
    #foreign authors from our own heroku for testing 
    #t15_req = requests.get('https://unhindled.herokuapp.com/service/authors', auth=('connectionsuperuser','404connection'), headers={'Referer': "http://127.0.0.1:8000/"})
    #if t15_req.status_code == 500:
        #pass
    #else:
        #js_req_15 = t15_req.json()['items']
        #for author in js_req_15:
            #author_list.append(author)
    return author_list
 
#get author given author.id NOT CURRENTLY IN USE  
def foreign_get_author(author):
    #team 3 once implemented
    if "social-dis.herokuapp.com" in author:
        url = author
        t3_req = requests.get(url, auth=('socialdistribution_t03','c404t03'), headers={'Referer': "http://127.0.0.1:8000/"})
        if t3_req.status_code == 500:
            return ""
        else:
            return t3_req.json()
    #our own heroku for local testing
    if "unhindled.herokuapp.com" in author:
        url = author
        t15_req = requests.put(url, auth=('connectionsuperuser','404connection'), headers={'Referer': "http://127.0.0.1:8000/"})
        if t15_req.status_code == 500:
            return ""
        else:
            return t15_req.json()

#sends put request to add one of our authors as a follower NOT CURRENTLY IN USE
def foreign_add_follower(author, follower):
    logger = logging.getLogger("log")
    logger.error(author)
    logger.error(follower)
    #team 3 once implemented
    if "social-dis.herokuapp.com" in author:
        url = author +'/followers/'+ follower
        logger.error(url)
        t3_req = requests.put(url, auth=('socialdistribution_t03','c404t03'), headers={'Referer': "http://127.0.0.1:8000/"})
        if t3_req.status_code == 500:
            return ""
        else:
            return t3_req.json()
    if "cmput404-socialdist-project.herokuapp.com" in author:
        url = author +'/followers/'+ follower
        t3_req = requests.put(url, auth=('socialdistribution_t03','c404t03'), headers={'Referer': "http://127.0.0.1:8000/"})
        if t3_req.status_code == 500:
            return ""
        else:
            return t3_req.json()
    #our own heroku for local testing
    #if "unhindled.herokuapp.com" in author:
        #url = author +'/followers/'+ follower
        #t15_req = requests.put(url, auth=('connectionsuperuser','404connection'), headers={'Referer': "http://127.0.0.1:8000/"})
        #if t15_req.status_code == 500:
           # return ""
       # else:
           # return t15_req.json()

#get foreign comments
def get_foreign_comments_list(source, author, post):
    for server in servers:
        if server[0][:-4] in source:
            auth = server[1]
            endpoint = "https://" + server[0] + "/author/" + author + "/posts/"+ post +"/comments"
            req = requests.get(endpoint, auth=auth, headers={'Referer': "http://127.0.0.1:8000/"})
            if req.status_code == 200:
                return req.json()['comments']
            else:
                return []
    return []

        

def post_foreign_comments(request, comm, postJson):
    #print(request.user.id)
    author = User.objects.get(id=request.user.id)
    author = UserSerializer(author).data
    # author['id'] = "https://unhindled.herokuapp.com/author/35fc41c5-7f34-4d5b-aae4-5310b23d2b02"
    # author['url'] = "https://unhindled.herokuapp.com/author/35fc41c5-7f34-4d5b-aae4-5310b23d2b02"
    #print('comm:\n\n', comm)
    #print(postJson['id'])
    print('team 14\n\n\n')
    #post comment on team 14
    if "linkedspace-staging.herokuapp.com" in postJson['id']:
        
        payload = {'Post_pk': postJson['comments'].replace('/comments', '').replace("/author/", "/api/author/"), 
                    'auth_pk': str(request.user.pk), 
                    'contentType': 'text/plain',
                    'text': comm
                    }
        print(payload)
        api_url = postJson["comments"].replace("/author/", "/api/author/")
        t14_req = requests.post(api_url, auth=('socialdistribution_t14','c404t14'), headers={'Referer': "http://127.0.0.1:8000/"}, json=payload)
        print(api_url)
        if t14_req.status_code == 200:
            pass    
        else: 
            return t14_req.json()

    #post comment on team 3
    if "social-dis.herokuapp.com" in postJson['id']:
        print('team 3\n\n\n')
       
        payload = { "type": "comments",
                    "author": json.dumps(author),
                    "comment": comm,
                    "contentType": "text/plain",
                    "published": str(datetime.now()),
                    "id": postJson['id'].split('/')[-1]
                }
        print(payload)
        print(postJson['id']+"/comments")
        t3_req = requests.post(postJson['id']+"/comments", auth=('socialdistribution_t03','c404t03'), headers={'Referer': "http://127.0.0.1:8000/"}, json=payload)
        
        if t3_req.status_code == 200:
            pass
        else:
            print(t3_req.json())
            return t3_req.json()

    #post comment on team 5
    # if "cmput404-socialdist-project.herokuapp.com" in postJson['id']:
    #     print('team 5\n\n\n')
    #     raise Exception
    #     url = author +'/followers/'+ follower
    #     raise Exception
    #     t5_req = requests.put(url, auth=('connectionsuperuser','404connection'), headers={'Referer': "http://127.0.0.1:8000/"})
    #     if t5_req.status_code == 500:
    #         return ""
    #     else:
    #         return t5_req.json()

def get_likes_on_post(post):
    source = post["source"].strip("/")
    post["author"]["id"] = post["author"]["id"].strip("/")
    post["id"] = post["id"].strip("/")
    author_id = post["author"]["id"].split("/author/")[-1]
    post_id = post["id"].split("/posts/")[-1]
    for server in servers:
        if server[0][:-4] in source:
            auth = server[1]
            endpoint = "https://" + server[0] + "/author/" + author_id + "/posts/" + post_id + "/likes"
            # print(endpoint)
            req = requests.get(endpoint, auth=auth, headers={'Referer': "http://127.0.0.1:8000/"})
            # print(req.json())
            if req.status_code == 500:
                return ""
            else:
                return req.json()

    
def send_like_object(post, author, post_author):
    serializer = UserSerializer(author)
    author_id = post_author.strip("/").split("/author/")[-1]
    data = {}
    data["type"] = "like"
    data["author"] = serializer.data
    data["object"] = post
    data["@context"] = "https://www.w3.org/ns/activitystreams"
    for server in servers:
        if server[0][:-4] in post:
            auth = server[1]
            endpoint = "https://" + server[0] + "/author/" + author_id + "/inbox"
            req = requests.post(endpoint, auth=auth,data=data, headers={'Referer': "http://127.0.0.1:8000/"})
            # print(endpoint)
            # print(data)
            if req.status_code == 200:
                return True
    
    return False
