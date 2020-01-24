from app.tests.assertions import assert_valid_schema


def test_read_videos(test_app):
    response = test_app.get('/comments/')
    assert response.status_code == 200
    assert_valid_schema(response.json(), 'comments/list.json')
