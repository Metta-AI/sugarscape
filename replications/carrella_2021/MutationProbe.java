import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import org.nlogo.headless.HeadlessWorkspace;

/** Native complete reproductive ticks at lower metabolism and upper/lower vision boundaries. */
public class MutationProbe {
    public static void main(String[] args) throws Exception {
        if (args.length != 2) throw new IllegalArgumentException("Usage: MutationProbe model new-output");
        Path output = Files.createDirectory(Path.of(args[1]));
        List<String> rows = new ArrayList<>();
        rows.add("parent_metabolism,parent_vision,seed,tick,population,sugar0,spice0,sugar1,spice1,metabolism_sugar1,metabolism_spice1,vision1,distance1,wealth1");
        HeadlessWorkspace workspace = HeadlessWorkspace.newInstance();
        try {
            workspace.open(args[0], true);
            for (int mode = 0; mode < 2; mode++) {
                int metabolism = mode == 0 ? 1 : 4;
                int vision = mode == 0 ? 6 : 0;
                for (int seed = 1; seed <= 16; seed++) {
                    workspace.command("clear-all random-seed " + seed + " set initial-population 0 "
                        + "set minimum-sugar-endowment 1 set maximum-sugar-endowment 10 "
                        + "set minimum-spice-endowment 1 set maximum-spice-endowment 10 "
                        + "set wealth-reproduction 5 set pmut 1 set trade? true setup "
                        + "ask patches [set max-psugar 0 set max-pspice 0 set psugar 0 set pspice 0] "
                        + "create-turtles 1 [turtle-setup setxy 25 25 set sugar 20 set spice 20 "
                        + "set sugar-metabolism " + metabolism + " set spice-metabolism " + metabolism
                        + " set vision " + vision + " set vision-points [] set wealth 20] go");
                    String row = metabolism + "," + vision + "," + seed;
                    for (String reporter : new String[]{"ticks", "count turtles", "[sugar] of turtle 0",
                            "[spice] of turtle 0", "[sugar] of turtle 1", "[spice] of turtle 1",
                            "[sugar-metabolism] of turtle 1", "[spice-metabolism] of turtle 1", "[vision] of turtle 1",
                            "[distance turtle 0] of turtle 1", "[wealth] of turtle 1"}) {
                        row += "," + workspace.report(reporter);
                    }
                    rows.add(row);
                }
            }
        } finally {
            workspace.dispose();
        }
        Files.write(output.resolve("mutations.csv"), rows);
    }
}
