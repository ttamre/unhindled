from datetime import datetime
import json
from logging import raiseExceptions
import uuid
from django.contrib import auth
from .models import User
from .serializers import UserSerializer
import requests
import logging

from unhindled.serializers import PostSerializer, UserSerializer


servers = [
        ('social-dis.herokuapp.com', ('socialdistribution_t03','c404t03')),
        ('cmput404-socialdist-project.herokuapp.com', ('socialcircleauth','cmput404')),
        ('linkedspace-staging.herokuapp.com/api', ('socialdistribution_t14','c404t14')),
        ('cmput404f21t17.herokuapp.com/service', ('a50ee73d-ee34-4201-8258-ead20eb71857','123456')),
        ('project-api-404.herokuapp.com/api/authors', ('team15','team15'))
    ]

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


    #foreign posts from team 5
    t5_req = requests.get('https://cmput404-social-circle.herokuapp.com/post/request_post_list?size=10000', auth=('socialdistribution_t05','c404t05'), headers={'Referer': "http://127.0.0.1:8000/"})
    if t5_req.status_code == 500:
        pass
    else:
        js_req_5 = t5_req.json()
        for post in js_req_5:
            post_list.append(post)

    #foreign posts from team 14
    t14_req = requests.get('https://linkedspace-staging.herokuapp.com/api/posts?size=10000', auth=('socialdistribution_t14','c404t14'), headers={'Referer': "http://127.0.0.1:8000/"})

    if t14_req.status_code == 500:
        pass
    else:
        js_req_14 = t14_req.json()
        for post in js_req_14:
            post_list.append(post)

   #foreign posts from team 17
    t17_req = requests.get('https://cmput404f21t17.herokuapp.com/service/connect/public/', auth=('a50ee73d-ee34-4201-8258-ead20eb71857','123456'), headers={'Referer': "http://127.0.0.1:8000/"})
    if t17_req.status_code == 500:
        pass
    else:
        js_req_17 = t17_req.json()['items']
        for post in js_req_17:
            if ":8000" not in post["source"]:
                post_list.append(post)

    #foreign posts from team 23
    # t23_req = requests.get('https://project-api-404.herokuapp.com/api/posts', auth=('team15','team15'), headers={'Referer': "http://127.0.0.1:8000/"})
    # if t23_req.status_code == 500:
    #     pass
    # else:
    #     print(t23_req)
    #     js_req_23 = t23_req.json()['items']
    #     for post in js_req_23:
    #         post_list.append(post)

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
    t5_req = requests.get('https://cmput404-social-circle.herokuapp.com/authors/', auth=('socialdistribution_t05','c404t05'), headers={'Referer': "http://127.0.0.1:8000/"})
    if t5_req.status_code == 500:
        pass
    else:
        js_req_5 = t5_req.json()['items']
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

    #foreign authors from team 17
    t17_req = requests.get('https://cmput404f21t17.herokuapp.com/service/connect/public/author/', auth=('a50ee73d-ee34-4201-8258-ead20eb71857','123456'), headers={'Referer': "http://127.0.0.1:8000/"})
    if t17_req.status_code == 500:
        pass
    else:
        js_req_17 = t17_req.json()['items']
        for author in js_req_17:
            author_list.append(author)

    #foreign authors from team 23
    # t23_req = requests.get('https://project-api-404.herokuapp.com/api/authors', auth=('team15','team15'), headers={'Referer': "http://127.0.0.1:8000/"})
    # if t23_req.status_code == 500:
    #     pass
    # else:
    #     js_req_23 = t23_req.json()['items']
    #     for author in js_req_23:
    #         author_list.append(author)

    #foreign authors from our own heroku for testing 
    #t15_req = requests.get('https://unhindled.herokuapp.com/service/authors', auth=('connectionsuperuser','404connection'), headers={'Referer': "http://127.0.0.1:8000/"})
    #if t15_req.status_code == 500:
        #pass
    #else:
        #js_req_15 = t15_req.json()['items']
        #for author in js_req_15:
            #author_list.append(author)
    return author_list

