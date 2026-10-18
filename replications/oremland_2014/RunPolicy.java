import java.io.BufferedWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.MessageDigest;
import java.util.List;
import org.nlogo.api.LogoList;
import org.nlogo.headless.HeadlessWorkspace;

/** Record complete heterogeneous-policy workflows and every native tax event. */
public class RunPolicy {
    public static void main(String[] args) throws Exception {
        Path model = Paths.get(args[0]).toAbsolutePath();
        List<String> rates = Files.readAllLines(Paths.get(args[1]));
        if (rates.size() != 200) throw new IllegalArgumentException("Expected 200 policy entries");
        for (String rate : rates) {
            double value = Double.parseDouble(rate);
            if (!(value == 0 || value == 0.25 || value == 0.5 || value == 0.75))
                throw new IllegalArgumentException("Invalid tax rate");
        }
        Path output = Paths.get(args[2]);
        int seeds = Integer.parseInt(args[3]);
        if (seeds < 1 || seeds > 100) throw new IllegalArgumentException("Seeds must be 1..100");
        Files.createDirectory(output);
        HeadlessWorkspace workspace = HeadlessWorkspace.newInstance();
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        BufferedWriter states = Files.newBufferedWriter(output.resolve("trajectory.csv"));
        BufferedWriter events = Files.newBufferedWriter(output.resolve("tax-events.csv"));
        try {
            workspace.open(model.toString());
            states.write("seed,phase,clipped,step,population,total_tax,debt_refund,state_sha256\n");
            events.write("seed,phase,clipped,step,agent,vision,metabolism,capacity,cycle,policy_index,rate,before,paid,after\n");
            for (int seed = 1; seed <= seeds; seed++) {
                for (int phase : new int[]{0, 4}) {
                    for (boolean clipped : new boolean[]{false, true}) {
                        workspace.command("setup-experiment " + seed + " [" + String.join(" ", rates) + "] " + phase + " " + clipped);
                        if (!Boolean.TRUE.equals(workspace.report("world-width = 50 and world-height = 50 and ([distance patch 49 0] of patch 0 0) = 1 and ([distance patch 0 49] of patch 0 0) = 1")))
                            throw new IllegalStateException("Expected 50x50 torus");
                        for (int step = 0; step <= 50; step++) {
                            byte[] hash = digest.digest(workspace.report("survivor-state").toString().getBytes(StandardCharsets.UTF_8));
                            StringBuilder hex = new StringBuilder();
                            for (byte value : hash) hex.append(String.format("%02x", value & 255));
                            states.write(seed + "," + phase + "," + clipped + "," + step + ","
                                + workspace.report("count turtles") + "," + workspace.report("total-tax") + ","
                                + workspace.report("debt-refund") + "," + hex + "\n");
                            for (Object entry : (LogoList) workspace.report("tax-events")) {
                                events.write(seed + "," + phase + "," + clipped + "," + step);
                                for (Object value : (LogoList) entry) events.write("," + value);
                                events.write("\n");
                            }
                            if (step < 50) workspace.command("go");
                        }
                        states.flush();
                        events.flush();
                    }
                }
                System.out.println("Completed policy seed " + seed + " of " + seeds);
            }
        } finally {
            states.close();
            events.close();
            ((org.nlogo.job.JobManager) workspace.jobManager).die();
        }
    }
}
