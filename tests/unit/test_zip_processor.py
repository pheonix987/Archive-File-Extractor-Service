from unittest.mock import MagicMock, patch
from services.zip_processor import process_zip
import io, zipfile

@patch("services.zip_processor.zipfile.ZipFile")
def test_process_zip_empty_archive(mock_zipfile):

    mock_zip = MagicMock()

    mock_zipfile.return_value.__enter__.return_value = mock_zip

    mock_zip.infolist.return_value = []

    response = process_zip(
        io.BytesIO(b""),
        "*.json"
    )

    assert response == []

    
def test_nested_zip(tmp_path):

    inner_zip = tmp_path / "inner.zip"

    with zipfile.ZipFile(inner_zip, "w") as z:
        z.writestr(
            "data.json",
            '{"name":"test"}'
        )

    outer_zip = tmp_path / "outer.zip"

    with zipfile.ZipFile(outer_zip, "w") as z:
        z.write(
            inner_zip,
            arcname="inner.zip"
        )

    matches = process_zip(
        str(outer_zip),
        "*.json"
    )

    assert len(matches) == 1

@patch("services.zip_processor.zipfile.ZipFile")
def test_process_zip_skips_directory(mock_zipfile):
    mock_zip = MagicMock()

    entry = MagicMock()
    entry.is_dir.return_value = True

    mock_zip.infolist.return_value = [entry]

    mock_zipfile.return_value.__enter__.return_value = mock_zip

    result = process_zip(
        io.BytesIO(b""),
        "*.json"
    )

    assert result == []

    entry.is_dir.assert_called_once()

@patch("services.zip_processor.is_archive")
@patch("services.zip_processor.zipfile.ZipFile")
def test_process_zip_handles_nested_archive_error(
    mock_zipfile,
    mock_is_archive
):
    mock_zip = MagicMock()

    entry = MagicMock()
    entry.is_dir.return_value = False
    entry.filename = "nested.zip"
    entry.file_size = 100

    mock_zip.infolist.return_value = [entry]

    mock_zip.read.side_effect = Exception(
        "Unable to read archive"
    )

    mock_zipfile.return_value.__enter__.return_value = mock_zip

    mock_is_archive.return_value = True

    result = process_zip(
        io.BytesIO(b""),
        "*.json"
    )

    assert result == []