def send_post_to_inbox(author, post):
    for server in servers:
        if server[0][:-4] in author:
            serializer = PostSerializer(post)
            data = serializer.data
            auth = server[1]
            author_id = author.strip("/").split("/")[-1]
            endpoint = "https://" + server[0] + "/author/" + author_id + "/inbox"
            req = requests.post(endpoint, auth=auth,json=data, headers={'Referer': "http://127.0.0.1:8000/"})
            if req.status_code == 200:
                return True

    return False

#get author given author.id   
def foreign_get_author(author):
    #team 3 
    if "social-dis.herokuapp.com" in author:
        author = author.split("/")[4]
        url = "https://social-dis.herokuapp.com/connection/author-detail/"+author
        t3_req = requests.get(url, auth=('socialdistribution_t03','c404t03'), headers={'Referer': "http://127.0.0.1:8000/"})
        if t3_req.status_code == 500:
            return ""
        else:
            return t3_req.json()
    #team 14
    if "linkedspace-staging.herokuapp.com" in author:
        author = author.split("/")[4]
        url = "https://linkedspace-staging.herokuapp.com/api/author/"+author
        t14_req = requests.get(url, auth=('socialdistribution_t14','c404t14'), headers={'Referer': "http://127.0.0.1:8000/"})
        if t14_req.status_code == 500:
            return ""
        else:
            return t14_req.json()
    #team 17
    if "cmput404f21t17.herokuapp.com" in author:
        author = author.split("/")[4]
        url = "https://cmput404f21t17.herokuapp.com/service/author/"+author
        t17_req = requests.get(url, auth=('a50ee73d-ee34-4201-8258-ead20eb71857','123456'), headers={'Referer': "http://127.0.0.1:8000/"})
        if t17_req.status_code == 500:
            return ""
        else:
            return t17_req.json()
    
def foreign_send_friend_request(author, follower):
    #team 3 once implemented
    if "social-dis.herokuapp.com" in author:
        author = author.split("/")[4]
        url = "https://social-dis.herokuapp.com/connection/friend-request/"+author +'/'+ str(follower)
        t3_req = requests.post(url, auth=('socialdistribution_t03','c404t03'), headers={'Referer': "http://127.0.0.1:8000/"})
        if t3_req.status_code == 500:
            return ""
        else:
            return t3_req.json()
#sends put request to add one of our authors as a follower NOT CURRENTLY IN USE
def foreign_add_follower(author, follower):
    #team 3 once implemented
    if "social-dis.herokuapp.com" in author:
        url = author +'/followers/'+ follower
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

def get_comment_likes(comment_link, post):
    comment_link = comment_link.strip("/")
    host = post["author"]["host"]
    for server in servers:
        if server[0][:-4] in host:
            auth = server[1]
            if "/posts/" in post["id"]:
                post_id = post["id"].split("/posts/")[-1]
            else:
                post_id = post["id"].split("/post/")[-1]

            if "/comments/" in comment_link:
                comment_id = comment_link.split("/comments/")[-1]
                comment_id = "/comments/" + comment_id
            else:
                comment_id = comment_link.split("/comment/")[-1]
                comment_id = "/comment/" + comment_id
            author_id = post["author"]["id"].split("/author/")[-1]

            endpoint = "https://" + server[0] + "/author/" + author_id + "/posts/"+ post_id + comment_id + "/likes"
            req = requests.get(endpoint, auth=auth, headers={'Referer': "http://127.0.0.1:8000/"})
            response = req.json()
            if type(response) == list:
                return response
            else:
                return response["items"]
    return []

