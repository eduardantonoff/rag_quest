import os
import argparse
import requests
import logging

logging.basicConfig(level=logging.DEBUG)


def upload_files(directory, url):
    # http_client = requests.Session()
    # http_client.verify = True
    # http_client.auth = None
    # http_client.proxies = {
    #     "http": None,
    #     "https": None,
    # }

    directory = os.path.abspath(os.path.normpath(directory))
    files_in_dir = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    for filename in files_in_dir:
        file_extension = os.path.splitext(filename)[1]

        file_ext = file_extension.lower()
        if file_ext in ['.pdf', '.docx', '.txt']:
            with open(os.path.join(directory, filename), 'rb') as f:

                file_data = f.read()
                response = requests.post(url, files={"file": (filename, file_data)})
                print(response.text)

                if response.status_code == 200:
                    print(f'Successfully uploaded: {filename}')
                else:
                    print(f'Failed to upload: {filename}')
        else:
            print(f'Skipping unsupported file type: {filename}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Upload PDF and DOCX files to API.')
    parser.add_argument('--src', type=str, required=True, help='Source directory path')
    parser.add_argument('--api', type=str, required=True, help='API endpoint URL')

    args = parser.parse_args()

    upload_files(args.src, args.api)
