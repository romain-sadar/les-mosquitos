import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io


def create_test_image(name="test.jpg"):
    file = io.BytesIO()
    image = Image.new("RGB", (100, 100))
    image.save(file, "JPEG")
    file.seek(0)
    return SimpleUploadedFile(name, file.read(), content_type="image/jpeg")


@pytest.mark.django_db
def test_upload_multiple_photos(auth_client, point):
    client, user = auth_client

    image1 = create_test_image("test1.jpg")
    image2 = create_test_image("test2.jpg")

    response = client.post(
        f"/api/points/{point.id}/photos/",
        data={"images": [image1, image2]},
        format="multipart",
    )

    assert response.status_code == 201
    assert len(response.data) == 2
