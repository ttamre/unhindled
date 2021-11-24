import requests


def get_list_foreign_posts():
    # foreign posts from team 3
    t3_req = requests.get('https://social-dis.herokuapp.com/posts', auth=('socialdistribution_t03','c404t03'), headers={'Referer': "http://127.0.0.1:8000/"})
    if t3_req.status_code == 500:
        pass
    else:
        js_req_3 = t3_req.json()
        
    # foreign posts from team5
    # t3_req = requests.get('https://social-dis.herokuapp.com/posts', auth=('socialdistribution_t03','c404t03'), headers={'Referer': "http://127.0.0.1:8000/"})
    # if t3_req.status_code == 500:
    #     pass
    # else:
    #     js_req_3 = t3_req.json()

    return js_req_3

def get_list_foreign_authors():
    # foreign authors from team 3
    t3_req = requests.get('https://social-dis.herokuapp.com/authors', auth=('socialdistribution_t03','c404t03'), headers={'Referer': "http://127.0.0.1:8000/"})
    if t3_req.status_code == 500:
        pass
    else:
        js_req_3 = t3_req.json()
    
    # foreign authors from team 5
    # t3_req = requests.get('https://social-dis.herokuapp.com/authors', auth=('socialdistribution_t03','c404t03'), headers={'Referer': "http://127.0.0.1:8000/"})
    # if t3_req.status_code == 500:
    #     pass
    # else:
    #     js_req_3 = t3_req.json()

    return js_req_3