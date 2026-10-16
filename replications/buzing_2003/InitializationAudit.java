package nl.vu.cs.sugarland.model;

import nl.vu.cs.sugarland.experiments.Experiment;

/** Observe instantiated 2003 attributes without advancing time or drawing randomness. */
public class InitializationAudit extends Experiment {
    private InitializationAudit() {
        super(new String[0]);
        if (!createDataLogDir()) throw new IllegalStateException("Cannot create data directory");
        createNewScape(DEFAULT_SCAPE_NAME, DEFAULT_SCAPE_PROPS);
        scape.setExperiment(this);
        scape.init();
    }

    public static void main(String[] args) {
        if (args.length != 0) throw new IllegalArgumentException("Configuration comes from working directory");
        InitializationAudit experiment = new InitializationAudit();
        Agent[] agents = experiment.scape.getAgents(false);
        if (agents.length != 400) throw new IllegalStateException("Initial population");
        System.out.println("agent,age,death_age,female,fertility_start,fertility_end,sugar,metabolism,vision,listen,talk");
        for (Agent generic : agents) {
            SugarAgent agent = (SugarAgent) generic;
            int[] p = agent.intProps;
            float[] f = agent.floatProps;
            if (f[SugarAgent.SUGAR_AMOUNT] != 50 || p[SugarAgent.SUGAR_METABOLISM] != 1 || p[Agent.VISION] != 1) throw new IllegalStateException("Agent endowment");
            if (p[Agent.DEATH_AGE] < 60 || p[Agent.DEATH_AGE] > 100 || agent.getAge() < 0 || agent.getAge() > p[Agent.DEATH_AGE]) throw new IllegalStateException("Initial age");
            if (p[Agent.BEGIN_CHILD_BEARING_AGE] < 12 || p[Agent.BEGIN_CHILD_BEARING_AGE] > 15) throw new IllegalStateException("Fertility start");
            int minimumEnd = p[Agent.FEMALE] == 1 ? 40 : 50;
            if (p[Agent.END_CHILD_BEARING_AGE] < minimumEnd || p[Agent.END_CHILD_BEARING_AGE] > minimumEnd + 10) throw new IllegalStateException("Fertility end");
            if (f[SugarAgent.LISTEN_PREF] != 1 || f[SugarAgent.TALK_PREF] < 0 || f[SugarAgent.TALK_PREF] > 1) throw new IllegalStateException("Communication initialization");
            if (p[SugarAgent.MIN_REPRODUCTION_SUGAR] != 5 || p[SugarAgent.MAX_REPRODUCTION_SUGAR] != 5) throw new IllegalStateException("Reproduction threshold");
            System.out.println("agent," + agent.getAge() + "," + p[Agent.DEATH_AGE] + "," + p[Agent.FEMALE] + "," + p[Agent.BEGIN_CHILD_BEARING_AGE] + "," + p[Agent.END_CHILD_BEARING_AGE] + "," + f[SugarAgent.SUGAR_AMOUNT] + "," + p[SugarAgent.SUGAR_METABOLISM] + "," + p[Agent.VISION] + "," + f[SugarAgent.LISTEN_PREF] + "," + f[SugarAgent.TALK_PREF]);
        }
        int[] sizes = new int[5];
        int seeds = 0;
        float sugar = 0;
        Cell[] cells = ((TorusScape) experiment.scape).getCells(false);
        for (Cell cell : cells) {
            ExtendedSugarPlant plant = (ExtendedSugarPlant) ((SugarCell) cell).getSugarPlant();
            for (int i = 0; i < plant.getNumberOfSeeds(); i++) {
                SugarSeed seed = plant.seedArray[i];
                if (seed.getGrowthRate() != 3 || seed.getCurrentSize() != seed.getMaxSize()) throw new IllegalStateException("Seed growth or initialization");
                ++sizes[(int) seed.getMaxSize()];
                sugar += seed.getCurrentSize();
                ++seeds;
            }
        }
        if (cells.length != 2500 || seeds != 500 || sugar != 1250) throw new IllegalStateException("Landscape totals");
        for (int size = 1; size <= 4; size++) if (sizes[size] != 125) throw new IllegalStateException("Seed composition");
        System.out.println("validated,400,500,1250,3");
    }
}
