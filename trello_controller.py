import requests
from datetime import datetime, timedelta
import json
from credentials import trello_key, trello_token, trello_board_id


class TrelloController:
    def __init__(self, target_list_name="准备中"):
        self.key = trello_key
        self.token = trello_token
        self.id_board = trello_board_id
        self.all_lists = self.get_all_lists()
        self.target_list = self.get_target_list(target_list_name)
        self.attachment_list = list()

    def get_all_lists(self):
        url = f"https://api.trello.com/1/boards/{self.id_board}/lists"

        query = {"key": self.key, "token": self.token}

        response = requests.request("GET", url, params=query)

        return response.json()

    def get_target_list(self, target_list_name):
        for list in self.all_lists:
            if list.get("name") == target_list_name:
                return list

    def set_target_list(self, list_name):
        self.target_list = self.get_target_list(list_name)

    def create_a_card(
        self,
        name="Test",
        desc="Test",
        pos=0,
        due=f"{(datetime.today()+timedelta(days=1, hours=11)).isoformat()}",
        due_complete=0,
        url_source="",
        id_members=[],
        id_labels=[],
        file_source="",
        id_card_source="",
    ):
        url = "https://api.trello.com/1/cards"

        query = {
            "key": self.key,
            "token": self.token,
            "idList": self.target_list.get("id"),
            "name": name,
            "desc": desc,
            "pos": pos,
            "due": due,
            "dueComplete": due_complete,
            "urlSource": url_source,
            "idMembers": id_members,
            "idLabels": id_labels,
            "fileSource": file_source,
            "idCardSource": id_card_source,
            "manualCoverAttachment": 1,
        }

        response = requests.request("POST", url, params=query)

        return response.json()

    def create_card_then_attach_link(
        self, name="Test", desc="test", url_source="www.google.com"
    ):
        response_card = self.create_a_card(name, desc)
        card_id = response_card.get("id")
        url = f"https://api.trello.com/1/cards/{card_id}/attachments"

        headers = {"Accept": "application/json"}

        query = {"key": self.key, "token": self.token, "url": url_source}

        response = requests.request("POST", url, headers=headers, params=query)

        # print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
        return response_card

    def get_cards_in_a_list(self, list_id):
        url = f"https://api.trello.com/1/lists/{list_id}/cards"

        query = {"key": self.key, "token": self.token}

        response = requests.request("GET", url, params=query)

        return response.json()

    def get_all_attachments_on_a_card(self, card_id):
        """
        Gets all the attachments from a single card. Attachments normally aren't available through self.get_cards_in_a_list()
        function. This is why we need to get all the attachments for a card first.

        :param card_id: Trello Card id
        :return: Dictionary. Returns the response of all the attachments on a card
        """
        url = f"https://api.trello.com/1/cards/{card_id}/attachments"

        headers = {"Accept": "application/json"}

        query = {"key": self.key, "token": self.token}

        response = requests.request("GET", url, headers=headers, params=query)

        return response.json()

    def get_all_attachment_from_cards_in_target_list(self):
        """
        This function simply iterates over each card in a list and gets their all attachments in a list.
        :return: list of attachments. Returns all the attachments as a list.
        """
        attach_list = list()

        for card in self.get_cards_in_a_list(self.target_list["id"]):
            for attachment in self.get_all_attachments_on_a_card(card["id"]):
                attach_list.append(attachment)

        return attach_list

    def get_all_urls_from_a_lists_attachments(self):
        self.attachment_list = self.get_all_attachment_from_cards_in_target_list()
        return [elem["url"] for elem in self.attachment_list]

    def get_description_for_a_card(self, card_id):

        url = f"https://api.trello.com/1/cards/{card_id}/desc"

        headers = {"Accept": "application/json"}

        query = {"key": self.key, "token": self.token}

        response = requests.request("GET", url, headers=headers, params=query)

        return response.json()

    def get_all_descriptions_from_target_list(self):
        desc_list = list()

        for card in self.get_cards_in_a_list(self.target_list["id"]):
            desc_list.append(self.get_description_for_a_card(card["id"]))

        return desc_list


if __name__ == "__main__":
    tre = TrelloController("在上传")
    print("\n".join(tre.get_all_urls_from_a_lists_attachments()))
    # print(tre.target_list) print(tre.get_cards_in_a_list(tre.target_list.get('id')))
    # tre.create_card_then_attach_link(name="test7", desc="[test again](www.google.com)",
    # url_source="https://docs.google.com/document/d/1exn-CA7tMxsWh8j3fGyHBon8lA_5bX80cSimCcehwrw/edit") print((
    # datetime.today()+timedelta(days=1, hours=11)).isoformat())
