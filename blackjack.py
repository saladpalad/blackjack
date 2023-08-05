import copy
import random
import pygame
import numpy as np
from collections import defaultdict
import time

pygame.init()
# game variables
cards = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'K', 'Q', 'J', 'A']
one_deck = 4 * cards
decks = 4
WIDTH = 600
HEIGHT = 900
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption('Blackjack')
timer = pygame.time.Clock()
font = pygame.font.Font('freesansbold.ttf', 44)
score_font = pygame.font.Font('freesansbold.ttf', 36)
fps = 60
active = False
hand_active = False

# wins, losses, draws
games_played = 0
records = [0, 0, 0]
player_score = 0
dealer_score = 0

hidden_card = 0
initial_deal = False
my_hand = []
dealer_hand = []
outcome = 0
reveal_dealer = False
add_score = False
results = ['', 'YOU BUSTED o_O',
    'YOU WIN! :)', 'DEALER WINS :(', 'TIE GAME...']

#AI variables
prevState = None
prevAction = None
reward = 0
ai_mode = False
actionSpace = [0,1] # 0 for stick, 1 for hit
e = 0.1 #Epsilon Value for Monte Carlo Algorithm
gamma = 1 #Gamma Value for Monte Carlo Algorithm
alpha= 0.02 #Alpha Value for Monte Carlo Algorithm


Q = defaultdict(lambda: np.zeros(2)) #initializes an empty dictionary for Q table
currentEpisode = [] #list containing the moves of the game

#shuffle algo w/ fisher-yates
def shuffle_deck(deck):
    """Shuffle a deck of cards using the Fisher-Yates algorithm."""
    for i in range(len(deck) - 1, 0, -1):
        j = random.randint(0, i)
        deck[i], deck[j] = deck[j], deck[i]


# endgame func
def check_bust(hand_act, deal_score, player_score, result, totals, add):
    # check end game scenarios if player has stood, busted or blackjacked
    # result 1- player bust, 2-player win, 3-loss (dealer win), 4-draw
    if not hand_act and deal_score >= 17:
        if player_score > 21:
            result = 1
        elif deal_score < player_score <= 21 or deal_score > 21:
            result = 2
        elif player_score < deal_score <= 21:
            result = 3
        else:
            result = 4
        # run after each round
        if add:
            if result == 1 or result == 3:  # losses
                totals[1] += 1
            elif result == 2:  # wins
                totals[0] += 1
            else:  # draws
                totals[2] += 1
            add = False
    return result, totals, add

# display cards
def draw_cards(player, dealer, reveal):
    for i in range(len(player)):
        pygame.draw.rect(screen, 'white', [
                         70 + (70 * i), 460 + (5 * i), 120, 220], 0, 5)
        screen.blit(font.render(player[i], True,
                    'black'), (75 + 70 * i, 465 + 5 * i))
        screen.blit(font.render(player[i], True,
                    'black'), (75 + 70 * i, 635 + 5 * i))
        pygame.draw.rect(
            screen, 'red', [70 + (70 * i), 460 + (5 * i), 120, 220], 5, 5)

    # if player hasn't finished turn, dealer will hide one card
    for i in range(len(dealer)):
        pygame.draw.rect(screen, 'white', [
                         70 + (70 * i), 160 + (5 * i), 120, 220], 0, 5)
        if i != 0 or reveal:
            screen.blit(font.render(
                dealer[i], True, 'black'), (75 + 70 * i, 165 + 5 * i))
            screen.blit(font.render(
                dealer[i], True, 'black'), (75 + 70 * i, 335 + 5 * i))
        else:
            screen.blit(font.render('???', True, 'black'),
                        (75 + 70 * i, 165 + 5 * i))
            screen.blit(font.render('???', True, 'black'),
                        (75 + 70 * i, 335 + 5 * i))
        pygame.draw.rect(screen, 'blue', [
                         70 + (70 * i), 160 + (5 * i), 120, 220], 5, 5)

