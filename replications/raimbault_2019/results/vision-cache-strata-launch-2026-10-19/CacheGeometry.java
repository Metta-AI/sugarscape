import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import org.nlogo.headless.HeadlessWorkspace;

public class CacheGeometry {
    public static void main(String[] args) throws Exception {
        if (args.length != 3) throw new IllegalArgumentException("model setup-command output-csv");
        HeadlessWorkspace workspace = HeadlessWorkspace.newInstance();
        try {
            workspace.open(args[0]);
            workspace.command(Files.readString(Path.of(args[1])));
            if ((Double) workspace.report("count patches") != 2500.0) throw new IllegalStateException("Wrong patch count");
            StringBuilder offsets = new StringBuilder();
            StringBuilder result = new StringBuilder("radius,patches,incorrect_sets\n");
            for (int radius = 1; radius <= 6; radius++) {
                offsets.append("[0 ").append(radius).append("] [").append(radius).append(" 0] [0 -")
                       .append(radius).append("] [-").append(radius).append(" 0] ");
                String reporter = "count patches with [(sort (item " + (radius - 1)
                    + " fixed-vision-sets)) != (sort (patches at-points [" + offsets + "]))]";
                double wrong = (Double) workspace.report(reporter);
                if (wrong != 0.0) throw new IllegalStateException("Geometry differs at radius " + radius);
                result.append(radius).append(",2500,0\n");
            }
            Files.writeString(Path.of(args[2]), result, StandardOpenOption.CREATE_NEW);
        } finally {
            workspace.dispose();
        }
    }
}
