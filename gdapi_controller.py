"""
How to install google_drive_api
1- Enbale Drive API from this link: https://developers.google.com/drive/api/v3/quickstart/python/
2- Install the package with the command below:
 pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib



"""
from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.file']


class GoogleDriveAPIController:
    def __init__(self):
        self.creds = None
        self.drive_service = None
        self.docs_service = None
        self.output_folder_id = None
        self.start_the_api()

    def credential_authorization(self):
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

    def service_creation(self):
        self.drive_service = build('drive', 'v3', credentials=self.creds)

    def start_the_api(self):
        self.credential_authorization()
        self.service_creation()

    def get_first_ten(self):
        results = self.drive_service.files().list(
            pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            print('No files found.')
        else:
            print('Files:')
            for item in items:
                print(f"{item['name']} ({item['id']})")

    def docx_to_gdocs_uploader(self,
                                 name='Test',
                                 filepath='2020.11.20/Test Document.docx',
                                 folder_id=None):

        """
            This function uploads a docx file as a Google Docs to the Google Drive.

        :parameter name is the name of the file being uploaded
        :parameter filepath is the relative path of the file being uploaded
        :parameter folder_id is the id of the folder we want to add this file to.

        mimetype used in metadata is referring to the target of the transformation. In this case we try to make Google
        Docs. the one we used in MediaFileUpload is referring to the source.

        Google's own MimeTypes to fill in metadata could be found here:
        - https://developers.google.com/drive/api/v3/mime-types
        Google's export MimeTypes to fill in media's mimetype could be found here:
        - https://developers.google.com/drive/api/v3/ref-export-formats

        """
        if not self.output_folder_id:
            with open("folder_id.txt", "r") as text:
                self.output_folder_id = text.readline().strip()

        if not folder_id:
            folder_id = self.output_folder_id

        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.document',
            'parents': [folder_id]
        }

        media = MediaFileUpload(filepath,
                                mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                                resumable=True)

        file = self.drive_service.files().create(body=file_metadata,
                                                 media_body=media,
                                                 fields='id').execute()
        file_link = "https://docs.google.com/document/d/" + file.get('id')
        return name, file_link

    def folder_search(self, query_type="mimeType='application/vnd.google-apps.folder'"):
        """
            This function searchs for all the folders in the Google Drive and prints their name and ID. This ID could
            be used when adding files in it.
            Change q parameter in list function to search different types of files. Full list is here:
            https://developers.google.com/drive/api/v3/ref-export-formats
            and here:
            https://developers.google.com/drive/api/v3/mime-types
            Some examples of queries:
            - name = '2020.11.18'
            - name contains '2020.11.18'
        :return:
        """
        # query_type = "name = 'Test'"
        page_token = None
        while True:
            response = self.drive_service.files().list(q=query_type,
                                                       spaces='drive',
                                                       fields='nextPageToken, files(id, name)',
                                                       pageToken=page_token).execute()
            for file in response.get('files', []):
                # Process change
                print(f"Found file: {file.get('name')} {file.get('id')}")
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break

    def show_the_metadata(self, file_id):
        """
            From file id show all the metadata of a file.
        :param file_id: Enter drive id for the file you want to see the metadafa of.
        :return:
        """
        file = self.drive_service.files().get(fileId=file_id, fields='*').execute()
        print(file)

    def upload_all_in_folder(self, folder_name='2020.11.20'):
        pathos = folder_name + '\\'
        files = os.listdir(pathos)
        uploaded_files = list()

        for file in files:
            patho_file = pathos + file
            uploaded_files.append(self.docx_to_gdocs_uploader(file, patho_file))
            print(patho_file)

        return uploaded_files


def main():
    gdapi = GoogleDriveAPIController()
    # gdapi.folder_search()
    # gdapi.show_the_metadata()
    # gdapi.docx_to_gdocs_uploader()
    print(gdapi.upload_all_in_folder("2020.12.07"))


if __name__ == '__main__':
    main()

