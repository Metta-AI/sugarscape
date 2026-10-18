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
        BufferedWriter initial = Files.newBufferedWriter(output.resolve("initial-agents.csv"));
        BufferedWriter patches = Files.newBufferedWriter(output.resolve("initial-patches.csv"));
        try {
            workspace.open(model.toString());
            states.write("seed,phase,clipped,step,population,total_tax,debt_refund,state_sha256\n");
            events.write("seed,phase,clipped,step,agent,vision,metabolism,capacity,cycle,policy_index,rate,before,paid,after\n");
            initial.write("seed,phase,clipped,agent,x,y,sugar,metabolism,vision,original_vision,vision_point_count\n");
            patches.write("seed,phase,clipped,x,y,capacity,sugar\n");
            for (int seed = 1; seed <= seeds; seed++) {
                for (int phase : new int[]{0, 4}) {
                    for (boolean clipped : new boolean[]{false, true}) {
                        workspace.command("setup-experiment " + seed + " [" + String.join(" ", rates) + "] " + phase + " " + clipped);
                        int width = ((Number) workspace.report("world-width")).intValue();
                        if (!Boolean.TRUE.equals(workspace.report("member? world-width [5 10 20 30 40 50] and world-width = world-height and min-pxcor = 0 and min-pycor = 0 and ([distance patch (world-width - 1) 0] of patch 0 0) = 1 and ([distance patch 0 (world-height - 1)] of patch 0 0) = 1")))
                            throw new IllegalStateException("Expected declared square torus");
                        String originalVision = width == 50 ? "vision" : "original-vision";
                        for (Object entry : (LogoList) workspace.report("map [(list [who] of ? [xcor] of ? [ycor] of ? [sugar] of ? [metabolism] of ? [vision] of ? [" + originalVision + "] of ? [length vision-points] of ?)] sort turtles")) {
                            initial.write(seed + "," + phase + "," + clipped);
                            for (Object value : (LogoList) entry) initial.write("," + value);
                            initial.write("\n");
                        }
                        for (Object entry : (LogoList) workspace.report("map [(list [pxcor] of ? [pycor] of ? [max-psugar] of ? [psugar] of ?)] sort patches")) {
                            patches.write(seed + "," + phase + "," + clipped);
                            for (Object value : (LogoList) entry) patches.write("," + value);
                            patches.write("\n");
                        }
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
            initial.close();
            patches.close();
            ((org.nlogo.job.JobManager) workspace.jobManager).die();
        }
    }
}
