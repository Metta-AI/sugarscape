import ec.util.ParameterDatabase;
import ec.util.Parameter;
import sim.app.sugarscape.Sugarscape;
import java.io.File;

public class Replay {
    public static void main(String[] args) throws Exception {
        ParameterDatabase parameters = new ParameterDatabase(new File(args[0]));
        parameters.set(new Parameter("chart_display"), "false");
        Sugarscape model = new Sugarscape(parameters, Long.parseLong(args[1]), 1);
        model.start();
        int steps = Integer.parseInt(args[2]);
        while (model.schedule.time() < steps) {
            if (!model.schedule.step(model)) throw new IllegalStateException("Schedule ended early");
        }
        model.stopLogging();
        model.finish();
    }
}
