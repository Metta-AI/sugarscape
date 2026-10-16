package nl.vu.cs.sugarland.model;

import java.util.ArrayList;
import java.util.IdentityHashMap;

/** Observe seed accounting at each native data boundary without drawing randomness. */
public final class ResourceAudit {
    public static void observe(SugarScape scape) {
        ArrayList<SugarSeed> seeds = new ArrayList<>();
        float available = 0;
        int occupied = 0;
        for (Cell cell : scape.getCells(false)) {
            ExtendedSugarPlant plant = (ExtendedSugarPlant) ((SugarCell) cell).getSugarPlant();
            float contents = 0;
            for (int i = 0; i < plant.getNumberOfSeeds(); i++) {
                SugarSeed seed = plant.seedArray[i];
                seeds.add(seed);
                contents += seed.getCurrentSize();
            }
            if (contents != plant.getSize()) throw new IllegalStateException("Plant accounting mismatch");
            available += contents;
            if (contents > 0) occupied++;
        }
        for (int i = 0; i < scape.numberOfSeedsToDistribute; i++) seeds.add(scape.sugarSeedsToDistribute[i]);
        if (seeds.size() != 500) throw new IllegalStateException("Seed count changed");
        IdentityHashMap<SugarSeed, Boolean> identities = new IdentityHashMap<>();
        int[] sizes = new int[5];
        float total = 0;
        for (SugarSeed seed : seeds) {
            if (identities.put(seed, true) != null) throw new IllegalStateException("Duplicate seed identity");
            float maximum = seed.getMaxSize();
            float current = seed.getCurrentSize();
            if (maximum < 1 || maximum > 4 || maximum != (int) maximum) throw new IllegalStateException("Seed maximum changed");
            if (!Float.isFinite(current) || current < 0 || current > maximum || seed.getGrowthRate() != 3) throw new IllegalStateException("Seed bounds or growth changed");
            sizes[(int) maximum]++;
            total += current;
        }
        for (int size = 1; size <= 4; size++) if (sizes[size] != 125) throw new IllegalStateException("Seed composition changed");
        System.out.println("resource-audit," + scape.getIteration() + "," + seeds.size() + "," + scape.numberOfSeedsToDistribute + "," + available + "," + total + "," + occupied);
    }
}
