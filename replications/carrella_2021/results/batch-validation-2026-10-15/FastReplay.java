import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.io.BufferedWriter;
import java.util.List;
import org.nlogo.headless.HeadlessWorkspace;

/** Replay a half-open range of archived inputs through the unchanged NetLogo model. */
public class FastReplay {
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
                String outputPath = directory.resolve("row-" + row + ".csv").toAbsolutePath().toString();
                String command = "file-open \"" + outputPath + "\" file-print \"tick," + String.join(",", reporters) + "\" repeat 501 [file-print (word ticks";
                for (String reporter : reporters) {
                    command += " \",\" (" + reporter + ")";
                }
                workspace.command(command + ") go] file-close");
                System.out.println("Completed row " + row + " in " + (System.nanoTime() - started) / 1e9 + " seconds");
            }
        } finally {
            workspace.dispose();
        }
    }
}
