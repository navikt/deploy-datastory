# Script to update datastory on datamarkedsplassen

import os
import subprocess

import requests
from google.cloud import secretmanager


def get_datastory_token_dev():
    s = secretmanager.SecretManagerServiceClient()
    secret = s.access_secret_version(name='projects/346704577283/secrets/nais-analyse-datafortelling-token/versions/latest')
    token = secret.payload.data.decode('UTF-8')
    return token


def render_quarto():
    try:
        print("Starting Quarto render process.")
        # Run the quarto render command
        result = subprocess.run(['quarto', 'render', 'deploy-complete-doc-datafortelling.ipynb', '--execute', '--output', 'index.html'], check=True, capture_output=True, text=True)
        print("Quarto render completed successfully.")
        print(f"Quarto render output: {result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Error rendering Quarto document: {e.stderr}")
        raise


def update_quarto(files_to_upload: list[str]):
    print("Starting Quarto update process.")
    multipart_form_data = {}
    for file_path in files_to_upload:
        file_name = os.path.basename(file_path)
        with open(file_path, 'rb') as file:
            # Read the file contents and store them in the dictionary
            file_contents = file.read()
            multipart_form_data[file_name] = (file_name, file_contents)
            print(f"Prepared file for upload: {file_name}")

    try:
        # Send the request with all files in the dictionary
        response = requests.put(
            f"https://{os.environ['ENV']}/quarto/update/{os.environ['QUARTO_ID']}",
            headers={"Authorization": f"Bearer {os.environ['DATAMARKEDSPLASSEN_TEAM_TOKEN']}"},
            files=multipart_form_data
        )
        response.raise_for_status()
        print("Quarto update completed successfully.")
    except requests.RequestException as e:
        print(f"Error updating Quarto document: {e}")
        raise



if __name__ == '__main__':
    #if os.getenv('DATAMARKEDSPLASSEN_TEAM_TOKEN') is None:
    if True:
        os.environ['DATAMARKEDSPLASSEN_TEAM_TOKEN'] = get_datastory_token_dev()
        os.environ['ENV'] = 'data.ekstern.dev.nav.no'
        os.environ['QUARTO_ID'] = '63738bcc-96a6-451b-b6af-4cc232236682'
    try:
        render_quarto()
        update_quarto(files_to_upload=["index.html"])
    except Exception as e:
        print(f"Script failed: {e}")
    print("Script finished.")