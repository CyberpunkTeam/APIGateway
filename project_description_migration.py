import requests

# all_projects_endpoint = "https://apigateway-a64ymxbbqq-uc.a.run.app/projects/"
token = "Bearer mati"

# projects = requests.get(all_projects_endpoint, headers={"X-Tiger-Token": token})
#
# projects_ids = [project.get("pid") for project in projects.json()]
# print(projects_ids)


projects_ids = [
    "1d5561b1-0f3e-49ed-aa25-0b9416e2bcd6",
    "b6839d09-2ffe-4934-a7b3-0f85a25a4aaa",
    "67752f36-4f30-4022-8745-aefc2b222f1a",
    "7ab14051-3494-4edd-ba06-851348863f23",
    "11a6ebab-b801-4300-87cd-dbe345aa38ce",
    "1051b08b-cbe3-4e8b-b655-292cf7b43d16",
    "aad3a744-fc57-4715-ac42-bb909450c3b5",
    "d86d93fb-8434-40eb-85c2-6f4f1d9f9f40",
    "b23f92aa-e284-4cd8-974a-4d5b029c5421",
    "2fe484ce-b56a-4a1c-be24-aa59e8afba40",
    "0a602a5a-53db-45ee-9df8-69ff23ef292c",
    "a9247635-0915-4096-987e-7c6dd4312c3a",
    "4ed2b8ba-2fe6-4019-b7fd-d851d9458339",
    "876fef08-867b-48a3-8dc8-972d53842977",
    "43470c72-d96c-4c75-bedd-0e9ab8f0c03d",
    "c662e397-4682-45b6-8345-0fd8b2903fe8",
    "057dc2ae-462c-43f7-9fb6-bcdd67c8ff1a",
    "00fd679b-4b3c-49af-9b7f-bb7eefa3988e",
    "e17f4e38-ddee-4f6c-8e53-e37145ccfae1",
    "ce246e6e-6b12-40cc-8aac-014947ff458a",
    "325b738e-6911-4b2b-9ea2-ffeb1936b5cf",
    "6cef2fb2-a119-44a9-be01-79e60cb043ee",
]
put_projects_endpoint = "https://apigateway-a64ymxbbqq-uc.a.run.app/projects/{}"
pid_errors = []
for pid in projects_ids:
    body = {"description": {"functional_requirements": " "}}
    url = put_projects_endpoint.format(pid)
    mimetype = "application/json"
    headers = {"Content-Type": mimetype, "Accept": mimetype, "X-Tiger-Token": token}
    response = requests.put(url, json=body, headers=headers)
    if response.status_code != 200:
        pid_errors.append(pid)
