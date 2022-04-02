from fastapi.testclient import TestClient
from main import app

client = TestClient(app)



def test_add_face():
    r= None
    with open('resources/putin.jpg', 'rb') as f:
        r = client.post("/add_face/", files={'file': f, })
    print(r.text)
    assert True

def test_add_faces_in_bulk():
    r= None
    with open('resources/mixed.zip', 'rb') as f:
        r = client.post("/add_faces_in_bulk/", files={'file': f, })
    assert r.json()['body'] == "3 faces added"
    assert r.status_code == 200
    assert True

def test_get_face_info():
    r = None
    r = client.post("/get_face_info/",data={'api_key':'123', 'face_id':'1'})
    assert(r.json()['body']['person'] == "putin")
    assert r.status_code == 200

def test_search_faces():
    r = None
    with open('resources/putin-obama.jpg', 'rb') as f:
        r = client.post("/search_faces/", files={'file': f, }, params={'tolerance': 0.5, 'k': 1})
    assert r.status_code == 200
    

