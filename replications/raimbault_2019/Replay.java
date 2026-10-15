import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.io.BufferedWriter;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.nlogo.headless.HeadlessWorkspace;

/** Replay a complete archived 1,000-step experiment through NetLogo 5. */
public class Replay {
    public static void main(String[] args) throws Exception {
        if (args.length != 4) {
            throw new IllegalArgumentException("Usage: Replay model reference.csv row-index output.csv");
        }
        List<String> rows = Files.readAllLines(Path.of(args[1]));
        String[] names = rows.get(0).split(",");
        String[] values = rows.get(Integer.parseInt(args[2]) + 1).split(",");
        Map<String, String> input = new HashMap<>();
        for (int index = 0; index < names.length; index++) {
            input.put(names[index], values[index]);
        }
        String[] parameters = {"population", "minSugar", "maxSugar", "setup", "spPopulation", "spGrowth",
                               "spAlpha", "spDiffusion", "spDiffsteps", "syCenters", "syMaxPop",
                               "syRankSizeExp", "syCenterDens", "replication"};
        StringBuilder setup = new StringBuilder("setup-experiment");
        for (String parameter : parameters) {
            setup.append(" ").append(input.get(parameter));
        }
        HeadlessWorkspace workspace = HeadlessWorkspace.newInstance();
        try (BufferedWriter output = Files.newBufferedWriter(Path.of(args[3]), StandardOpenOption.CREATE_NEW)) {
            workspace.open(args[0]);
            workspace.command(setup.toString());
            output.write("tick,gini,population\n");
            for (int tick = 1; tick <= 1000; tick++) {
                workspace.command("go");
                output.write(workspace.report("ticks") + "," + workspace.report("gini") + ","
                             + workspace.report("count turtles") + "\n");
            }
            System.out.println("gini=" + workspace.report("gini") + "; archived=" + input.get("gini"));
            System.out.println("mwgini=" + workspace.report("moving-window-gini") + "; archived=" + input.get("mwgini"));
        } finally {
            workspace.dispose();
        }
    }
}
