import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.io.BufferedWriter;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.nlogo.headless.HeadlessWorkspace;

/** Replay an archived row interval at the validated 10,000-step horizon. */
public class BatchReplay {
    public static void main(String[] args) throws Exception {
        if (args.length != 5) {
            throw new IllegalArgumentException("Usage: BatchReplay model reference.csv start stop output.csv");
        }
        int steps = 10000;
        int start = Integer.parseInt(args[2]);
        int stop = Integer.parseInt(args[3]);
        List<String> rows = Files.readAllLines(Path.of(args[1]));
        String[] names = rows.get(0).split(",");
        String[] parameters = {"population", "minSugar", "maxSugar", "setup", "spPopulation", "spGrowth",
                               "spAlpha", "spDiffusion", "spDiffsteps", "syCenters", "syMaxPop",
                               "syRankSizeExp", "syCenterDens", "replication"};
        HeadlessWorkspace workspace = HeadlessWorkspace.newInstance();
        try (BufferedWriter output = Files.newBufferedWriter(Path.of(args[4]), StandardOpenOption.CREATE_NEW)) {
            workspace.open(args[0]);
            if (start < 0 || stop <= start || stop > rows.size() - 1) throw new IllegalArgumentException("Invalid row interval");
            output.write("row,seed,population,ticks,gini,mwgini,archived_gini,archived_mwgini\n");
            for (int row = start; row < stop; ++row) {
                String[] values = rows.get(row + 1).split(",");
                if (values.length != names.length) throw new IllegalStateException("Malformed archive row");
                Map<String, String> input = new HashMap<>();
                for (int index = 0; index < names.length; ++index) input.put(names[index], values[index]);
                // Headless setup creates turtles without clearing prior agents. Reset before reseeding.
                StringBuilder setup = new StringBuilder("clear-all setup-experiment");
                for (String parameter : parameters) setup.append(" ").append(input.get(parameter));
                workspace.command(setup.toString());
                workspace.command("set total-time-steps " + steps + " repeat " + steps + " [ go if count turtles != initial-population [ error \"Population invariant failed\" ] ]");
                double tick = (Double) workspace.report("ticks");
                double population = (Double) workspace.report("count turtles");
                double gini = (Double) workspace.report("gini");
                double window = (Double) workspace.report("moving-window-gini");
                if (tick != steps || !Double.isFinite(gini) || !Double.isFinite(window)) throw new IllegalStateException("Incomplete or nonfinite simulation");
                output.write(row + "," + input.get("replication") + "," + population + "," + tick + "," + gini + "," + window + "," + input.get("gini") + "," + input.get("mwgini") + "\n");
                output.flush();
                System.out.println("completed_row=" + row);
            }
        } finally {
            workspace.dispose();
        }
    }
}
