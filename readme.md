"Layer" concept taken to the extreme


Start on base layer where there are only arrows leaving transitions and entering doors
then from this door you transition to itself on the "exit" layer where all the arrows
are pointing out towards the exit door then the transition nodes
this should create a distinct flow where the only path you can take is 
transition node (start layer) > start door (start layer) > start door (exit layer) > exit door (exit layer) > transition node (exit layer)

Then the exit layer transition node can return to the start layer


There are also different pairs of layers for branching start, branching end, two ways (outside branch), one ways (during branch)



View of the Overall Layer Flow:


|-Path Start---------|-Two Way Loop----------------------------|-Branch Begin-------|-One Way Loop------------------------|-Branch End--------|--Path End-|
Level Start Node ---->Two Way Start Layer > Two Way Exit Layer > Branch Start Layer > One Way Start Layer > OW Exit Layer > Branch Exit Layer >> John Loop
                     ^                                         |                    ^                                     |                   |^
    	             |_________________________________________|                    |_____________________________________|                   ||
                     ^     				                       |									                                          ||
                     |_________________________________________)______________________________________________________________________________||
							                                   |                                                                               |
      							                               |_______________________________________________________________________________|

Two way Loop:
Repeating any number of Two-Way rooms.
Rooms must be traversible both ways and both times to be in this layer.

|-Start Layer-------------------------|-Exit Layer--------------------------------------|
> TW Start Transition > TW Start Door > Tw Start Door > TW Exit Door > TW Exit Transition > CHOICE: TW Start Layer or Branch Start Layer or John Loop


One Way Loop:
Repeating any number of One-Way OR Two-Way rooms.
Rooms CAN be traversible both ways. 
Prefer one-ways when possible.
Prefer choosing Branch Exit Layer when possible.
OW rooms must be traverisble in NOTPIZZATIME

|-Start Layer-------------------------|-Exit Layer--------------------------------------|
> OW Start Transition > OW Start Door > OW Start Door > OW Exit Door > OW Exit Transition > CHOICE: OW Start Layer or Branch Exit Layer


Branch Start/Exit Layer:
Single Choice. Room that Begins/Ends a "Branch" section of the path.
Upon Leaving Branch Exit, must also find an additional PIZZATIME OW loop path that reconnects to Branch Start
Branch Exit may also itself be a john

TW Loop > Branch Start/Any > OW Loop > Branch Exit/Any > CHOICE: TW Loop or John
                         



