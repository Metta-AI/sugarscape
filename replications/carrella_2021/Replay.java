import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.io.BufferedWriter;
import java.util.List;
import org.nlogo.headless.HeadlessWorkspace;

/** Replay one archived parameter row through the unchanged NetLogo model. */
public class Replay {
    public static void main(String[] args) throws Exception {
        if (args.length != 4) {
            throw new IllegalArgumentException("Usage: Replay model parameters.csv row-index output.csv");
        }
        List<String> inputs = Files.readAllLines(Path.of(args[1]));
        String[] names = inputs.get(0).split(",");
        String[] values = inputs.get(Integer.parseInt(args[2]) + 1).split(",");
        String[] reporters = {"count turtles", "normalized-gini", "sum [psugar] of patches",
                              "sum [pspice] of patches", "number_of_prices", "mean_prices"};
        HeadlessWorkspace workspace = HeadlessWorkspace.newInstance();
        try (BufferedWriter output = Files.newBufferedWriter(Path.of(args[3]), StandardOpenOption.CREATE_NEW)) {
            workspace.open(args[0], true);
            for (int index = 0; index < names.length; index++) {
                String command = names[index].equals("random-seed") ? "random-seed " : "set " + names[index] + " ";
                workspace.command(command + values[index]);
            }
            workspace.command("setup");
            output.write("tick," + String.join(",", reporters) + "\n");
            // Pre-2020 pyNetLogo reports before each of 501 go calls: ticks 0..500.
            for (int step = 0; step < 501; step++) {
                output.write(workspace.report("ticks").toString());
                for (String reporter : reporters) {
                    output.write("," + workspace.report(reporter));
                }
                output.write("\n");
                workspace.command("go");
            }
        } finally {
            workspace.dispose();
        }
    }
}
