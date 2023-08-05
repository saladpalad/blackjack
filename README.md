# blackjack game

Blackjack card game with a Human & AI aspect

# Demo of Player Control

![blackjackplayer](https://github.com/saladpalad/blackjack/assets/59659804/2f23507d-d636-4fba-ae39-8157e94941c1)

# Demo of AI Control

![blackjackai](https://github.com/saladpalad/blackjack/assets/59659804/09c7889b-5ef7-49df-8079-7f3359def69a

# Explanation of AI aspect

I wanted to show how rigged blackjack is in casinos, so I built a blackjack bot that uses the Monte Carlo reinforcement learning technique, to try to beat the dealer at blackjack. I also configured the game environment, so that the dealer hits on a soft 17, which is a policy commonly enforced in casinos.

# Results after 1,000 Iterations
![1000graph](https://github.com/saladpalad/blackjack/assets/59659804/4b6018ed-ce59-4209-97aa-07901fc45f11)

Win Rate:
Loss Rate:
Draw Rate:

# Results after 10,000 Iterations
![10000graph](https://github.com/saladpalad/blackjack/assets/59659804/f4885a82-2e29-4027-84c3-ce8879e560c3)

Win Rate:
Loss Rate:
Draw Rate:

# Results after 25,000 Iterations
![25000graph](https://github.com/saladpalad/blackjack/assets/59659804/f444702e-f865-49bd-a3cb-2d205276a7e2)

Win Rate:
Loss Rate:
Draw Rate:

# Results after 100,000 Iterations
![100,000graph](https://github.com/saladpalad/blackjack/assets/59659804/4099e5f1-9ced-4c81-bcb6-fd18f33d2ceb)

Win Rate:
Loss Rate:
Draw Rate:

# Conclusion
As we can see from the graphs, the bot was able to learn which state values would be associated with high reward/wins. In this case as we can see the AI was able to win when they were given a hand closer to 21, and when the dealer's revealing card was high (as the dealer was most likely to bust).
Unfortunately, my bot only achieved a 38% win rate with the dealer hitting on a soft 17, so hopefully it doesn't develop a gambling addiction.




