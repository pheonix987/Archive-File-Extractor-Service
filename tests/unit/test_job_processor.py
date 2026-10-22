from unittest.mock import MagicMock, patch

from services.job_processor import process_job


@patch("services.job_processor.ExtractedFile")
@patch("services.job_processor.process_archive")
@patch("services.job_processor.db")
def test_process_job_success(
    mock_db,
    mock_process_archive,
    mock_extracted_file,
):
    app = MagicMock()

    app_context = MagicMock()
    app.app_context.return_value.__enter__.return_value = app_context
    app.app_context.return_value.__exit__.return_value = None

    job = MagicMock()
    job.id = "job-123"
    job.status = "pending"

    mock_db.session.get.return_value = job

    mock_process_archive.return_value = [
        {
            "full_path": "/tmp/file1.txt",
            "file_name": "file1.txt",
            "file_size": 123,
            "nesting_depth": 1,
            "source_archive": "archive.zip",
        }
    ]

    process_job(
        app=app,
        job_id="job-123",
        archive_path="/tmp/archive.zip",
        archive_name="archive.zip",
        pattern="*.txt",
    )

    assert job.status == "completed"

    mock_db.session.get.assert_called_once()
    mock_process_archive.assert_called_once_with(
        "/tmp/archive.zip",
        "archive.zip",
        "*.txt",
    )

    mock_extracted_file.assert_called_once_with(
        job_id="job-123",
        full_path="/tmp/file1.txt",
        file_name="file1.txt",
        file_size=123,
        nesting_depth=1,
        source_archive="archive.zip",
    )

    mock_db.session.add.assert_called_once()
    assert mock_db.session.commit.call_count == 2
    

@patch("services.job_processor.Job")
@patch("services.job_processor.process_archive")
@patch("services.job_processor.db")
def test_process_job_failure(
    mock_db,
    mock_process_archive,
    mock_job_model,
):
    app = MagicMock()

    app_context = MagicMock()
    app.app_context.return_value.__enter__.return_value = app_context
    app.app_context.return_value.__exit__.return_value = None

    running_job = MagicMock()
    mock_db.session.get.return_value = running_job

    mock_process_archive.side_effect = Exception(
        "processing failed"
    )

    failed_job = MagicMock()
    mock_job_model.query.get.return_value = failed_job

    process_job(
        app=app,
        job_id="job-123",
        archive_path="/tmp/archive.zip",
        archive_name="archive.zip",
        pattern="*.txt",
    )

    assert failed_job.status == "failed"
    assert failed_job.error == "processing failed"

    mock_db.session.commit.assert_called()