# deal cards
def deal_cards(current_hand, current_deck):
        card = random.randint(0, len(current_deck))
        current_hand.append(current_deck[card-1])
        current_deck.pop(card-1)
        return current_hand, current_deck

# calculate score of hand
def calculate_score(hand):
    hand_score = 0
    aces_count = hand.count('A')
    for i in range(len(hand)):
        # for 2,3,4,5,6,7,8,9 - just add the number to total
        for j in range(8):
            if hand[i] == cards[j]:
                hand_score += int(hand[i])
        # for 10 and face cards, add 10
        if hand[i] in ['10', 'J', 'Q', 'K']:
            hand_score += 10
        # for aces start by adding 11, and then check if it is too much
        elif hand[i] == 'A':
            hand_score += 11
    # determine how many aces need to be 1 instead off 11 to get under 21 if possible
    if hand_score > 21 and aces_count > 0:
        for i in range(aces_count):
            if hand_score > 21:
                hand_score -= 10
    return hand_score

# display scores
def draw_scores(player, dealer):
    screen.blit(score_font.render(
        f'My Hand [{player}] ', True, 'white'), (275, 400))
    if reveal_dealer:
        screen.blit(score_font.render(
            f'Dealer Hand [{dealer}] ', True, 'white'), (275, 100))

# display buttons
def draw_game(act, record, result):
    button_list = []
    # deal new hand
    if not act:
        deal = pygame.draw.rect(screen, 'white', [150, 20, 300, 100], 0, 5)
        pygame.draw.rect(screen, 'green', [150, 20, 300, 100], 3, 5)
        deal_text = font.render('PLAYER', True, 'black')
        screen.blit(deal_text, (205, 50))
        button_list.append(deal)

        ai = pygame.draw.rect(screen, 'white', [150, 250, 300, 100], 0, 5)
        pygame.draw.rect(screen, 'green', [150, 250, 300, 100], 3, 5)
        ai_text = font.render('AI', True, 'black')
        screen.blit(ai_text, (265, 280))
        button_list.append(ai)

    # show game
    else:
        hit = pygame.draw.rect(screen, 'white', [0, 700, 300, 100], 0, 5)
        pygame.draw.rect(screen, 'green', [0, 700, 300, 100], 3, 5)
        hit_text = font.render('HIT', True, 'black')
        screen.blit(hit_text, (100, 735))
        button_list.append(hit)

        stand = pygame.draw.rect(screen, 'white', [300, 700, 300, 100], 0, 5)
        pygame.draw.rect(screen, 'green', [300, 700, 300, 100], 3, 5)
        hit_text = font.render('STAND', True, 'black')
        screen.blit(hit_text, (365, 735))
        button_list.append(stand)

        score_text = score_font.render(
            f'   Wins: {record[0]}   Losses: {record[1]}   Draws: {record[2]}', True, 'white')
        screen.blit(score_text, (15, 840))
    # restart game
    if result != 0:
        screen.blit(font.render(results[result], True, 'white'), (15, 25))
        deal = pygame.draw.rect(screen, 'white', [150, 220, 300, 100], 0, 5)
        pygame.draw.rect(screen, 'green', [150, 220, 300, 100], 3, 5)
        pygame.draw.rect(screen, 'black', [153, 223, 294, 94], 3, 5)
        deal_text = font.render('NEW HAND', True, 'black')
        screen.blit(deal_text, (165, 250))
        button_list.append(deal)

    return button_list

