import java.nio.file.Files;
import java.nio.file.Path;
import org.nlogo.headless.HeadlessWorkspace;

/** Complete deterministic resource/starvation trajectories through native go. */
public class TrajectoryProbe {
    public static void main(String[] args) throws Exception {
        if (args.length != 2) throw new IllegalArgumentException("Usage: TrajectoryProbe model new-output");
        Path output = Files.createDirectory(Path.of(args[1]));
        HeadlessWorkspace workspace = HeadlessWorkspace.newInstance();
        try {
            workspace.open(args[0], true);
            int[][] cases = {{1, 1, 0, 4, 4}, {3, 3, 0, 4, 4}, {1, 1, 0, 4, 0},
                             {1, 1, -1, 4, 4}, {1, 1, 6, 4, 4}};
            for (int index = 0; index < cases.length; index++) {
                int[] c = cases[index];
                workspace.command("clear-all random-seed 123 set initial-population 0 "
                    + "set minimum-sugar-endowment 1 set maximum-sugar-endowment 10 "
                    + "set minimum-spice-endowment 1 set maximum-spice-endowment 10 "
                    + "set wealth-reproduction 100000 set pmut 0 set trade? true setup "
                    + "ask patches [set max-psugar 0 set max-pspice 0 set psugar 0 set pspice 0] "
                    + "ask patch 25 25 [set max-psugar " + c[3] + " set psugar " + c[3]
                    + " set max-pspice " + c[4] + " set pspice " + c[4] + "] "
                    + "create-turtles 1 [turtle-setup setxy 25 25 set sugar 10 set spice 10 "
                    + "set sugar-metabolism " + c[0] + " set spice-metabolism " + c[1]
                    + " set vision " + c[2] + " set vision-points [] "
                    + "foreach (range 1 (vision + 1)) [n -> set vision-points sentence vision-points "
                    + "(list (list 0 n) (list n 0) (list 0 (- n)) (list (- n) 0))] "
                    + "set wealth wealth-func sugar spice sugar-metabolism spice-metabolism] "
                    + "update-lorenz-and-gini set prices [] set mean_prices 7");
                String path = output.resolve("case-" + index + ".csv").toAbsolutePath().toString();
                workspace.command("file-open \"" + path + "\" "
                    + "file-print \"tick,population,gini,landscape_sugar,landscape_spice,trades,mean_price,agent_sugar,agent_spice,utility\" "
                    + "repeat 501 [file-print (word ticks \",\" count turtles \",\" normalized-gini "
                    + "\",\" sum [psugar] of patches \",\" sum [pspice] of patches \",\" number_of_prices "
                    + "\",\" mean_prices \",\" sum [sugar] of turtles \",\" sum [spice] of turtles "
                    + "\",\" sum [wealth] of turtles) go] file-close");
            }
        } finally {
            workspace.dispose();
        }
    }
}
