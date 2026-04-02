from django.core.files.uploadedfile import SimpleUploadedFile


def test_upload_photo(auth_client, point):
    client, _ = auth_client

    image = SimpleUploadedFile("test.jpg", b"filecontent", content_type="image/jpeg")

    response = client.post(
        f"/api/points/{point.id}/photos/", {"images": [image]}, format="multipart"
    )

    assert response.status_code == 201
