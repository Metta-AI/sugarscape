import java.io.BufferedWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.MessageDigest;
import org.nlogo.headless.HeadlessWorkspace;

/** Run complete paired workflows through NetLogo's public headless interface. */
public class RunEnsemble {
    public static void main(String[] args) throws Exception {
        Path model = Paths.get(args[0]).toAbsolutePath();
        Path output = Paths.get(args[1]);
        int seeds = Integer.parseInt(args[2]);
        if (seeds < 1 || seeds > 100) throw new IllegalArgumentException("Seeds must be 1..100");
        Files.createDirectory(output);
        HeadlessWorkspace workspace = HeadlessWorkspace.newInstance();
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        BufferedWriter stream = Files.newBufferedWriter(output.resolve("trajectory.csv"));
        try {
            workspace.open(model.toString());
            stream.write("seed,rate,phase,clipped,step,population,total_tax,debt_refund,state_sha256\n");
            for (int seed = 1; seed <= seeds; seed++) {
                for (double rate : new double[]{0, 0.25, 0.5, 0.75}) {
                    for (int phase : new int[]{0, 4}) {
                        for (boolean clipped : new boolean[]{false, true}) {
                            workspace.command("setup-experiment " + seed + " (n-values 200 [" + rate + "]) " + phase + " " + clipped);
                            for (int step = 0; step <= 50; step++) {
                                String state = workspace.report("survivor-state").toString();
                                byte[] hash = digest.digest(state.getBytes(StandardCharsets.UTF_8));
                                StringBuilder hex = new StringBuilder();
                                for (byte value : hash) hex.append(String.format("%02x", value & 255));
                                stream.write(seed + "," + rate + "," + phase + "," + clipped + "," + step + ","
                                    + workspace.report("count turtles") + "," + workspace.report("total-tax") + ","
                                    + workspace.report("debt-refund") + "," + hex + "\n");
                                if (step < 50) workspace.command("go");
                            }
                            stream.flush();
                        }
                    }
                }
                System.out.println("Completed seed " + seed + " of " + seeds);
            }
        } finally {
            stream.close();
            ((org.nlogo.job.JobManager) workspace.jobManager).die();
        }
    }
}