def post_foreign_comments(request, comm, postJson):
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
        payload = { "type": "comments",
                    "author": json.dumps(author),
                    "comment": comm,
                    "contentType": "text/plain",
                    "published": str(datetime.now()),
                    "id": postJson['id'].split('/')[-1]
                }
        t3_req = requests.post(postJson['id']+"/comments", auth=('socialdistribution_t03','c404t03'), headers={'Referer': "http://127.0.0.1:8000/"}, json=payload)
        
        if t3_req.status_code == 200:
            pass
        else:
            return t3_req.json()

    #print('team 14\n\n\n')
    #post comment on team 14
    if "linkedspace-staging.herokuapp.com" in postJson['id']:
        
        payload = {'Post_pk': postJson['comments'].replace('/comments', '').replace("/author/", "/api/author/"), 
                    'auth_pk': str(request.user.pk), 
                    'contentType': 'text/plain',
                    'text': comm
                    }
        # print(payload)
        api_url = postJson["comments"].replace("/author/", "/api/author/")
        t14_req = requests.post(api_url, auth=('socialdistribution_t14','c404t14'), headers={'Referer': "http://127.0.0.1:8000/"}, json=payload)
        if t14_req.status_code == 200:
            pass    
        else: 
            return t14_req.json()

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
            req = requests.get(endpoint, auth=auth, headers={'Referer': "http://127.0.0.1:8000/"})
            if req.status_code == 404:
                return ""
            elif req.status_code == 500:
                return ""
            else:
                return req.json()
                
def foreign_send_post_to_inbox(follower_id, author):
    foreign_author = foreign_get_author()
    #for server in servers: 
        #if server[0][:-4] in post:


def send_like_object(post_url, author, post_author):
    serializer = UserSerializer(author)
    author_id = post_author.strip("/").split("/author/")[-1]

    if "posts" in post_url:
        post_id = post_url.split("/posts/")[-1]
    else:
        post_id = post_url.split("/post/")[-1]

    data = {}
    data["type"] = "Like"
    data["author"] = serializer.data
    data["object"] = post_url
    data["@context"] = "https://www.w3.org/ns/activitystreams"
    data["summary"] = str(author.username) + " likes your post"
    for server in servers:
        if server[0][:-4] in post_url:
            auth = server[1]
            endpoint = "https://" + server[0] + "/author/" + author_id + "/inbox"
            likeEndpoint = "https://" + server[0] + "/author/" + author_id + "/posts/" + post_id + "/likes"
            req = requests.post(endpoint, auth=auth,json=data, headers={'Referer': "http://127.0.0.1:8000/"})
            req2 = requests.post(likeEndpoint, auth=auth,json=data, headers={'Referer': "http://127.0.0.1:8000/"})
            if req.status_code == 200 or req2.status_code == 200:
                return True
    
    return False

def send_like_comment(post_url, author, post_author,comment_id):
    serializer = UserSerializer(author)
    author_id = post_author.strip("/").split("/author/")[-1]
    data = {}
    if "posts" in post_url:
        post_id = post_url.split("/posts/")[-1]
    else:
        post_id = post_url.split("/post/")[-1]

    if "comments" in post_url:
        comment_id = comment_id.split("/comments/")[-1]
    else:
        comment_id = comment_id.split("/comment/")[-1]
    
    data["type"] = "Like"
    data["author"] = serializer.data
    data["object"] = post_url + "/comments/" + comment_id
    data["@context"] = "https://www.w3.org/ns/activitystreams"
    data["summary"] = str(author.username) + " likes your post"
    for server in servers:
        if server[0][:-4] in post_url:
            auth = server[1]
            endpoint = "https://" + server[0] + "/author/" + author_id + "/inbox"
            likeEndpoint = "https://" + server[0] + "/author/" + author_id + "/posts/" + post_id + "/comments/" + comment_id + "/likes"
            req = requests.post(endpoint, auth=auth,json=data, headers={'Referer': "http://127.0.0.1:8000/"})
            req2 = requests.post(likeEndpoint, auth=auth,json=data, headers={'Referer': "http://127.0.0.1:8000/"})
            if req.status_code == 200 or req2.status_code == 200:
                return True
    
    return False
