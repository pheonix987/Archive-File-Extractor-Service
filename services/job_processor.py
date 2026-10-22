from config.db import db
from services.archive_processor import process_archive
from models.job import Job
from models.extracted_file import ExtractedFile
import os

def process_job(app, job_id, archive_path, archive_name, pattern):
    with app.app_context():

        try:

            job = db.session.get(Job, job_id)

            job.status = "running"

            db.session.commit()

            matches = process_archive(archive_path, archive_name, pattern)

            for match in matches:

                db.session.add(
                    ExtractedFile(
                        job_id=job_id,
                        full_path=match["full_path"],
                        file_name=match["file_name"],
                        file_size=match["file_size"],
                        nesting_depth=match["nesting_depth"],
                        source_archive=match["source_archive"],
                    )
                )

            job.status = "completed"

            print("MATCHES =", matches)

            db.session.commit()

        except Exception as e:

            job = Job.query.get(job_id)

            if job:

                job.status = "failed"
                job.error = str(e)

                db.session.commit()

        finally:
            if os.path.exists(archive_path):
                os.remove(archive_path)
