# Introduction

This is a Python-based client that connects to a [JSettlers2](https://github.com/jdmonin/JSettlers2) server and plays Settlers of Catan as either a random agent or Monte-Carlo tree search agent (MCTS). The client has only been tested on V.2.5.0.0 of JSettlers2. Currently the bot only works for 4-player base game play.

This is for the final project of 95-891: Introduction to AI at Heinz College, Carnegie Mellon. 

# Setup

Before you can run the bots, you need to have a way to connect to a JSettlers2 server. For these instructions, I will assume that the server is installed locally. 

# Instructions

## Play against 3 heuristic bots

To run a game with one of the bots against the JSettlers2 heuristic bots, do the following.

Start the server:

	java -Djsettlers.allow.debug=Y -jar JSettlers2-main\build\libs\JSettlersServer-2.5.00.jar -Djsettlers.startrobots=10 8080 50
	
Start the JSettlers2 client for viewing the game:

	java -Djsettlers.debug.traffic=Y -jar JSettlers2-main\build\libs\JSettlers-2.5.00.jar localhost 8080
	
Start the Python client:

	python Client.py bot_type 0 game_name localhost
	
bot_type can either be "random" or "mcts".
0 is the player number and designates where they sit. If it is set to 0, the bot initializes the game and starts it after 30 seconds. 
game_name is the name of the game. This will show  up in the JSettlers2 client display so that you can observe or play the game.

## Play against random bots

To play the mcts bot against random bots, do the following:

Start the server:

	java -Djsettlers.allow.debug=Y -jar JSettlers2-main\build\libs\JSettlersServer-2.5.00.jar -Djsettlers.startrobots=10 8080 50
	
Start the JSettlers2 client for viewing the game:

	java -Djsettlers.debug.traffic=Y -jar JSettlers2-main\build\libs\JSettlers-2.5.00.jar localhost 8080
	
	
Now you will start 4 clients. These can be any bot type that you would like (random or mcts). Open four terminals and run a client separately from each one. Make sure that you start the player_number=0 first because it creates the game so that the other bots can join. The game will begin 30 seconds after player_number=0 is run.

Start each Python client:

	python Client.py bot_type player_number game_name localhost