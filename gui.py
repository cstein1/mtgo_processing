import os
import sys
import math
import pygame
import time

import mtg_helper

class Mouse:
    clicked = False 
    has_clicked = False

    def check_click(self):
        mouse_clicked = pygame.mouse.get_pressed()[0]
        if not self.has_clicked and mouse_clicked:
            self.clicked = True
        else:
            self.clicked = False
        self.has_clicked = True
        return self.clicked
    
    def check_unclick(self):
        mouse_clicked = pygame.mouse.get_pressed()[0]
        if not mouse_clicked:
            self.clicked = False
            self.has_clicked = False

mouse = Mouse()
deck = mtg_helper.Deck()

def render_card(card: mtg_helper.Card, ind: int, y_o: int, d_y: int, screen) -> tuple[int, int, int]:
    """y_o is where y starts, d_y if not 0 is the amount of displacement per row"""
    file = os.path.join(os.path.dirname(__file__), "tmp", card.safe_name() + draft.EXT)
    if not os.path.exists:
        card.download_or_get_existing_card_image(file)
    try:
        im = pygame.image.load(file)
    except:
        print("Could not find card " + str(card))
        sys.exit(1)
    s_w = screen.get_width()
    i_w, i_h = im.get_width(), im.get_height()
    x_per_row = math.floor(s_w/i_w)
    x = (ind % x_per_row) * i_w
    if d_y == 0:
        d_y = 1
    y = (math.floor(ind/x_per_row) * i_h)*d_y + y_o
    screen.blit(im, (x, y))
    return i_w, i_h, x, y

def render_cards(cards: list[mtg_helper.Card], picked: str, cursor_pos: tuple[int, int], screen) -> tuple[mtg_helper.Card, bool]:
    y = 0
    c_x, c_y = cursor_pos
    for ind, card in enumerate(cards):
        i_w, i_h, x, y = render_card(card, ind, 0, 0, screen)
        if c_x > x and c_x < x + i_w  and c_y > y and c_y < y + i_h: 
            pygame.draw.rect(screen, "red", pygame.Rect(x, y, i_w, i_h), 4)
            if mouse.check_click():
                deck.add_card(mtg_helper.Card(picked))
                if picked != card.name:
                    deck.add_wrong_card(card)
                render_card(mtg_helper.Card(picked), 0, screen.get_height()-i_h, 0, screen)
                pygame.display.update()
                time.sleep(.5)
                return card, True
            mouse.check_unclick()
    return None, False

def score(deck: mtg_helper.Deck):
    for card in deck.wrong_cards:
        print("Wrong card picked: " + str(card))
    print("Amount of wrong cards picked: %d out of %d" % (len(deck.wrong_cards), 45))

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()
    running = True

    d_x, d_y = 0, 0

    draft = mtg_helper.Draft("penguiturtle-2020.7.19-5308-18179315-C03C03C03.txt")
    draft.download_images()
    draft_list = draft.to_list()
    draft_ind = 0
    render_cards(draft_list[draft_ind][draft.CARDS], draft_list[draft_ind][draft.PICK],(0, 0), screen)

    drafted_ind = 0

    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        c_x, c_y = pygame.mouse.get_pos()

        if c_x != d_x or c_y != d_y or pygame.mouse.get_pressed()[0]:
            card, clicked = render_cards(draft_list[draft_ind][draft.CARDS], draft_list[draft_ind][draft.PICK], (c_x, c_y), screen)
            if clicked:
                draft_ind += 1
                if draft_ind == len(draft_list):
                    print("End of draft")
                    score(deck)
                    sys.exit(0)
                screen.fill("black")
            for ind, card in enumerate(deck.cards):
                # Render picked cards
                s_w, s_h = screen.get_width(), screen.get_height()
                render_card(card, ind, screen.get_height()/2, .15, screen)
            d_y = c_y
            d_x = c_x

        # flip() the display to put your work on screen
        pygame.display.flip()

        clock.tick(60)  # limits FPS to 60

    pygame.quit()
