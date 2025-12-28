import node_id_objects as nio

def find_path_through_all_layers(entrance_layer, branchentrance_layer, twoway_layer, branchstart_layer, oneway_layer, branchend_layer, brannchjohn_layer, john_layer):
    
    #start
        #to 1 or 1b
    #1. once through entrance
        #to 2
    #1b. once through branchentrance
        #to 4
    #2. n times through twoway     
    #3. once through branchstart       
    #4. n times through oneway  
        #to 5 or 5b
    #5. once through branchend
        #to 2 or 6
    #5b. once through branchjohn
        #END
    #6. once through john
        #END
    pass

def find_path_in_layer_from_transition(layer, initial_door_type, initial_door_dir):
    
    #pick potential transition types using inital values and
    #a graph linking allowed transitions
    
    #perhaps add all transitions labled as "initial" and connect them to valid
    #"start" transitions depending on traversal rules
    
    
    pass
    