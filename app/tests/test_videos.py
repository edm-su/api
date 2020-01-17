from app.tests.assertions import assert_valid_schema


def test_read_videos(test_app):
    response = test_app.get('/videos/')
    assert response.status_code == 200
    assert_valid_schema(response.json(), 'videos/list.json')


def test_read_video(test_app):
    response = test_app.get(f'/videos/juan-sanchez-verknipt-day-1-ade-be-at-tv')
    assert response.status_code == 200
    assert_valid_schema(response.json(), 'videos/item.json')
