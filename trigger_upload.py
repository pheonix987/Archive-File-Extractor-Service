import requests
filenames = ["simple_zip.zip", "nested_zip.zip", "nested_tar_zip.tar", "nested_targz_zip.tar.gz"]

for filename in filenames:
    response = requests.post(
        "http://localhost:8080/extractions",
        files={
            "archive": open(filename, "rb")
        },
        data={
            "pattern": "*.json"
        }
    )

    job_id = response.json()["job_id"]
    print(job_id)
 