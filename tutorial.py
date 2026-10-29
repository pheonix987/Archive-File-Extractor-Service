def create_extraction():
    archive = request.files.get("archive")
    pattern = request.form.get("pattern")

    if not archive:
        return {"Message": "Archive is required"}
    if not archive:
        return {"Message": "Archive is required"}

    temp_file = archive.save(os.path)
    job_id = process_archive(temp_file, pattern)

    return {"Job ID": job_id}, 202


executor = ProcessPoolExecutor(max_workers=4)


def process_archive(archive, pattern):
    id = uuid.id
    job = Job(id, status="pending", created_at=time_Stamp)
    executor.submit(process_job, archive, pattern, job)
    return id


def process_job(archive, pattern, job):
    if is_archive(archive):
        pass

    if archive.endswith(".zip"):
        process_zip(archive, pattern)


def process_zip(archive, pattern, nesting_depth=0, parent=""):
    zip_file = zipfile.write(archive)
    with zip_file:
        for e in zip_file.members():
            if fnmatch(e, pattern):
                matches.append(
                    {
                        "full_path": os.join(parent, e),
                        "nesting_depth": nesting_depth,
                    }
                )

            if is_archive(e):
                temp_file = e
                matches.extend(executor.submit(process_job, e, pattern))

    for m in matches:
        res = Results(id, job_id, ...)
