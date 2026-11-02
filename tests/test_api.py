def test_upload_csv(client, sample_csv_bytes):
    # TODO: Upload the sample CSV to POST /upload.
    # Assert status 200, six rows, two columns,
    # and a positive integer dataset ID.
    response = client.post("/upload", files={"file": ("sample_data.csv", sample_csv_bytes, "text/csv")})
    data = response.json()

    assert response.status_code == 200
    assert data["rows"] == 6
    assert data["columns"] == 2
    assert isinstance(data["id"], int)
    assert data["id"] > 0


def test_process_and_retrieve(
    client, uploaded_dataset_id, processing_body
):
    # TODO 1: Send a POST request to
    # /datasets/{uploaded_dataset_id}/process
    # using json=processing_body.
    # Assert status 200, one validation removal,
    # and a cleaning report showing 5 → 3 rows.

    # TODO 2: GET /datasets/{uploaded_dataset_id}.
    # Assert status 200 and total_rows == 3.
    # Check that the returned records contain student IDs
    # 1, 2, and 5 with scores 80, 90, and 85.
    
    response = client.post(f"/datasets/{uploaded_dataset_id}/process", json=processing_body)
    data = response.json()
    # id: int
    #     validation_rows_removed: int
    #     cleaning_report: dict[str, int]
    
    assert response.status_code == 200
    assert data["validation_rows_removed"] == 1
    assert data["cleaning_report"]["rows_before"] == 5
    assert data["cleaning_report"]["rows_after"] == 3

    response2 = client.get(f'/datasets/{uploaded_dataset_id}')
    data = response2.json()

    assert response2.status_code == 200
    assert data["total_rows"] == 3
    assert data["data"][0]["student_id"] == 1
    assert data["data"][1]['student_id'] == 2
    assert data["data"][2]['student_id'] == 5
    assert data["data"][0]["score"] == 80
    assert data["data"][1]["score"] == 90
    assert data["data"][2]["score"] == 85




def test_retrieve_missing_dataset(client):
    # TODO: Retrieve a dataset ID that does not exist.
    # Assert status 404.
    response = client.get('/datasets/99999999999999')

    assert response.status_code == 404
    
    


