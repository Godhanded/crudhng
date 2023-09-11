import requests

BASE_URI = "https://godand.pythonanywhere.com/api"

print("Ensure Internet is connected")
print(f"Base URI: {BASE_URI}")


def clean_up(id):
    """helper function to de clutter db by deleting created test records"""
    requests.delete(BASE_URI + f"/{id}")


def test_get_all_persons():
    """
    test get all persons in db
    """
    data = requests.get(BASE_URI)
    res = data.json()
    print(data)
    assert data.status_code == 200
    assert isinstance(res["persons"], list)


def test_create_person():
    """test add name of person record to db"""
    data = requests.post(BASE_URI, json={"name": "test"})
    res = data.json()

    assert data.status_code == 201
    assert res["id"] and res["name"]
    assert res["name"] == "test"
    clean_up(res["id"])


def test_read_person():
    """test get a singlw person in the db with user_id"""
    # create user to get by id
    data = (requests.post(BASE_URI, json={"name": "test_user"})).json()
    id = data["id"]  # get id of created user

    # request to get the user
    get_req = requests.get(BASE_URI + f"/{id}")
    res = get_req.json()

    assert get_req.status_code == 200
    assert isinstance(res, dict)
    assert res["message"] == "success"
    assert "person" in res
    assert "id" in res["person"]
    assert "name" in res["person"]
    assert res["person"]["name"] == "test_user"
    clean_up(id)


def test_update_person():
    """test perform update on name of person"""
    # create a person and get user_id
    data = (requests.post(BASE_URI, json={"name": "old name"})).json()
    id, old_name = data["id"], data["name"]  # get id and name of created user to edit

    # update person name
    update_res = (requests.patch(BASE_URI + f"/{id}", json={"name": "new name"})).json()

    # get the user back
    data = (requests.get(BASE_URI + f"/{id}")).json()
    new_id, new_name = data["person"]["id"], data["person"]["name"]

    assert update_res["message"] == "name updated"
    assert id == new_id  # assert its same user
    assert old_name != new_name  # assert old name and new name are different
    assert new_name == "new name"  # assert it updated to the correct name
    assert new_name == update_res["name"]
    clean_up(id)


def test_delete_person():
    """test delete person record"""
    # create a person and get user id
    data = (requests.post(BASE_URI, json={"name": "old name"})).json()
    id = data["id"]

    # delete the user
    delete_req = requests.delete(BASE_URI + f"/{id}")
    res = delete_req.json()

    assert delete_req.status_code == 200
    assert res["message"] == "deleted"
    assert res["id"] == id  # assert the correct id was deleted

    # try and get deleted person
    data = requests.get(BASE_URI + f"{id}")
    assert data.status_code == 404  # user not found
