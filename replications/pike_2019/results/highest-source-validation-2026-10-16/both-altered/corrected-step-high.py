def step_high(self, agent,meta):

    highest = None
    sele_agent = None

    #identify the highest
    for status in meta.sub_agents.values(): 
        if highest == None: 
            highest = list(status.accumulations.values())
            sele_agent = status.unique_id
        else:
            new = list(status.accumulations.values())
            if max(highest) < max(new):
                highest = new
                sele_agent = status.unique_id

    psuedo_accs = meta.sub_agents[sele_agent].accumulations

    #Use ML_mesa MetaAgent Buffer otherwise error
    #for agent in meta.agent_buffer(): 
    #store actual
    actual = agent.accumulations
    #replcae your accumulations with those of the lowest
    agent.accumulations = psuedo_accs
    #move with this new percpetion
    agent.move()
    #return you accumulations
    agent.accumulations = actual
    agent.eat()
    agent.eat()
    agent.die()
    if agent.status == "dead":
        return
    agent.trade()
