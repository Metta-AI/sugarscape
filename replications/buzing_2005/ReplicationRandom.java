package nl.vu.cs.sugarland.util;

import java.util.Random;

/** Assign reproducible independent generator seeds in construction order. */
public final class ReplicationRandom {
    private static final Random seeds = new Random(Long.parseLong(System.getProperty("replication.seed")));

    private ReplicationRandom() {}

    public static synchronized Random create() {
        return new Random(seeds.nextLong());
    }
}
