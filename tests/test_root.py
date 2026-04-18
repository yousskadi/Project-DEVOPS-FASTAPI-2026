def test_read_root(client):
    res = client.get("/")
    print(res.json())
    assert res.status_code == 200
    assert res.json() == {"message": "Hello all the World"}