#check if ace is valid
def is_valid_ace(hand):
    hand_score = 0
    aces_count = hand.count('A')
    for i in range(len(hand)):
        # for 2,3,4,5,6,7,8,9 - just add the number to total
        for j in range(8):
            if hand[i] == cards[j]:
                hand_score += int(hand[i])
        # for 10 and face cards, add 10
        if hand[i] in ['10', 'J', 'Q', 'K']:
            hand_score += 10
        # for aces start by adding 11, and then check if it is too much
        elif hand[i] == 'A':
            hand_score += 11
        # determine how many aces need to be 1 instead off 11 to get under 21 if possible
        if hand_score > 21 and aces_count > 0:
            for i in range(aces_count):
                if hand_score > 21:
                    hand_score -= 10

    if aces_count > 0 and hand_score <= 21:
        return True

    return False

#create a state value to represent the curren situation of the game
#state value: player's sum, dealer's hidden card value, validity of an ace in player's hand
def createStateValues(playersHand, dealersHand):
    return calculate_score(playersHand), calculate_score(dealersHand[0]), is_valid_ace(playersHand)

#follows an epsilon greedy policy, where the given Q determines the next action
#determine the best course of action to take in the current moment
#returns 0 for stand, 1 for hit
def generate_action(state, e, Q):
    probHit = Q[state][1]
    probStick = Q[state][0]

    if probHit > probStick:
        probs = [e, 1-e]
    elif probStick > probHit:
        probs = [1-e, e]
    else:
        probs = [0.5, 0.5]

    action = np.random.choice(np.arange(2), p=probs)
    return action

#Given an action (0 or 1), execute the action
def aiStep(action, playersHand, gameDeck):
    if action == 1 and hand_active: #hit
        playersHand, gameDeck = deal_cards(playersHand, gameDeck)
    #else: #stand
       # reveal_dealer = True

    return playersHand, gameDeck

#Changes Q after each completed game/episode
#where the 'learning' happens
def setQ(Q, currentEpisode, gamma, alpha):
    for t in range(len(currentEpisode)):
        #episode[t+1:,2] gives all the rewards in the episode from t+1 onwards
        rewards = currentEpisode[t:,2]

        #create a list with the gamma rate increasing
        discountRate = [gamma**i for i in range(1, len(rewards)+1)]
        
        #discounting the rewards from t+1 onwards
        updatedReward = rewards * discountRate
        
        #Sum up the discounted rewards to equal the return at time step t
        Gt = np.sum(updatedReward)
        
        #calculating the actual Q table value of the state,action pair
        Q[currentEpisode[t][0]][currentEpisode[t][1]] += alpha *(Gt - Q[currentEpisode[t][0]][currentEpisode[t][1]])
    
    return Q

