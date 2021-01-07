import requests
from datetime import datetime, timedelta


class TrelloController:
    def __init__(self):
        self.key, self.token = self.get_credentials()
        self.id_board = self.get_board_id()
        self.all_lists = self.get_all_lists()
        self.target_list = self.get_target_list('准备中')

    @staticmethod
    def get_board_id():
        with open("trello_board_id.txt", "r") as file:
            board_id = file.readline().strip()
        return board_id

    @staticmethod
    def get_credentials():
        with open("trello_creds.txt", "r") as file:
            key = file.readline().strip()
            token = file.readline().strip()
        return key, token

    def get_all_lists(self):
        url = f"https://api.trello.com/1/boards/{self.id_board}/lists"

        query = {
            'key': self.key,
            'token': self.token
        }

        response = requests.request(
            "GET",
            url,
            params=query
        )

        return response.json()

    def get_target_list(self, target_list_name):
        for list in self.all_lists:
            if list.get('name') == target_list_name:
                return list

    def create_a_card(self,
                      name="Test",
                      desc="Test",
                      pos=0,
                      due=f"{(datetime.today()+timedelta(days=1, hours=11)).isoformat()}",
                      due_complete=0,
                      url_source="",
                      id_members=[],
                      id_labels=[],
                      file_source="",
                      id_card_source=""):
        url = "https://api.trello.com/1/cards"

        query = {
            'key': self.key,
            'token': self.token,
            'idList': self.target_list.get('id'),
            'name': name,
            'desc': desc,
            'pos': pos,
            'due': due,
            'dueComplete': due_complete,
            'urlSource': url_source,
            'idMembers': id_members,
            'idLabels': id_labels,
            'fileSource': file_source,
            'idCardSource': id_card_source,
            'manualCoverAttachment': 1
        }

        response = requests.request(
            "POST",
            url,
            params=query
        )

        return response.json()

    def create_card_then_attach_link(self, name="Test", desc="test", url_source="www.google.com"):
        response_card = self.create_a_card(name, desc)
        card_id = response_card.get('id')
        url = f"https://api.trello.com/1/cards/{card_id}/attachments"

        headers = {
            "Accept": "application/json"
        }

        query = {
            'key': self.key,
            'token': self.token,
            'url': url_source
        }

        response = requests.request(
            "POST",
            url,
            headers=headers,
            params=query
        )

        # print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
        return response_card

    def get_cards_in_a_list(self, list_id):
        url = f"https://api.trello.com/1/lists/{list_id}/cards"

        query = {
            'key': self.key,
            'token': self.token
        }

        response = requests.request(
            "GET",
            url,
            params=query
        )

        return response.json()


if __name__ == '__main__':
    tre = TrelloController()
    # print(tre.target_list)
    # print(tre.get_cards_in_a_list(tre.target_list.get('id')))
    tre.create_card_then_attach_link(name="test7", desc="[test again](www.google.com)", url_source="https://docs.google.com/document/d/1exn-CA7tMxsWh8j3fGyHBon8lA_5bX80cSimCcehwrw/edit")
    # print((datetime.today()+timedelta(days=1, hours=11)).isoformat())
