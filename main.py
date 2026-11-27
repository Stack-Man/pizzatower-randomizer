#Author: Stack Man
#Date: 11/9/2026

#Run the program

#TODO: BS to JB can take awhile (0.7s - 1s)

#TODO: Try Immediate E to J can also take awhile
#its not immedaite E to J but everything before it, since the START of E to J reports 5s
#that means it took that long from TRY seg to DUMP

#it wasnt CLEAN ro DUMP, it was entrance_or_entranec_branch_segments which was taking a long time to finish ~5s
#theortically, since its always the START of the level, a failed E/EB to BS/BE pair will NEVER Succeed later
#therefore, we can store these between level generations and never try them again?

#but first lets try to figure out why its so expensive

#TODO: try to reduce repeated failed generations to an unsuccessful Js, hard b/c clean and replenish could mean the gen is possible...

#TODO: replace tower_tutorial1N/tower_tutorial with custom option between the two
#and use it for both peppino and noise

