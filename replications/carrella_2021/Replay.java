import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import org.nlogo.headless.HeadlessWorkspace;

/** Replay a half-open range of archived inputs through the unchanged NetLogo model. */
public class Replay {
    public static void main(String[] args) throws Exception {
        if (args.length != 5) {
            throw new IllegalArgumentException("Usage: Replay model parameters.csv start-row stop-row output-directory");
        }
        List<String> inputs = Files.readAllLines(Path.of(args[1]));
        String[] names = inputs.get(0).split(",");
        int start = Integer.parseInt(args[2]);
        int stop = Integer.parseInt(args[3]);
        if (start < 0 || start >= stop || stop > inputs.size() - 1) {
            throw new IllegalArgumentException("Row range must be nonempty and within the parameter CSV");
        }
        Path directory = Files.createDirectory(Path.of(args[4]));
        String[] reporters = {"count turtles", "normalized-gini", "sum [psugar] of patches",
                              "sum [pspice] of patches", "number_of_prices", "mean_prices"};
        HeadlessWorkspace workspace = HeadlessWorkspace.newInstance();
        try {
            workspace.open(args[0], true);
            for (int row = start; row < stop; row++) {
                long started = System.nanoTime();
                String[] values = inputs.get(row + 1).split(",");
                for (int index = 0; index < names.length; index++) {
                    String command = names[index].equals("random-seed") ? "random-seed " : "set " + names[index] + " ";
                    workspace.command(command + values[index]);
                }
                workspace.command("setup");
                Path output = Files.createFile(directory.resolve("row-" + row + ".csv"));
                String outputPath = output.toAbsolutePath().toString().replace("\\", "\\\\").replace("\"", "\\\"");
                // Report before each go, matching the historical connector.
                String command = "file-open \"" + outputPath + "\" file-print \"tick," + String.join(",", reporters) + "\" repeat 501 [file-print (word ticks";
                for (String reporter : reporters) {
                    command += " \",\" (" + reporter + ")";
                }
                workspace.command(command + ") go] file-close");
                List<String> observations = Files.readAllLines(output);
                if (observations.size() != 502) {
                    throw new IllegalStateException("Incomplete trajectory for row " + row + ": " + observations.size() + " lines");
                }
                for (int tick = 0; tick <= 500; tick++) {
                    String[] fields = observations.get(tick + 1).split(",", -1);
                    if (fields.length != 7 || Double.parseDouble(fields[0]) != tick) {
                        throw new IllegalStateException("Invalid trajectory at row " + row + ", tick " + tick);
                    }
                    for (String field : fields) {
                        if (!Double.isFinite(Double.parseDouble(field))) {
                            throw new IllegalStateException("Nonfinite trajectory at row " + row + ", tick " + tick);
                        }
                    }
                }
                System.out.println("Completed row " + row + " in " + (System.nanoTime() - started) / 1e9 + " seconds");
            }
        } finally {
            workspace.dispose();
        }
    }
}
