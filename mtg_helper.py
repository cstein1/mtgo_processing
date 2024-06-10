import os
import sys
import json
import requests
import time

class Card:
    name: str = ""
    default_path: str = os.path.join(
                os.path.dirname(__file__), "tmp"
            )
    clicked: bool = False
    scryfall_image_url = "https://api.scryfall.com/cards/named?fuzzy="

    def __init__(self, name=""):
        self.name = name

    def get_scryfall_url(self) -> str:
        return self.scryfall_image_url+self.safe_name().replace(" ", "+")

    def safe_name(self) -> str:
        return self.name.replace(",", " ").replace("/", " ").replace("&", " ").replace("'", " ").replace("\"", " ").replace("Ã", " ")
    
    def get_path(self, pathname="") -> str:
        path_to_files = os.path.dirname(pathname)
        if not pathname:
            path_to_files = self.default_path
        
        return os.path.join(
                        path_to_files, self.safe_name() + ".jpg"
                )

    def download_card_image(self, pathname=""):
        path_to_files = os.path.dirname(pathname)
        if not pathname:
            path_to_files = self.default_path
        
        if not os.path.exists(path_to_files):
            os.makedirs(path_to_files)
        
        # out_dic = {}
        path_to_card = os.path.join(
                        path_to_files, self.safe_name() + ".jpg"
                )
        if not os.path.exists(path_to_card):
            print("Downloading card from: " + self.get_scryfall_url())
            req = requests.get(
                url=self.get_scryfall_url()
            )
            if req.status_code == 200:
                req_json = req.json()
                if (double_faced := "card_faces") in req_json and "image_uris" not in req_json:
                    req_json = req_json[double_faced][0]
                if (image_keys := "image_uris") in req_json:
                    if (small_key := "small") in req_json[image_keys]:
                        req = requests.get(url=req_json[image_keys][small_key])
                        if req.status_code == 200:
                            with open(path_to_card, 'wb') as f:
                                f.write(req.content)
                        time.sleep(.75)
            else:
                print(req)
                print("Failed to get card " + self.name)
        
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name
    
    def __add__(self, other):
        if isinstance(other, str):
            return self.name + other
        print("Cannot add card to non-string")
        sys.exit(1)

class Pack:
    """Qualities of a pack of magic cards are the pack pick, 
    the cards in the pack, and the name of the pack"""
    pack_pick: str = ""
    cards: list[Card] = []
    id_string: str = ""

    def __init__(self):
        self.cards = []

    def set_pick(self, pack_pick: str):
        self.pack_pick = pack_pick

    def add_card(self, card_name: str):
        self.cards.append(Card(card_name))

    def __str__(self) -> str:
        return ", ".join(list(map(lambda x: str(x), self.cards)))

class Draft:
    """A draft is a data object of a list of packs along
    with the picks made per each pack"""
    packs: list[Pack] = []
    CARDS: str = "cards" # keyname
    PICK: str = "pick" # keyname
    EXT: str = ".jpg" # image extention

    def __init__(self, filename: str):
        self.packs = []
        self.parse_file(filename)

    def parse_file(self, filename: str):
        if not os.path.exists(filename):
            print("File %s does not exist" % filename)
            sys.exit(1)

        with open(filename, "r+") as f:
            data_lines = f.readlines()
        
        pack_num = -1
        for line in data_lines[11:]:
            if not line.strip():
                continue
            elif line.startswith("Pack "):
                self.packs.append(Pack())
                pack_num += 1
            elif line.startswith((pick_delim := "Picked: ")):
                self.packs[pack_num].set_pick(line.removeprefix(pick_delim).strip())
            elif line.startswith((arr_delim := "-->")) or line.startswith((space_delim := "    ")):
                self.packs[pack_num].add_card(line.removeprefix(arr_delim).removeprefix(space_delim).strip())
            elif line.startswith("Pack "):
                self.packs[pack_num].id_string = line.strip()
            else:
                "Non interesting data point!"

    def __str__(self) -> str:
        out_str = "\n"
        for pack in self.packs:
            out_str += pack.id_string + str(pack) + "\n\n"
        return out_str
    
    def to_json(self) -> dict:
        pack_dict = {}
        for ind, pack in enumerate(self.packs):
            pack_dict[self.PICK + str(ind)] = {
                self.CARDS: pack.cards,
                self.PICK: pack.pack_pick
            }
        return pack_dict
    
    def to_list(self):
        pack_list = []
        for pack in self.packs:
            pack_list.append({
                "cards": pack.cards,
                "pick": pack.pack_pick
            })
        return pack_list
    
    def download_images(self):
        for vals in self.to_json().values():
            for card in vals[self.CARDS]:
                card.download_card_image()
                
    def pretty_print(self) -> str:
        return json.dumps(self.to_json(), indent=3)

class Deck:
    cards: list[Card] = []
    wrong_cards: list[Card] = []

    def add_card(self, new_card: Card):
        self.cards.append(new_card)
    
    def add_wrong_card(self, new_card: Card):
        self.wrong_cards.append(new_card)

if __name__ == "__main__":
    file = os.path.join(
        os.curdir,
        "penguiturtle-2024.5.19-8163-29405881-C03C03C03.txt"
    )

    new_game = Draft(file)
    print(new_game.download_images())
