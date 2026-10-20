import java.nio.file.*;
import java.io.*;
import org.nlogo.headless.HeadlessWorkspace;
public class AuditDeathBoundary {
    public static void main(String[] args) throws Exception {
        try (BufferedWriter out = Files.newBufferedWriter(Paths.get(args[2]), StandardOpenOption.CREATE_NEW)) {
            out.write("model,phase,clipped,step,population,zero_sugar,negative_sugar,total_tax\n");
            for (int model=0; model<2; model++) {
                HeadlessWorkspace w = HeadlessWorkspace.newInstance();
                try {
                w.open(args[model]);
                w.plotManager().forgetAll();
                for (int phase : new int[]{0,4}) for (boolean clipped : new boolean[]{false,true}) {
                    w.command("setup-experiment 1 (n-values 200 [0]) " + phase + " " + clipped);
                    for (int t=0; t<=50; t++) {
                        out.write(model+","+phase+","+clipped+","+t+","+w.report("count turtles")+","+w.report("count turtles with [sugar = 0]")+","+w.report("count turtles with [sugar < 0]")+","+w.report("total-tax")+"\n");
                        if(t<50) w.command("go");
                    }
                }
                } finally { ((org.nlogo.job.JobManager)w.jobManager).die(); }
            }
        }
    }
}
