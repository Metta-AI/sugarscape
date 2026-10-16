import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import org.nlogo.headless.HeadlessWorkspace;

/** Controlled complete native ticks identifying cached-wealth and price semantics. */
public class SemanticsProbe {
    public static void main(String[] args) throws Exception {
        if (args.length != 2) throw new IllegalArgumentException("Usage: SemanticsProbe model new-output");
        Path output = Files.createDirectory(Path.of(args[1]));
        List<String> rows = new ArrayList<>();
        rows.add("case,tick,population,total_sugar,total_spice,total_utility,trade_count,mean_price");
        HeadlessWorkspace workspace = HeadlessWorkspace.newInstance();
        try {
            workspace.open(args[0], true);
            for (int cached : new int[]{1, 10}) {
                workspace.command("clear-all random-seed 123 set initial-population 0 "
                    + "set minimum-sugar-endowment 1 set maximum-sugar-endowment 10 "
                    + "set minimum-spice-endowment 1 set maximum-spice-endowment 10 "
                    + "set wealth-reproduction 5 set pmut 0 set trade? true setup "
                    + "ask patches [set max-psugar 0 set max-pspice 0 set psugar 0 set pspice 0] "
                    + "create-turtles 1 [turtle-setup setxy 25 25 set sugar 10 set spice 10 "
                    + "set sugar-metabolism 1 set spice-metabolism 1 set vision 1 "
                    + "set vision-points [[0 1] [1 0] [0 -1] [-1 0]] set wealth " + cached + "] "
                    + "set prices [] set mean_prices 7");
                workspace.command("go");
                double population = ((Number) workspace.report("count turtles")).doubleValue();
                double expectedPopulation = cached == 1 ? 1 : 2;
                if (population != expectedPopulation) throw new IllegalStateException("Cached wealth reproduction differs");
                for (String commodity : new String[]{"sugar", "spice"}) {
                    double amount = ((Number) workspace.report("sum [" + commodity + "] of turtles")).doubleValue();
                    if (amount != 9) throw new IllegalStateException("Native reproduction did not conserve holdings");
                }
                double price = ((Number) workspace.report("mean_prices")).doubleValue();
                if (price != 7) throw new IllegalStateException("No-trade price did not persist");
                String row = "cached-" + cached;
                for (String reporter : new String[]{"ticks", "count turtles", "sum [sugar] of turtles",
                        "sum [spice] of turtles", "sum [wealth] of turtles", "number_of_prices", "mean_prices"}) {
                    row += "," + workspace.report(reporter);
                }
                rows.add(row);
            }
        } finally {
            workspace.dispose();
        }
        Files.write(output.resolve("results.csv"), rows);
    }
}
