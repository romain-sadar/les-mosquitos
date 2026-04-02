def test_create_track(auth_client, parcours):
    client, _ = auth_client

    response = client.post(
        "/api/mission-tracks/",
        {"parcours": str(parcours.id), "latitude": 48.85, "longitude": 2.35},
    )

    assert response.status_code == 201