# main game loop
run = True
while run:
    timer.tick(fps)
    screen.fill('black')

    games_played = records[0] + records[1] + records[2]

    # initial deal condition
    if initial_deal:
        for i in range(2):
            my_hand, game_deck = deal_cards(my_hand, game_deck)
            dealer_hand, game_deck = deal_cards(dealer_hand, game_deck)
        initial_deal = False
        
    # handle game condition
    if active:
        player_score = calculate_score(my_hand)
        draw_cards(my_hand, dealer_hand, reveal_dealer)
        
        #dealer's turn
        if reveal_dealer and not hand_active:
            dealer_score = calculate_score(dealer_hand)
            # dealer should hit on soft 17 as followed by most casinos
            if dealer_score <= 17:
                dealer_hand, game_deck = deal_cards(dealer_hand, game_deck)
        draw_scores(player_score, dealer_score)

    buttons = draw_game(active, records, outcome) #adds buttons as game progresses

    # AI aspect
    if ai_mode and active and not initial_deal:
        #time.sleep(2)
        if hand_active:
            currState = createStateValues(my_hand, dealer_hand)
            action = generate_action(currState, e, Q)
            currentEpisode.append((currState, action, reward))

        #dealer's turn when the AI stands
        if action == 0:
            hand_active = False
            reveal_dealer = True

        #check if AI busts
        if hand_active and player_score > 21:
            hand_active = False
            reveal_dealer = True

        #handle player hits
        if hand_active:
            my_hand, game_deck = aiStep(action, my_hand, game_deck)

        if outcome == 2: #AI wins
            reward = 1
        elif outcome == 1 or outcome == 3: #Dealer wins
            reward = -1
        elif outcome == 4: #draw
            reward = 0

        #reset episode after round is over
        if outcome != 0:
            currentEpisode.append((currState, action, reward))
            currState = None
            prevState = None
            currentEpisode = np.array(currentEpisode, dtype=object)
            Q = setQ(Q, currentEpisode, gamma, alpha)
            currentEpisode = []

    # handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONUP:
            if not active:
                # give control to player
                if buttons[0].collidepoint(event.pos):
                    active = True
                    initial_deal = True
                    game_deck = copy.deepcopy(decks * one_deck)
                    shuffle_deck(game_deck)
                    my_hand = []
                    dealer_hand = []
                    outcome = 0
                    hand_active = True
                    reveal_dealer = False
                    add_score = True
                # ai takes over
                elif buttons[1].collidepoint(event.pos):
                    active = True
                    initial_deal = True
                    game_deck = copy.deepcopy(decks * one_deck)
                    shuffle_deck(game_deck)
                    my_hand = []
                    dealer_hand = []
                    outcome = 0
                    hand_active = True
                    reveal_dealer = False
                    add_score = True
                    ai_mode = True

            # human aspect
            if not ai_mode and active and not initial_deal:
                # player hits
                if buttons[0].collidepoint(event.pos) and player_score < 21 and hand_active:
                    my_hand, game_deck = deal_cards(my_hand, game_deck)
                # player stand
                elif buttons[1].collidepoint(event.pos) and not reveal_dealer:
                    reveal_dealer = True
                    hand_active = False
                # start new game
                elif len(buttons) == 3:
                    if buttons[2].collidepoint(event.pos): 
                        active = True
                        initial_deal = True
                        game_deck = copy.deepcopy(decks * one_deck)
                        shuffle_deck(game_deck)
                        my_hand = []
                        dealer_hand = []
                        outcome = 0
                        reveal_dealer = False
                        hand_active = True
                        add_score = True
                        dealer_score = 0
                        player_score = 0

        if event.type == pygame.KEYDOWN:
            #plot blackjack values
            #records[0] - wins, records[1] - losses
            if active and ai_mode and event.key == pygame.K_p:
                from plot import plot_blackjack_values
                wins = records[0]
                losses = records[1]
                plot_blackjack_values(dict((k,np.max(v)) for k, v in Q.items()), games_played, wins, losses)
            #plot hit/stick policy
            if active and ai_mode and event.key == pygame.K_k:
                from plot import plot_policy
                policy = dict((k,np.max(v)) for k, v in Q.items())
                plot_policy(policy)
 
    #player automatically busts
    if not ai_mode and hand_active and player_score > 21:
        hand_active = False
        reveal_dealer = True

    #handles endgame function
    outcome, records, add_score = check_bust(hand_active, dealer_score, player_score, outcome, records, add_score)

    #resets game for the AI
    if ai_mode and len(buttons) == 3:
        reward = 0
        active = True
        initial_deal = True
        game_deck = copy.deepcopy(decks * one_deck)
        shuffle_deck(game_deck)
        my_hand = []
        dealer_hand = []
        outcome = 0
        reveal_dealer = False
        hand_active = True
        add_score = True
        dealer_score = 0
        player_score = 0

        if games_played in [250000] :
            from plot import plot_blackjack_values
            from plot import plot_policy
            wins = records[0]
            losses = records[1]
            draws = records[2]
            print("Wins: ")
            print(wins)
            print("Losses: ")
            print(losses)
            print("Draws")
            print(draws)
            plot_blackjack_values(dict((k, np.max(v)) for k, v in Q.items()), games_played, records[0], records[1])
            policy = dict((k,np.max(v)) for k, v in Q.items())
            plot_policy(policy)
           

    pygame.display.flip()

pygame.quit()