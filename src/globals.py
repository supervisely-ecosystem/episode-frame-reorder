import os

import supervisely as sly
from dotenv import load_dotenv

if sly.is_development():
    load_dotenv("local.env")
    load_dotenv(os.path.expanduser("~/supervisely.env"))

api = sly.Api.from_env()
sly.logger.info(f"API server address: {api.server_address}")

TEAM_ID = sly.env.team_id()
WORKSPACE_ID = sly.env.workspace_id()

PROJECT_ID = sly.env.project_id(raise_not_found=False)
DATASET_ID = sly.env.dataset_id(raise_not_found=False)
sly.logger.info(
    f"Team ID: {TEAM_ID}, Workspace ID: {WORKSPACE_ID}, "
    f"Project ID: {PROJECT_ID}, Dataset ID: {DATASET_ID}"
)

COLUMNS = [
    "ID",
    "Name",
    "Figures count",
    "Objects count",
    "Created At",
    "Updated At",
]
