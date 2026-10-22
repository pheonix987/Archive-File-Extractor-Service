from unittest.mock import patch
from sqlalchemy.exc import SQLAlchemyError

def test_clear_route(client):
    response = client.delete("/clear")
    assert response.json == {"message": "Cleared Successfully"}
    assert response.status_code == 200

@patch("app.ExtractedFile")
def test_clear_route_database_error(
    mock_extracted_file,
    client
):
    mock_extracted_file.query.delete.side_effect = (
        SQLAlchemyError("test database error")
    )

    response = client.delete("/clear")

    assert response.status_code == 500

    assert response.get_json() == {
        "error": "Database Error",
        "details": "test database error"
    }