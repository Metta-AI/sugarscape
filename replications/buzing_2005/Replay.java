import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import nl.vu.cs.sugarland.experiments.Experiment;
import nl.vu.cs.sugarland.model.Scape;

/** Invoke the released model lifecycle without the empty CLI launch method. */
public class Replay {
    private static class Headless extends Experiment {
        private final CountDownLatch finished = new CountDownLatch(1);

        public Headless() {
            super(new String[0]);
            if (!createDataLogDir()) throw new IllegalStateException("Cannot create data directory");
            createNewScape(DEFAULT_SCAPE_NAME, DEFAULT_SCAPE_PROPS);
            scape.setExperiment(this);
            scape.init();
        }

        @Override
        public synchronized void scapeFinished(Scape model) {
            super.scapeFinished(model);
            finished.countDown();
        }

    }

    public static void main(String[] args) throws Exception {
        if (args.length != 0) throw new IllegalArgumentException("Configuration is read from the working directory");
        Headless experiment = new Headless();
        int initial = experiment.scape.getNumberOfAgents();
        if (!experiment.scape.start()) throw new IllegalStateException("Model did not start");
        if (!experiment.finished.await(60, TimeUnit.SECONDS)) throw new IllegalStateException("Model did not finish within 60 seconds");
        int expected = experiment.getIntProperty(Experiment.RUN_LENGTH);
        if (experiment.scape.getIteration() != expected) throw new IllegalStateException("Incomplete trajectory");
        System.out.println("iterations=" + expected + ",initial=" + initial + ",final=" + experiment.scape.getNumberOfAgents());
    }
}
