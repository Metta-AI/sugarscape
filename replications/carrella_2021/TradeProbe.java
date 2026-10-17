import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import org.nlogo.headless.HeadlessWorkspace;

/** Complete native ticks exercising both trade-price branches and cached rejection. */
public class TradeProbe {
    public static void main(String[] args) throws Exception {
        if (args.length != 2) throw new IllegalArgumentException("Usage: TradeProbe model new-output");
        Path output = Files.createDirectory(Path.of(args[1]));
        List<String> rows = new ArrayList<>();
        rows.add("case,tick,population,sugar0,spice0,wealth0,sugar1,spice1,wealth1,trades,mean_price");
        HeadlessWorkspace workspace = HeadlessWorkspace.newInstance();
        try {
            workspace.open(args[0], true);
            int[][] cases = {{10, 40, 40, 40, 1}, {40, 10, 40, 40, 1},
                             {10, 40, 40, 10, 1}, {10, 40, 40, 40, 1000}};
            for (int index = 0; index < cases.length; index++) {
                int[] c = cases[index];
                workspace.command("clear-all random-seed 123 set initial-population 0 "
                    + "set minimum-sugar-endowment 1 set maximum-sugar-endowment 10 "
                    + "set minimum-spice-endowment 1 set maximum-spice-endowment 10 "
                    + "set wealth-reproduction 2000 set pmut 0 set trade? true setup "
                    + "ask patches [set max-psugar 0 set max-pspice 0 set psugar 0 set pspice 0] "
                    + "create-turtles 2 [turtle-setup setxy (25 + who) 25 "
                    + "set sugar-metabolism 1 set spice-metabolism 1 set vision 1 "
                    + "set vision-points [[0 1] [1 0] [0 -1] [-1 0]] set wealth " + c[4] + "] "
                    + "ask turtle 0 [set sugar " + c[0] + " set spice " + c[1] + "] "
                    + "ask turtle 1 [set sugar " + c[2] + " set spice " + c[3] + "] "
                    + "set prices [] set mean_prices 7 go");
                String row = Integer.toString(index);
                for (String reporter : new String[]{"ticks", "count turtles", "[sugar] of turtle 0",
                        "[spice] of turtle 0", "[wealth] of turtle 0", "[sugar] of turtle 1",
                        "[spice] of turtle 1", "[wealth] of turtle 1", "number_of_prices", "mean_prices"}) {
                    row += "," + workspace.report(reporter);
                }
                rows.add(row);
            }
        } finally {
            workspace.dispose();
        }
        Files.write(output.resolve("trades.csv"), rows);
    }
}
