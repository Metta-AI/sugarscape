import ec.util.ParameterDatabase;
import ec.util.Parameter;
import sim.app.sugarscape.Agent;
import sim.app.sugarscape.Sugarscape;
import java.io.File;
import java.io.PrintWriter;

public class AuditReplay {
    private static void snapshot(Sugarscape model, PrintWriter output) {
        int gridAlive = 0;
        for (Object[] column : model.agents_grid.field) {
            for (Object value : column) {
                if (value instanceof Agent && ((Agent) value).alive) gridAlive++;
            }
        }
        int registeredAlive = 0;
        for (Agent agent : model.active_agents) if (agent.alive) registeredAlive++;
        output.println((model.schedule.time() + 1) + "," + model.active_agents_count + ","
            + gridAlive + "," + model.active_agents.size() + "," + registeredAlive);
    }

    public static void main(String[] args) throws Exception {
        ParameterDatabase parameters = new ParameterDatabase(new File(args[0]));
        parameters.set(new Parameter("chart_display"), "false");
        Sugarscape model = new Sugarscape(parameters, Long.parseLong(args[1]), 1);
        model.start();
        int steps = Integer.parseInt(args[2]);
        try (PrintWriter output = new PrintWriter(new File(args[3]))) {
            output.println("time,reported_population,grid_alive,registered,registered_alive");
            snapshot(model, output);
            while (model.schedule.time() < steps) {
                if (!model.schedule.step(model)) throw new IllegalStateException("Schedule ended early");
                snapshot(model, output);
            }
        }
        model.stopLogging();
        model.finish();
    }
}
