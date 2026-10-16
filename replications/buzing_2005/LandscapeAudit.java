package nl.vu.cs.sugarland.model;

import java.util.Map;
import java.util.TreeMap;
import nl.vu.cs.sugarland.experiments.Experiment;
import nl.vu.cs.sugarland.model.Cell;
import nl.vu.cs.sugarland.model.ExtendedSugarPlant;
import nl.vu.cs.sugarland.model.SugarCell;
import nl.vu.cs.sugarland.model.TorusScape;

/** Read the initialized landscape without advancing the simulation or drawing randomness. */
public class LandscapeAudit extends Experiment {
    private LandscapeAudit() {
        super(new String[0]);
        if (!createDataLogDir()) throw new IllegalStateException("Cannot create data directory");
        createNewScape(DEFAULT_SCAPE_NAME, DEFAULT_SCAPE_PROPS);
        scape.setExperiment(this);
        scape.init();
    }

    public static void main(String[] args) {
        if (args.length != 0) throw new IllegalArgumentException("Configuration comes from the working directory");
        LandscapeAudit experiment = new LandscapeAudit();
        Cell[] cells = ((TorusScape) experiment.scape).getCells(false);
        Map<Float, Integer> amounts = new TreeMap<>();
        Map<Float, Integer> seedSizes = new TreeMap<>();
        int seeds = 0;
        int multipleSeeds = 0;
        int aboveFour = 0;
        float sugar = 0;
        for (Cell cell : cells) {
            ExtendedSugarPlant plant = (ExtendedSugarPlant) ((SugarCell) cell).getSugarPlant();
            float amount = plant.getSize();
            amounts.merge(amount, 1, Integer::sum);
            sugar += amount;
            seeds += plant.getNumberOfSeeds();
            nl.vu.cs.sugarland.model.SugarSeed[] values = plant.seedArray;
            for (int i = 0; i < plant.getNumberOfSeeds(); i++) {
                seedSizes.merge(values[i].getMaxSize(), 1, Integer::sum);
            }
            if (plant.getNumberOfSeeds() > 1) ++multipleSeeds;
            if (amount > 4) ++aboveFour;
        }
        System.out.println("cells,seeds,sugar,multiple_seed_cells,cells_above_four");
        System.out.println(cells.length + "," + seeds + "," + sugar + "," + multipleSeeds + "," + aboveFour);
        System.out.println("seed_maximum,count");
        for (Map.Entry<Float, Integer> entry : seedSizes.entrySet()) {
            System.out.println(entry.getKey() + "," + entry.getValue());
        }
        System.out.println("amount,cells");
        for (Map.Entry<Float, Integer> entry : amounts.entrySet()) {
            System.out.println(entry.getKey() + "," + entry.getValue());
        }
    }
}
