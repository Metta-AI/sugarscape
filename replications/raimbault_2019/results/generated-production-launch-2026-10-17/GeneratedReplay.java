import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;
import java.util.zip.GZIPInputStream;
import org.nlogo.headless.HeadlessWorkspace;

/** Stream original generated-landscape seeds without retaining the full archive in memory. */
public class GeneratedReplay {
    public static void main(String[] args) throws Exception {
        if (args.length != 5) {
            throw new IllegalArgumentException("Usage: GeneratedReplay model generated.csv.gz start stop output.csv");
        }
        int start = Integer.parseInt(args[2]);
        int stop = Integer.parseInt(args[3]);
        if (start < 0 || stop <= start) throw new IllegalArgumentException("Invalid row interval");
        String[] parameters = {"population", "minSugar", "maxSugar", "setup", "spPopulation", "spGrowth",
                               "spAlpha", "spDiffusion", "spDiffsteps", "syCenters", "syMaxPop",
                               "syRankSizeExp", "syCenterDens", "replication"};
        String[] columns = {"gini", "mwgini", "moran", "distance", "entropy", "slope", "rsquared",
                            "moranRessource", "distanceRessource", "entropyRessource", "slopeRessource", "rsquaredRessource"};
        String[] reporters = {"gini", "moving-window-gini", "moran", "mean-distance", "entropy", "slope", "slope-rsquared",
                              "moran-ressource", "mean-distance-ressource", "entropy-ressource", "slope-ressource", "slope-rsquared-ressource"};
        HeadlessWorkspace workspace = HeadlessWorkspace.newInstance();
        try (BufferedReader archive = new BufferedReader(new InputStreamReader(
                 new GZIPInputStream(Files.newInputStream(Path.of(args[1]))), StandardCharsets.UTF_8));
             BufferedWriter output = Files.newBufferedWriter(Path.of(args[4]), StandardOpenOption.CREATE_NEW)) {
            String[] names = archive.readLine().split(",");
            workspace.open(args[0]);
            output.write("row,id,seed,population,ticks," + String.join(",", columns) + "\n");
            for (int row = 0; row < stop; ++row) {
                String line = archive.readLine();
                if (line == null) throw new IllegalArgumentException("Requested interval exceeds archive");
                if (row < start) continue;
                String[] values = line.split(",");
                if (values.length != names.length) throw new IllegalStateException("Malformed archive row");
                Map<String, String> input = new HashMap<>();
                for (int index = 0; index < names.length; ++index) input.put(names[index], values[index]);
                if (!input.get("setup").equals("1")) throw new IllegalArgumentException("Expected generated landscape");
                StringBuilder setup = new StringBuilder("clear-all setup-experiment");
                for (String parameter : parameters) setup.append(" ").append(input.get(parameter));
                workspace.command(setup.toString());
                workspace.command("set total-time-steps 10000 repeat 10000 [ go if count turtles != initial-population [ error \"Population invariant failed\" ] ]");
                double ticks = (Double) workspace.report("ticks");
                if (ticks != 10000) throw new IllegalStateException("Incomplete horizon");
                output.write(row + "," + input.get("id") + "," + input.get("replication") + ","
                             + workspace.report("count turtles") + "," + ticks);
                for (String reporter : reporters) {
                    double result = (Double) workspace.report(reporter);
                    if (!Double.isFinite(result)) throw new IllegalStateException("Nonfinite " + reporter);
                    output.write("," + result);
                }
                output.write("\n");
                output.flush();
                System.out.println("completed_row=" + row);
            }
        } finally {
            workspace.dispose();
        }
    }
}
