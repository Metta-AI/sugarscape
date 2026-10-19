import java.nio.file.*;
import java.util.*;
import org.nlogo.headless.HeadlessWorkspace;
public class VisionProbe {
 public static void main(String[] args) throws Exception {
  HeadlessWorkspace w=HeadlessWorkspace.newInstance();
  List<String> rows=new ArrayList<>();
  rows.add("vision,offset,vision_points,tick,x,y,sugar,spice");
  try {
   w.open(args[0],true);
   for(int v:new int[]{-3,-1,0,1,2,6}) for(int offset:new int[]{1,2}) {
    w.command("clear-all random-seed 0 set initial-population 0 set minimum-sugar-endowment 1 set maximum-sugar-endowment 10 set minimum-spice-endowment 1 set maximum-spice-endowment 10 set wealth-reproduction 100000 set pmut 0 set trade? true setup ask patches [set max-psugar 0 set max-pspice 0 set psugar 0 set pspice 0] ask patch "+(25+offset)+" 25 [set max-psugar 4 set max-pspice 4 set psugar 4 set pspice 4] create-turtles 1 [turtle-setup setxy 25 25 set sugar 10 set spice 10 set sugar-metabolism 1 set spice-metabolism 1 set vision "+v+" set vision-points [] foreach (range 1 (vision + 1)) [n -> set vision-points sentence vision-points (list (list 0 n) (list n 0) (list 0 (- n)) (list (- n) 0))] set wealth wealth-func sugar spice sugar-metabolism spice-metabolism] go");
    String row=v+","+offset;
    for(String s:new String[]{"[length vision-points] of turtle 0","ticks","[xcor] of turtle 0","[ycor] of turtle 0","[sugar] of turtle 0","[spice] of turtle 0"})row+=","+w.report(s);
    rows.add(row);
   }
  } finally {w.dispose();}
  Files.write(Path.of(args[1]),rows);
 }
}
