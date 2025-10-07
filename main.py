import logging
import os
import subprocess

import requests
from google.cloud import secretmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_datastory_token_dev():
    s = secretmanager.SecretManagerServiceClient()
    secret = s.access_secret_version(name='projects/346704577283/secrets/nais-analyse-datafortelling-token/versions/latest')
    token = secret.payload.data.decode('UTF-8')
    return token


def render_quarto():
    try:
        logger.info("Starting Quarto render process.")
        result = subprocess.run(['quarto', 'render', 'deploy-complete-doc-datafortelling.ipynb', '--execute', '--output', 'index.html'], check=True, capture_output=True, text=True)
        logger.info("Quarto render completed successfully.")
        logger.debug(f"Quarto render output: {result.stdout}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error rendering Quarto document: {e.stderr}")
        raise


def update_quarto(files_to_upload: list[str]):
    logger.info("Starting Quarto update process.")
    multipart_form_data = {}
    for file_path in files_to_upload:
        file_name = os.path.basename(file_path)
        with open(file_path, 'rb') as file:
            file_contents = file.read()
            multipart_form_data[file_name] = (file_name, file_contents)
            logger.debug(f"Prepared file for upload: {file_name}")

    try:
        response = requests.put(
            f"https://{os.environ['ENV']}/quarto/update/{os.environ['QUARTO_ID']}",
            headers={"Authorization": f"Bearer {os.environ['DATAMARKEDSPLASSEN_TEAM_TOKEN']}"},
            files=multipart_form_data
        )
        response.raise_for_status()
        logger.info("Quarto update completed successfully.")
    except requests.RequestException as e:
        logger.error(f"Error updating Quarto document: {e}")
        raise



if __name__ == '__main__':
    is_dev = os.getenv('DATAMARKEDSPLASSEN_TEAM_TOKEN') is None
    if is_dev:
        logger.info("Env: dev")
        os.environ['DATAMARKEDSPLASSEN_TEAM_TOKEN'] = get_datastory_token_dev()
        os.environ['ENV'] = 'data.ekstern.dev.nav.no'
        os.environ['QUARTO_ID'] = '63738bcc-96a6-451b-b6af-4cc232236682'
    else: 
        logger.info("Env: prod")
    try:
        render_quarto()
        update_quarto(files_to_upload=["index.html"])
    except Exception as e:
        logger.error(f"Script failed: {e}")
    logger.info("Script finished.")