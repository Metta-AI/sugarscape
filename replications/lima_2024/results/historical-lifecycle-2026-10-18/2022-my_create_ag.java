package mylib;

import jason.*;
import jason.runtime.*;
import jason.asSemantics.*;
import jason.asSyntax.*;

import java.nio.file.Path;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.io.*;
import java.util.List;

// FUNCIONAVA SÓ LENDO, AGORA QUERO ESCREVER
// import java.nio.charset.StandardCharsets;

import java.nio.charset.StandardCharsets;
import java.nio.file.StandardOpenOption;


// SÓ PRO RANDOM NO NOME, SE NÃO USAR, TIRAR
import java.util.Random;

//import java.io.File;








// PRO DB
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

import java.util.ArrayList;

import java.util.*;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Map;
import javax.script.ScriptEngine;
import javax.script.ScriptEngineManager;
import javax.script.ScriptException;

// import java.util.regex.Pattern;
// import java.util.regex.Matcher;

// import javax.json.Json;
// import javax.json.JsonObject;
// import javax.json.JsonReader;

// import javax.json.JsonArray;
// import javax.json.JsonValue;

// import com.google.gson.Gson;

// import org.python.util.PythonInterpreter;

// https://smartbear.com/blog/embedding-jython-in-java-applications/

// import org.python.util.PythonInterpreter;
// import org.python.core.*;

import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Scanner;


//import org.json.*;


import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
// https://medium.com/swlh/getting-json-data-from-a-restful-api-using-java-b327aafb3751



import java.util.stream.Stream;

public class my_create_ag extends DefaultInternalAction {

    @Override
    public Object execute(TransitionSystem ts, Unifier un, Term[] args) throws Exception {

        boolean using_docker = true;
        String host = "";

        if (using_docker){
            host = "api";
        } else {
            host = "localhost";
        }

        //String version = Runtime.class.getPackage().getImplementationVersion();

        /*
        System.out.println("Executing JAVA custom code - create");        
        String version = Runtime.version().toString();
        System.out.println("Version: "+version);
        */

        RuntimeServices rs = RuntimeServicesFactory.get();

        Collection<String> names = rs.getAgentsNames();
        System.out.println("All agents at the moment:");
        System.out.println(names);

        String y[] = names.toArray(new String[names.size()]);

        // if (names.size() > 2){
        // }

        // for(String agent : y) {
        //     System.out.println(agent);
        // }

        // Boolean has_df = false;
        // List valid = Arrays.asList(y);
        // if (valid.contains("df")) {
        //     has_df = true
        // }

        Boolean has_df = (Arrays.asList(y)).contains("df");

        //System.out.println("has df? "+(Arrays.asList(y)).contains("df"));
        //System.out.println("has killer_agent? "+(Arrays.asList(y)).contains("killer_agent"));

        //System.out.println("has df? "+has_df);

        // List valid = Arrays.asList(y);
        // if (valid.contains("df")) {
        //     has_df = true
        // }

        //30.05.22 - Teste, funciona, testando se da pra não se importar com o df
        //if (!has_df && names.size() == 3) {
        if ((!has_df && names.size() == 3) || (has_df && names.size() == 4)) {
            System.out.println("3 agents and no df, checking if there is a new agent on API to be created...");

            try {
                URL url = new URL("http://"+host+":5000/api/v1/resources/check_new_agents_1?model=m3");
                String inline = "";
                Scanner scanner = new Scanner(url.openStream());

                //Write all the JSON data into a string using a scanner
                while (scanner.hasNext()) {
                    inline += scanner.nextLine();
                }

                //Close the scanner
                scanner.close();

                //System.out.println("Inline: "+ inline.toString());

                //Using the JSON simple library parse the string into a json object
                JSONParser parse = new JSONParser();

                JSONParser parser = new JSONParser();
                JSONArray arr  = (JSONArray) parser.parse(inline);  

                //System.out.println("Size: "+ arr.size());

                if (arr.size() > 0){
                    System.out.println("New agents");
                    for (int i = 0; i < arr.size(); i++) {
                        JSONArray arr2  = (JSONArray) arr.get(i);

                        String agent_id = arr2.get(0).toString();
                        String agent_stats = arr2.get(1).toString();
                        String agent_path = arr2.get(2).toString();

                        System.out.println("ID: " + agent_id);
                        System.out.println("Stats: " + agent_stats);
                        System.out.println("Path: " + agent_path);

                        JSONParser parser2 = new JSONParser();
                        JSONArray arr3  = (JSONArray) parser2.parse(arr2.get(1).toString());

                        String sugar = arr3.get(0).toString();
                        String metabolism = arr3.get(1).toString();
                        String vision = arr3.get(2).toString();

                        System.out.println("Sugar: " + sugar);
                        System.out.println("Metabolism: " + metabolism);
                        System.out.println("Vision: " + vision);

                        Settings s = new Settings();

                        char ch='"';
                        String bels = "agent_id("+agent_id+")";
                        bels = bels + ",path("+ ch + agent_path + ch + ")";
                        bels = bels + ", sugar("+sugar+"), metabolism("+metabolism+"), vision("+vision+")";
                        System.out.println("Vai criar o agente com os beliefs: "+bels);

                        s.addOption(Settings.INIT_BELS, bels);
                        //s.addOption(Settings.INIT_GOALS, "a");
                        s.addOption(Settings.INIT_GOALS, "jcm::focus_env_art([art_env(mining,m2view,default)],5)");


                        try {
                            String asl_file_name = "list/"+agent_id+".asl";

                            if (!Files.exists(Paths.get("src/agt/"+asl_file_name))){
                                //asl_file_name = "regular_agent.asl";
                                asl_file_name = "miner3.asl";
                            }

                            System.out.println("asl_file_name: "+asl_file_name);

                            rs.createAgent(agent_id, asl_file_name, null, null, null, s, ts.getAg());
                            rs.startAgent(agent_id);
                            System.out.println("Agent created by custom file");
                        } catch (Exception e) {
                            e.printStackTrace();
                        }
                    } 
                } else {
                    //System.out.println("No agents to join");
                }

            } catch (Exception e) {
                e.printStackTrace();
            }
        }

        // try {
        //     System.out.println("Print 1");
        //     URL url = new URL("http://localhost:5000/api/v1/resources/check_new_agents?model=m3");

        //     HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        //     conn.setRequestMethod("GET");
        //     conn.connect();

        //     //Getting the response code
        //     int responsecode = conn.getResponseCode();

        //     if (responsecode != 200) {
        //         throw new RuntimeException("HttpResponseCode: " + responsecode);
        //     } else {
        //         String inline = "";
        //         Scanner scanner = new Scanner(url.openStream());

        //         //Write all the JSON data into a string using a scanner
        //         while (scanner.hasNext()) {
        //             inline += scanner.nextLine();
        //         }

        //         //Close the scanner
        //         scanner.close();

        //         System.out.println("Inline: "+ inline.toString());

        //         //Using the JSON simple library parse the string into a json object
        //         JSONParser parse = new JSONParser();

        //         JSONParser parser = new JSONParser();
        //         JSONArray arr  = (JSONArray) parser.parse(inline);  

        //         System.out.println("Size: "+ arr.size());

        //         if (arr.size() > 0){
        //             System.out.println("New agents");
        //             for (int i = 0; i < arr.size(); i++) {
        //                 JSONArray arr2  = (JSONArray) arr.get(i);

        //                 String agent_id = arr2.get(0).toString();
        //                 String agent_stats = arr2.get(1).toString();
        //                 String agent_path = arr2.get(2).toString();

        //                 System.out.println("ID: " + agent_id);
        //                 System.out.println("Stats: " + agent_stats);
        //                 System.out.println("Path: " + agent_path);

        //                 JSONParser parser2 = new JSONParser();
        //                 JSONArray arr3  = (JSONArray) parser2.parse(arr2.get(1).toString());

        //                 String sugar = arr3.get(0).toString();
        //                 String metabolism = arr3.get(1).toString();
        //                 String vision = arr3.get(2).toString();

        //                 System.out.println("Sugar: " + sugar);
        //                 System.out.println("Metabolism: " + metabolism);
        //                 System.out.println("Vision: " + vision);

        //                 // System.out.println("Att0: " + arr3.get(0));
        //                 // System.out.println("Att1: " + arr3.get(1));
        //                 // System.out.println("Att2: " + arr3.get(2));

        //                 Settings s = new Settings();

        //                 char ch='"';
        //                 // String bels = "agent_id(" + ch + agent_id + ch + ")";
        //                 // bels = bels + ",path("+ ch + agent_path + ch + ")";
        //                 String bels = "agent_id("+agent_id+")";
        //                 bels = bels + ",path("+ ch + agent_path + ch + ")";
        //                 bels = bels + ", sugar("+sugar+"), metabolism("+metabolism+"), vision("+vision+")";
        //                 System.out.println("Vai criar o agente com os beliefs: "+bels);

        //                 s.addOption(Settings.INIT_BELS, bels);
        //                 s.addOption(Settings.INIT_GOALS, "a");


        //                 try {
        //                     String asl_file_name = "list/"+agent_id+".asl";

        //                     if (!Files.exists(Paths.get("src/agt/"+asl_file_name))){
        //                         // asl_file_name = "regular_agent.asl";
        //                         asl_file_name = "regular_agent.asl";
        //                     }

        //                     System.out.println("asl_file_name: "+asl_file_name);

        //                     rs.createAgent(agent_id, asl_file_name, null, null, null, s, ts.getAg());
        //                     rs.startAgent(agent_id);
        //                     System.out.println("Agent created by custom file");
        //                 } catch (Exception e) {
        //                     e.printStackTrace();
        //                 }
        //             } 
        //         } else {
        //             System.out.println("No agents to join");
        //         }
        //     }

        // } catch (Exception e) {
        //     e.printStackTrace();
        // }

        // try {
        //     System.out.println("Print 1");
        //     URL url = new URL("http://localhost:5000/api/v1/resources/check_new_agents?model=m3");

        //     HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        //     conn.setRequestMethod("GET");
        //     conn.connect();

        //     //Getting the response code
        //     int responsecode = conn.getResponseCode();

        //     if (responsecode != 200) {
        //         throw new RuntimeException("HttpResponseCode: " + responsecode);
        //     } else {

        //         String inline = "";
        //         Scanner scanner = new Scanner(url.openStream());

        //         //Write all the JSON data into a string using a scanner
        //         while (scanner.hasNext()) {
        //             inline += scanner.nextLine();
        //         }

        //         //Close the scanner
        //         scanner.close();

        //         System.out.println("Inline: "+ inline.toString());

        //         //Using the JSON simple library parse the string into a json object
        //         JSONParser parse = new JSONParser();

        //         JSONParser parser = new JSONParser();
        //         JSONArray arr  = (JSONArray) parser.parse(inline);  

        //         System.out.println("Size: "+ arr.size());

        //         if (arr.size() > 0){
        //             System.out.println("New agents");
        //             for (int i = 0; i < arr.size(); i++) {
        //                 JSONArray arr2  = (JSONArray) arr.get(i);

        //                 String agent_id = arr2.get(0).toString();
        //                 String agent_stats = arr2.get(1).toString();
        //                 String agent_path = arr2.get(2).toString();

        //                 System.out.println("ID: " + agent_id);
        //                 System.out.println("Stats: " + agent_stats);
        //                 System.out.println("Path: " + agent_path);

        //                 JSONParser parser2 = new JSONParser();
        //                 JSONArray arr3  = (JSONArray) parser2.parse(arr2.get(1).toString());

        //                 String sugar = arr3.get(0).toString();
        //                 String metabolism = arr3.get(1).toString();
        //                 String vision = arr3.get(2).toString();

        //                 System.out.println("Sugar: " + sugar);
        //                 System.out.println("Metabolism: " + metabolism);
        //                 System.out.println("Vision: " + vision);

        //                 // System.out.println("Att0: " + arr3.get(0));
        //                 // System.out.println("Att1: " + arr3.get(1));
        //                 // System.out.println("Att2: " + arr3.get(2));

        //                 Settings s = new Settings();

        //                 char ch='"';
        //                 // String bels = "agent_id(" + ch + agent_id + ch + ")";
        //                 // bels = bels + ",path("+ ch + agent_path + ch + ")";
        //                 String bels = "agent_id("+agent_id+")";
        //                 bels = bels + ",path("+ ch + agent_path + ch + ")";
        //                 bels = bels + ", sugar("+sugar+"), metabolism("+metabolism+"), vision("+vision+")";
        //                 System.out.println("Vai criar o agente com os beliefs: "+bels);

        //                 s.addOption(Settings.INIT_BELS, bels);
        //                 s.addOption(Settings.INIT_GOALS, "a");


        //                 try {
        //                     String asl_file_name = "list/"+agent_id+".asl";

        //                     if (!Files.exists(Paths.get("src/agt/"+asl_file_name))){
        //                         // asl_file_name = "regular_agent.asl";
        //                         asl_file_name = "regular_agent.asl";
        //                     }

        //                     System.out.println("asl_file_name: "+asl_file_name);

        //                     rs.createAgent(agent_id, asl_file_name, null, null, null, s, ts.getAg());
        //                     rs.startAgent(agent_id);
        //                     System.out.println("Agent created by custom file");
        //                 } catch (Exception e) {
        //                     e.printStackTrace();
        //                 }
        //             } 
        //         } else {
        //             System.out.println("No agents to join");
        //         }
        //     }

        // } catch (Exception e) {
        //     e.printStackTrace();
        // }

        // if (Files.exists(Paths.get(path)) && Files.size(Paths.get(path)) >= 0) {            
        //     // RuntimeServices provides services to create agents in the current platform (Local, JADE, JaCaMo, ...)
        //     RuntimeServices rs = RuntimeServicesFactory.get();

        //     String fileName = path;
        //     File file = new File(fileName);

        //     try (Stream linesStream = Files.lines(file.toPath())) {
        //         linesStream.forEach(line2 -> {
        //             String name = "";
        //             String aehoo = String.valueOf(line2);

        //             System.out.println("Linha: "+aehoo);

        //             String[] splitStr = aehoo.split("\\s+");

        //             System.out.println("ID do agente: "+splitStr[1]);

        //             // use Settings to add initial beliefs and goals for the new agent
        //             // (as used in the .mas2j project file)
        //             Settings s = new Settings();
        //             // String bels = "+other_models("+aehoo+")";

        //             String platform_string = "";
        //             String escape_agent = splitStr[0].replace("\"", "").replace("[", "");
        //             String escape_path = splitStr[5].replace("\"", "").replace("]", "");
        //             // platform_string = "\"" + escape_agent + "\"" + " " + splitStr[1] + " " + splitStr[2] + " " + splitStr[3] + " " + splitStr[4] + " " + "\"" + escape_path + "\"";
        //             // platform_string = escape_agent + " " + splitStr[1] + " " + splitStr[2] + " " + splitStr[3] + " " + splitStr[4] + " " + escape_path;
        //             // String bels = "platform_string("+platform_string+")";
        //             char ch='"';
        //             // FUNCIONA
        //             // String bels = "b("+ ch + "aehoo aehii" + ch + ")";
        //             // FUNCIONA
        //             // String bels = "b("+ ch + escape_agent + " " + splitStr[1] + " " + splitStr[2] + " " + splitStr[3] + " " + splitStr[4] + " " + escape_path + ch + ")";

        //             // FUNCIONA QUASE 100%, FALTA ASPAS NO FIM DE AGENT E NO INICIO DO PATH
        //             // String bels = "b(["+ ch + escape_agent + " " + splitStr[1] + " " + splitStr[2] + " " + splitStr[3] + " " + splitStr[4] + " " + escape_path + ch + "])";


        //             // PARTINDO EM VARIAS STRINGS
        //             // String bels = "previous_0(" + ch + escape_agent + ch + ")";
        //             // bels = bels + ",previous_1("+ splitStr[1] + ")";
        //             // bels = bels + ",previous_2("+ splitStr[2] + ")";
        //             // bels = bels + ",previous_3("+ splitStr[3] + ")";
        //             // bels = bels + ",previous_4("+ splitStr[4] + ")";
        //             // bels = bels + ",previous_5(" + ch + escape_path + ch + ")";

        //             // PARTINDO SÓ EM 3
        //             String bels = "previous_0(" + ch + escape_agent + ch + ")";

        //             // 10/03/22 - FUNCIONA GERANDO COISAS RANDOM PRA CONFIRMAR SE ESTA INDO CERTO
        //             // Random rand = new Random();
        //             // int randomNum2 = rand.nextInt((20 - 0) + 1) + 0;
        //             // int randomNum3 = rand.nextInt((10 - 0) + 1) + 0;
        //             // int randomNum4 = rand.nextInt((5 - 0) + 1) + 0;
        //             // bels = bels + ",previous_1("+ ch + splitStr[1] + " " + randomNum2 + " " + randomNum3 + " " + randomNum4 + ch +  ")";
        //             // 10/03/22 - FUNCIONA PEGANDO DO ARQUIVO, TESTANDO PRA VER SE TA ATUALIZANDO A CRENÇA /\
        //             bels = bels + ",previous_1("+ ch + splitStr[1] + " " + splitStr[2] + " " + splitStr[3] + " " + splitStr[4] + ch +  ")";
        //             bels = bels + ",previous_2(" + ch + escape_path + ch + ")";

        //             bels = bels + ", sugar("+splitStr[2]+"), metabolism("+splitStr[3]+"), vision("+splitStr[4]+")";

        //             System.out.println("Vai criar o agente com os beliefs: "+bels);


        //             // String bels = "other_models("+splitStr[2]+splitStr[3]+splitStr[4]+")";

        //             //10.03 - JUNTANDO OS BELS EM 1 VARIAVEL SO
        //             // s.addOption(Settings.INIT_BELS, bels+ ", sugar("+splitStr[2]+"), metabolism("+splitStr[3]+"), vision("+splitStr[4]+")");
        //             s.addOption(Settings.INIT_BELS, bels);
        //             s.addOption(Settings.INIT_GOALS, "a");

        //             // // ANTES DE ADICIONAR CRENÇA DA STRING ANTERIOR DO AGENTE
        //             // // use Settings to add initial beliefs and goals for the new agent
        //             // // (as used in the .mas2j project file)
        //             // Settings s = new Settings();
        //             // String bels = "b1(10),b2(20)";
        //             // s.addOption(Settings.INIT_BELS, bels+ ", b3("+splitStr[2]+"), b4("+splitStr[3]+"), b5("+splitStr[4]+")");
        //             // s.addOption(Settings.INIT_GOALS, "a");

        //             try {
        //                 String asl_file_name = "list/"+splitStr[1]+".asl";

        //                 if (!Files.exists(Paths.get("src/agt/"+asl_file_name))){
        //                     asl_file_name = "regular_agent.asl";
        //                 }

        //                 System.out.println("asl_file_name: "+asl_file_name);

        //                 // rs.createAgent(splitStr[1], "regular_agent.asl", null, null, null, s, ts.getAg());
        //                 rs.createAgent(splitStr[1], asl_file_name, null, null, null, s, ts.getAg());
        //                 rs.startAgent(splitStr[1]);
        //                 System.out.println("Agent created by custom file");
        //             } catch (Exception e) {

        //             }
        //         });

        //         System.out.println("! Deleting After creating agents !");
        //         Files.delete(Paths.get(path));
        //         System.out.println("! Deleted !");
        //     }
        // }
        // else {
        //     System.out.println(path+" não existe");
        // }

        // everything ok, so returns true
        return true;
    }
}


// BACKUP ANTES DE JUNTAR COM A ESTRUTURA TODA, TA CRIANDO TODOS AGENTES DO ARQUIVO, 1 POR 1
// package mylib;

// import jason.*;
// import jason.runtime.*;
// import jason.asSemantics.*;
// import jason.asSyntax.*;

// import java.nio.file.Path;
// import java.nio.file.Files;
// import java.nio.file.Paths;
// import java.io.*;
// import java.util.List;

// // FUNCIONAVA SÓ LENDO, AGORA QUERO ESCREVER
// // import java.nio.charset.StandardCharsets;

// import java.nio.charset.StandardCharsets;
// import java.nio.file.StandardOpenOption;


// // SÓ PRO RANDOM NO NOME, SE NÃO USAR, TIRAR
// import java.util.Random;

// //import java.io.File;

// import java.util.stream.Stream;

// public class my_create_ag extends DefaultInternalAction {

//     @Override
//     public Object execute(TransitionSystem ts, Unifier un, Term[] args) throws Exception {

//         System.out.println("Executing JAVA custom code - create");

//         if (Files.exists(Paths.get("/teste/important/send_agent3.txt")) && Files.size(Paths.get("/teste/important/send_agent3.txt")) >= 0 ) {
//             System.out.println("existe e não vazio");
//         }
//         else {
//             System.out.println("não existe ou vazio");
//         }

//         if (Files.exists(Paths.get("/teste/important/data0.txt"))) {
//             System.out.println("/teste/important/data0.txt não existe");
//         }
//         else {
//             if (Files.exists(Paths.get("/teste/important/send_agent3.txt"))) {

//                 // RuntimeServices provides services to create agents in the current platform (Local, JADE, JaCaMo, ...)
//                 RuntimeServices rs = RuntimeServicesFactory.get();

//                 String fileName = "/teste/important/send_agent3.txt";
//                 File file = new File(fileName);

//                 try (Stream linesStream = Files.lines(file.toPath())) {
//                     linesStream.forEach(line2 -> {
//                         String name = "";
//                         String aehoo = String.valueOf(line2);

//                         System.out.println(aehoo);

//                         String[] splitStr = aehoo.split("\\s+");

//                         // use Settings to add initial beliefs and goals for the new agent
//                         // (as used in the .mas2j project file)
//                         Settings s = new Settings();
//                         String bels = "b(10),b(20)";
//                         s.addOption(Settings.INIT_BELS, bels+ ", b("+splitStr[2]+"), b("+splitStr[3]+"), b("+splitStr[4]+")");
//                         s.addOption(Settings.INIT_GOALS, "a");

//                         try {
//                             rs.createAgent(splitStr[1], "bob.asl", null, null, null, s, ts.getAg());
//                             rs.startAgent(splitStr[1]);
//                             System.out.println("Agent created by custom file");
//                         } catch (Exception e) {

//                         }
//                     });
//                 }

//                 // System.out.println("! Deleting After creating agents !");
//                 // Files.delete(Paths.get("/teste/important/send_agent3.txt"));
//                 // System.out.println("! Deleted !");
//             }
//             else {
//                 System.out.println("/teste/important/send_agent3.txt não existe");
//             }
//         }


//         // System.out.println("Writing...");

//         // Files.write(Paths.get("data2.txt"), "the text \n".getBytes(), StandardOpenOption.CREATE);
//         // Files.write(Paths.get("data2.txt"), "aehoo \n".getBytes(), StandardOpenOption.APPEND);

//         // System.out.println("Reading...");

//         // String fileName2 = "data2.txt";
//         // File file2 = new File(fileName2);

//         // byte [] fileBytes2 = Files.readAllBytes(file2.toPath());
//         // char singleChar2;
//         // for(byte b2 : fileBytes2) {
//         //   singleChar2 = (char) b2;
//         //   System.out.print(singleChar2);
//         // }

//         // System.out.println("Done.");

//         // everything ok, so returns true
//         return true;
//     }
// }


// BACKUP ESCREVE BELS PRA 1 AGENTE SÓ
// package mylib;

// import jason.*;
// import jason.runtime.*;
// import jason.asSemantics.*;
// import jason.asSyntax.*;

// import java.nio.file.Path;
// import java.nio.file.Files;
// import java.nio.file.Paths;
// import java.io.*;
// import java.util.List;

// // FUNCIONAVA SÓ LENDO, AGORA QUERO ESCREVER
// // import java.nio.charset.StandardCharsets;

// import java.nio.charset.StandardCharsets;
// import java.nio.file.StandardOpenOption;


// // SÓ PRO RANDOM NO NOME, SE NÃO USAR, TIRAR
// import java.util.Random;

// //import java.io.File;

// public class my_create_ag extends DefaultInternalAction {

//     @Override
//     public Object execute(TransitionSystem ts, Unifier un, Term[] args) throws Exception {

//         System.out.println("Executing JAVA custom code");

//         if (Files.exists(Paths.get("/teste/important/send_agent3.txt")) && Files.size(Paths.get("/teste/important/send_agent3.txt")) >= 0 ) {
//             System.out.println("existe e não vazio");
//         }
//         else {
//             System.out.println("não existe ou vazio");
//         }

//         if (Files.exists(Paths.get("/teste/important/data0.txt"))) {
//             System.out.println("/teste/important/data0.txt não existe");
//         }
//         else {
//             if (Files.exists(Paths.get("/teste/important/send_agent3.txt"))) {
//                 // use Settings to add initial beliefs and goals for the new agent
//                 // (as used in the .mas2j project file)
//                 // Settings s = new Settings();
//                 // s.addOption(Settings.INIT_BELS, "b(10),b(20)");
//                 // s.addOption(Settings.INIT_GOALS, "a");

//                 // RuntimeServices provides services to create agents in the current platform (Local, JADE, JaCaMo, ...)
//                 RuntimeServices rs = RuntimeServicesFactory.get();

//                 int line = 1;
//                 String read_line = Files.readAllLines(Paths.get("/teste/important/send_agent3.txt")).get(line - 1);
//                 System.out.println(read_line);

//                 String name = read_line;
//                 // name = rs.createAgent(name.split(" ")[1], "bob.asl", null, null, null, s, ts.getAg());
//                 // Random random = new Random();
//                 // name = rs.createAgent(Double.toString(random.nextDouble() * 100), "bob.asl", null, null, null, s, ts.getAg());

//                 //String str = " Hello I'm your String";

//                 Random random = new Random();

//                 String[] splitStr = read_line.split("\\s+");
//                 Settings s = new Settings();
//                 String bels = "b(10),b(20)";
//                 s.addOption(Settings.INIT_BELS, bels+ ", b("+splitStr[2]+"), b("+splitStr[3]+"), b("+splitStr[4]+")");
//                 s.addOption(Settings.INIT_GOALS, "a");
//                 name = rs.createAgent(splitStr[1]+Double.toString(random.nextDouble() * 100), "bob.asl", null, null, null, s, ts.getAg());
//                 rs.startAgent(name);
//                 System.out.println("Agent created by custom file");
//             }
//             else {
//                 System.out.println("/teste/important/send_agent3.txt não existe");
//             }
//         }


//         // System.out.println("Writing...");

//         // Files.write(Paths.get("data2.txt"), "the text \n".getBytes(), StandardOpenOption.CREATE);
//         // Files.write(Paths.get("data2.txt"), "aehoo \n".getBytes(), StandardOpenOption.APPEND);

//         // System.out.println("Reading...");

//         // String fileName2 = "data2.txt";
//         // File file2 = new File(fileName2);

//         // byte [] fileBytes2 = Files.readAllBytes(file2.toPath());
//         // char singleChar2;
//         // for(byte b2 : fileBytes2) {
//         //   singleChar2 = (char) b2;
//         //   System.out.print(singleChar2);
//         // }

//         // System.out.println("Done.");

//         // everything ok, so returns true
//         return true;
//     }
// }


// BACKUP, DEPOIS DE JA TER JUNTADO, LÊ ARQUIVO E PRINTA COM NOME RANDOM
// package mylib;

// import jason.*;
// import jason.runtime.*;
// import jason.asSemantics.*;
// import jason.asSyntax.*;

// import java.nio.file.Path;
// import java.nio.file.Files;
// import java.nio.file.Paths;
// import java.io.*;
// import java.util.List;

// // FUNCIONAVA SÓ LENDO, AGORA QUERO ESCREVER
// // import java.nio.charset.StandardCharsets;

// import java.nio.charset.StandardCharsets;
// import java.nio.file.StandardOpenOption;


// // SÓ PRO RANDOM NO NOME, SE NÃO USAR, TIRAR
// import java.util.Random;

// //import java.io.File;

// public class my_create_ag extends DefaultInternalAction {

//     @Override
//     public Object execute(TransitionSystem ts, Unifier un, Term[] args) throws Exception {

//         System.out.println("Executing JAVA custom code");

//         if (Files.exists(Paths.get("/teste/important/send_agent3.txt")) && Files.size(Paths.get("/teste/important/send_agent3.txt")) >= 0 ) {
//             System.out.println("existe e vazio");
//         }
//         else {
//             System.out.println("não existe ou não vazio");
//         }

//         if (Files.exists(Paths.get("/teste/important/data0.txt"))) {
//             System.out.println("/teste/important/data0.txt não existe");
//         }
//         else {
//             if (Files.exists(Paths.get("/teste/important/send_agent3.txt"))) {
//                 // use Settings to add initial beliefs and goals for the new agent
//                 // (as used in the .mas2j project file)
//                 Settings s = new Settings();
//                 s.addOption(Settings.INIT_BELS, "b(10),b(20)");
//                 s.addOption(Settings.INIT_GOALS, "a");

//                 // RuntimeServices provides services to create agents in the current platform (Local, JADE, JaCaMo, ...)
//                 RuntimeServices rs = RuntimeServicesFactory.get();

//                 int line = 1;
//                 String read_line = Files.readAllLines(Paths.get("/teste/important/send_agent3.txt")).get(line - 1);
//                 System.out.println(read_line);

//                 String name = read_line;
//                 // name = rs.createAgent(name.split(" ")[1], "bob.asl", null, null, null, s, ts.getAg());
//                 Random random = new Random();
//                 name = rs.createAgent(Double.toString(random.nextDouble() * 100), "bob.asl", null, null, null, s, ts.getAg());
//                 rs.startAgent(name);
//                 System.out.println("Agent created by custom file");
//             }
//             else {
//                 System.out.println("/teste/important/send_agent3.txt não existe");
//             }
//         }


//         // System.out.println("Writing...");

//         // Files.write(Paths.get("data2.txt"), "the text \n".getBytes(), StandardOpenOption.CREATE);
//         // Files.write(Paths.get("data2.txt"), "aehoo \n".getBytes(), StandardOpenOption.APPEND);

//         // System.out.println("Reading...");

//         // String fileName2 = "data2.txt";
//         // File file2 = new File(fileName2);

//         // byte [] fileBytes2 = Files.readAllBytes(file2.toPath());
//         // char singleChar2;
//         // for(byte b2 : fileBytes2) {
//         //   singleChar2 = (char) b2;
//         //   System.out.print(singleChar2);
//         // }

//         // System.out.println("Done.");

//         // everything ok, so returns true
//         return true;
//     }
// }

// BACKUP ANTES DE JUNTAR COM TUDO, LÊ E ESCREVE, ANTES DE LER ARQUIVOS DO NETLOGO

// package mylib;

// import jason.*;
// import jason.runtime.*;
// import jason.asSemantics.*;
// import jason.asSyntax.*;

// import java.nio.file.Path;
// import java.nio.file.Files;
// import java.nio.file.Paths;
// import java.io.*;
// import java.util.List;

// // FUNCIONAVA SÓ LENDO, AGORA QUERO ESCREVER
// // import java.nio.charset.StandardCharsets;

// import java.nio.charset.StandardCharsets;
// import java.nio.file.StandardOpenOption;

// //import java.io.File;

// public class my_create_ag extends DefaultInternalAction {

//     @Override
//     public Object execute(TransitionSystem ts, Unifier un, Term[] args) throws Exception {

//         // use Settings to add initial beliefs and goals for the new agent
//         // (as used in the .mas2j project file)
//         Settings s = new Settings();
//         s.addOption(Settings.INIT_BELS, "b(10),b(20)");
//         s.addOption(Settings.INIT_GOALS, "a");

//         // RuntimeServices provides services to create agents in the current platform (Local, JADE, JaCaMo, ...)
//         RuntimeServices rs = RuntimeServicesFactory.get();

//         int line = 1;
//         String read_line = Files.readAllLines(Paths.get("data.txt")).get(line - 1);
//         System.out.println(read_line);

//         //Path path2 = Paths.get("data.txt");
//         //List<String> lines2 = Files.readAllLines(path2, StandardCharsets.UTF_8);
//         System.out.println("Writing...");
//         //Path path3 = Paths.get("data2.txt");
//         //Files.write(path3, lines2, StandardCharsets.UTF_8, StandardOpenOption.CREATE, StandardOpenOption.APPEND);

//         Files.write(Paths.get("data2.txt"), "the text \n".getBytes(), StandardOpenOption.CREATE);
//         Files.write(Paths.get("data2.txt"), "aehoo \n".getBytes(), StandardOpenOption.APPEND);

//         System.out.println("Reading...");

//         String fileName2 = "data2.txt";
//         File file2 = new File(fileName2);

//         byte [] fileBytes2 = Files.readAllBytes(file2.toPath());
//         char singleChar2;
//         for(byte b2 : fileBytes2) {
//           singleChar2 = (char) b2;
//           System.out.print(singleChar2);
//         }

//         // FUNCIONA, LÊ, MAS É A OPÇÃO LENTA
//         // String fileName2 = "data2.txt";
//         // FileReader fileReader2 = new FileReader(fileName2);

//         // BufferedReader bufferedReader2 = new BufferedReader(fileReader2);
//         // String line2;
//         // while((line2 = bufferedReader2.readLine()) != null) {
//         //     System.out.println(line2);
//         // }

//         System.out.println("Done.");

//         // System.out.println("Será?");

//         // String fileName = "data2.txt";
//         // File file = new File(fileName);

//         // byte [] fileBytes = Files.readAllBytes(file.toPath());
//         // char singleChar;
//         // for(byte b : fileBytes) {
//         //   singleChar = (char) b;
//         //   System.out.println(singleChar);
//         // }

//         // System.out.println("foi?");

//         //String name = System.getProperty("user.dir");
//         String name = read_line;
//         //String name = "ta_dificil";
//         name = rs.createAgent(name, "bob.asl", null, null, null, s, ts.getAg());
//         rs.startAgent(name);

//         // int lineNumber = 1;
//         // String data = "aeee";
//         // Path path = Paths.get("data2.txt");
//         // List<String> lines = Files.readAllLines(path, StandardCharsets.UTF_8);
//         // lines.set(lineNumber - 1, data);
//         // // IMPRIME EM LINHA ESPECIFICA
//         // Files.write(path, lines, StandardCharsets.UTF_8);


//         // String name = read_line.get(0);
//         // name = rs.createAgent(name, "bob.asl", null, null, null, s, ts.getAg());
//         // rs.startAgent(name);

//         // everything ok, so returns true
//         return true;
//     }
// }


// BACKUP LE E ESCREVE EM ARQUIVO

// Write your code here
// System.out.println("Hello, World!");

// int line = 1;
// String read_line = Files.readAllLines(Paths.get("data.txt")).get(line - 1);
// System.out.println(read_line);

// int lineNumber = 1;
// String data = "aeee";
// Path path = Paths.get("data.txt");
// List<String> lines = Files.readAllLines(path, StandardCharsets.UTF_8);
// lines.set(lineNumber - 1, data);
// // IMPRIME EM LINHA ESPECIFICA
// Files.write(path, lines, StandardCharsets.UTF_8);



// PELO MENOS FUNCIONA ALGO

// public class my_create_ag extends DefaultInternalAction {

//     @Override
//     public Object execute(TransitionSystem ts, Unifier un, Term[] args) throws Exception {

//         // use Settings to add initial beliefs and goals for the new agent
//         // (as used in the .mas2j project file)
//         Settings s = new Settings();
//         s.addOption(Settings.INIT_BELS, "b(10),b(20)");
//         s.addOption(Settings.INIT_GOALS, "a");

//         // RuntimeServices provides services to create agents in the current platform (Local, JADE, JaCaMo, ...)
//         RuntimeServices rs = RuntimeServicesFactory.get();

//         int line = 1;
//         String read_line = Files.readAllLines(Paths.get("data.txt")).get(line - 1);
//         System.out.println(read_line);

//         //String name = System.getProperty("user.dir");
//         String name = read_line;
//         //String name = "ta_dificil";
//         name = rs.createAgent(name, "bob.asl", null, null, null, s, ts.getAg());
//         rs.startAgent(name);

//         // String name = read_line.get(0);
//         // name = rs.createAgent(name, "bob.asl", null, null, null, s, ts.getAg());
//         // rs.startAgent(name);

//         // everything ok, so returns true
//         return true;
//     }
// }



// BACKUP ANTES DE COMEÇAR A USAR ARQUIVOS .ASL PRA GERAR OS AGENTES
// package mylib;

// import jason.*;
// import jason.runtime.*;
// import jason.asSemantics.*;
// import jason.asSyntax.*;

// import java.nio.file.Path;
// import java.nio.file.Files;
// import java.nio.file.Paths;
// import java.io.*;
// import java.util.List;

// // FUNCIONAVA SÓ LENDO, AGORA QUERO ESCREVER
// // import java.nio.charset.StandardCharsets;

// import java.nio.charset.StandardCharsets;
// import java.nio.file.StandardOpenOption;


// // SÓ PRO RANDOM NO NOME, SE NÃO USAR, TIRAR
// import java.util.Random;

// //import java.io.File;

// import java.util.stream.Stream;

// public class aaa_my_create_ag extends DefaultInternalAction {

//     @Override
//     public Object execute(TransitionSystem ts, Unifier un, Term[] args) throws Exception {

//         boolean using_docker = false;
//         String path = "";

//         if (using_docker){
//             path = "/teste/important/receive_agent3.txt";
//         } else {
//             path = "teste/important/receive_agent3.txt";
//         }

//         System.out.println("Executing JAVA custom code - create");

//         if (Files.exists(Paths.get(path)) && Files.size(Paths.get(path)) >= 0) {            
//             // RuntimeServices provides services to create agents in the current platform (Local, JADE, JaCaMo, ...)
//             RuntimeServices rs = RuntimeServicesFactory.get();

//             String fileName = path;
//             File file = new File(fileName);

//             try (Stream linesStream = Files.lines(file.toPath())) {
//                 linesStream.forEach(line2 -> {
//                     String name = "";
//                     String aehoo = String.valueOf(line2);

//                     System.out.println(aehoo);

//                     String[] splitStr = aehoo.split("\\s+");

//                     // use Settings to add initial beliefs and goals for the new agent
//                     // (as used in the .mas2j project file)
//                     Settings s = new Settings();
//                     String bels = "b(10),b(20)";
//                     s.addOption(Settings.INIT_BELS, bels+ ", b("+splitStr[2]+"), b("+splitStr[3]+"), b("+splitStr[4]+")");
//                     s.addOption(Settings.INIT_GOALS, "a");

//                     try {
//                         rs.createAgent(splitStr[1], "bob.asl", null, null, null, s, ts.getAg());
//                         rs.startAgent(splitStr[1]);
//                         System.out.println("Agent created by custom file");
//                     } catch (Exception e) {

//                     }
//                 });

//                 System.out.println("! Deleting After creating agents !");
//                 Files.delete(Paths.get(path));
//                 System.out.println("! Deleted !");
//             }

//             // System.out.println("! Deleting After creating agents !");
//             // Files.delete(Paths.get("/teste/important/send_agent3.txt"));
//             // System.out.println("! Deleted !");
//         }
//         else {
//             System.out.println(path+" não existe");
//         }


//         // System.out.println("Writing...");

//         // Files.write(Paths.get("data2.txt"), "the text \n".getBytes(), StandardOpenOption.CREATE);
//         // Files.write(Paths.get("data2.txt"), "aehoo \n".getBytes(), StandardOpenOption.APPEND);

//         // System.out.println("Reading...");

//         // String fileName2 = "data2.txt";
//         // File file2 = new File(fileName2);

//         // byte [] fileBytes2 = Files.readAllBytes(file2.toPath());
//         // char singleChar2;
//         // for(byte b2 : fileBytes2) {
//         //   singleChar2 = (char) b2;
//         //   System.out.print(singleChar2);
//         // }

//         // System.out.println("Done.");

//         // everything ok, so returns true
//         return true;
//     }
// }


// // BACKUP ANTES DE JUNTAR COM A ESTRUTURA TODA, TA CRIANDO TODOS AGENTES DO ARQUIVO, 1 POR 1
// // package mylib;

// // import jason.*;
// // import jason.runtime.*;
// // import jason.asSemantics.*;
// // import jason.asSyntax.*;

// // import java.nio.file.Path;
// // import java.nio.file.Files;
// // import java.nio.file.Paths;
// // import java.io.*;
// // import java.util.List;

// // // FUNCIONAVA SÓ LENDO, AGORA QUERO ESCREVER
// // // import java.nio.charset.StandardCharsets;

// // import java.nio.charset.StandardCharsets;
// // import java.nio.file.StandardOpenOption;


// // // SÓ PRO RANDOM NO NOME, SE NÃO USAR, TIRAR
// // import java.util.Random;

// // //import java.io.File;

// // import java.util.stream.Stream;

// // public class my_create_ag extends DefaultInternalAction {

// //     @Override
// //     public Object execute(TransitionSystem ts, Unifier un, Term[] args) throws Exception {

// //         System.out.println("Executing JAVA custom code - create");

// //         if (Files.exists(Paths.get("/teste/important/send_agent3.txt")) && Files.size(Paths.get("/teste/important/send_agent3.txt")) >= 0 ) {
// //             System.out.println("existe e não vazio");
// //         }
// //         else {
// //             System.out.println("não existe ou vazio");
// //         }

// //         if (Files.exists(Paths.get("/teste/important/data0.txt"))) {
// //             System.out.println("/teste/important/data0.txt não existe");
// //         }
// //         else {
// //             if (Files.exists(Paths.get("/teste/important/send_agent3.txt"))) {

// //                 // RuntimeServices provides services to create agents in the current platform (Local, JADE, JaCaMo, ...)
// //                 RuntimeServices rs = RuntimeServicesFactory.get();

// //                 String fileName = "/teste/important/send_agent3.txt";
// //                 File file = new File(fileName);

// //                 try (Stream linesStream = Files.lines(file.toPath())) {
// //                     linesStream.forEach(line2 -> {
// //                         String name = "";
// //                         String aehoo = String.valueOf(line2);

// //                         System.out.println(aehoo);

// //                         String[] splitStr = aehoo.split("\\s+");

// //                         // use Settings to add initial beliefs and goals for the new agent
// //                         // (as used in the .mas2j project file)
// //                         Settings s = new Settings();
// //                         String bels = "b(10),b(20)";
// //                         s.addOption(Settings.INIT_BELS, bels+ ", b("+splitStr[2]+"), b("+splitStr[3]+"), b("+splitStr[4]+")");
// //                         s.addOption(Settings.INIT_GOALS, "a");

// //                         try {
// //                             rs.createAgent(splitStr[1], "bob.asl", null, null, null, s, ts.getAg());
// //                             rs.startAgent(splitStr[1]);
// //                             System.out.println("Agent created by custom file");
// //                         } catch (Exception e) {

// //                         }
// //                     });
// //                 }

// //                 // System.out.println("! Deleting After creating agents !");
// //                 // Files.delete(Paths.get("/teste/important/send_agent3.txt"));
// //                 // System.out.println("! Deleted !");
// //             }
// //             else {
// //                 System.out.println("/teste/important/send_agent3.txt não existe");
// //             }
// //         }


// //         // System.out.println("Writing...");

// //         // Files.write(Paths.get("data2.txt"), "the text \n".getBytes(), StandardOpenOption.CREATE);
// //         // Files.write(Paths.get("data2.txt"), "aehoo \n".getBytes(), StandardOpenOption.APPEND);

// //         // System.out.println("Reading...");

// //         // String fileName2 = "data2.txt";
// //         // File file2 = new File(fileName2);

// //         // byte [] fileBytes2 = Files.readAllBytes(file2.toPath());
// //         // char singleChar2;
// //         // for(byte b2 : fileBytes2) {
// //         //   singleChar2 = (char) b2;
// //         //   System.out.print(singleChar2);
// //         // }

// //         // System.out.println("Done.");

// //         // everything ok, so returns true
// //         return true;
// //     }
// // }


// // BACKUP ESCREVE BELS PRA 1 AGENTE SÓ
// // package mylib;

// // import jason.*;
// // import jason.runtime.*;
// // import jason.asSemantics.*;
// // import jason.asSyntax.*;

// // import java.nio.file.Path;
// // import java.nio.file.Files;
// // import java.nio.file.Paths;
// // import java.io.*;
// // import java.util.List;

// // // FUNCIONAVA SÓ LENDO, AGORA QUERO ESCREVER
// // // import java.nio.charset.StandardCharsets;

// // import java.nio.charset.StandardCharsets;
// // import java.nio.file.StandardOpenOption;


// // // SÓ PRO RANDOM NO NOME, SE NÃO USAR, TIRAR
// // import java.util.Random;

// // //import java.io.File;

// // public class my_create_ag extends DefaultInternalAction {

// //     @Override
// //     public Object execute(TransitionSystem ts, Unifier un, Term[] args) throws Exception {

// //         System.out.println("Executing JAVA custom code");

// //         if (Files.exists(Paths.get("/teste/important/send_agent3.txt")) && Files.size(Paths.get("/teste/important/send_agent3.txt")) >= 0 ) {
// //             System.out.println("existe e não vazio");
// //         }
// //         else {
// //             System.out.println("não existe ou vazio");
// //         }

// //         if (Files.exists(Paths.get("/teste/important/data0.txt"))) {
// //             System.out.println("/teste/important/data0.txt não existe");
// //         }
// //         else {
// //             if (Files.exists(Paths.get("/teste/important/send_agent3.txt"))) {
// //                 // use Settings to add initial beliefs and goals for the new agent
// //                 // (as used in the .mas2j project file)
// //                 // Settings s = new Settings();
// //                 // s.addOption(Settings.INIT_BELS, "b(10),b(20)");
// //                 // s.addOption(Settings.INIT_GOALS, "a");

// //                 // RuntimeServices provides services to create agents in the current platform (Local, JADE, JaCaMo, ...)
// //                 RuntimeServices rs = RuntimeServicesFactory.get();

// //                 int line = 1;
// //                 String read_line = Files.readAllLines(Paths.get("/teste/important/send_agent3.txt")).get(line - 1);
// //                 System.out.println(read_line);

// //                 String name = read_line;
// //                 // name = rs.createAgent(name.split(" ")[1], "bob.asl", null, null, null, s, ts.getAg());
// //                 // Random random = new Random();
// //                 // name = rs.createAgent(Double.toString(random.nextDouble() * 100), "bob.asl", null, null, null, s, ts.getAg());

// //                 //String str = " Hello I'm your String";

// //                 Random random = new Random();

// //                 String[] splitStr = read_line.split("\\s+");
// //                 Settings s = new Settings();
// //                 String bels = "b(10),b(20)";
// //                 s.addOption(Settings.INIT_BELS, bels+ ", b("+splitStr[2]+"), b("+splitStr[3]+"), b("+splitStr[4]+")");
// //                 s.addOption(Settings.INIT_GOALS, "a");
// //                 name = rs.createAgent(splitStr[1]+Double.toString(random.nextDouble() * 100), "bob.asl", null, null, null, s, ts.getAg());
// //                 rs.startAgent(name);
// //                 System.out.println("Agent created by custom file");
// //             }
// //             else {
// //                 System.out.println("/teste/important/send_agent3.txt não existe");
// //             }
// //         }


// //         // System.out.println("Writing...");

// //         // Files.write(Paths.get("data2.txt"), "the text \n".getBytes(), StandardOpenOption.CREATE);
// //         // Files.write(Paths.get("data2.txt"), "aehoo \n".getBytes(), StandardOpenOption.APPEND);

// //         // System.out.println("Reading...");

// //         // String fileName2 = "data2.txt";
// //         // File file2 = new File(fileName2);

// //         // byte [] fileBytes2 = Files.readAllBytes(file2.toPath());
// //         // char singleChar2;
// //         // for(byte b2 : fileBytes2) {
// //         //   singleChar2 = (char) b2;
// //         //   System.out.print(singleChar2);
// //         // }

// //         // System.out.println("Done.");

// //         // everything ok, so returns true
// //         return true;
// //     }
// // }


// // BACKUP, DEPOIS DE JA TER JUNTADO, LÊ ARQUIVO E PRINTA COM NOME RANDOM
// // package mylib;

// // import jason.*;
// // import jason.runtime.*;
// // import jason.asSemantics.*;
// // import jason.asSyntax.*;

// // import java.nio.file.Path;
// // import java.nio.file.Files;
// // import java.nio.file.Paths;
// // import java.io.*;
// // import java.util.List;

// // // FUNCIONAVA SÓ LENDO, AGORA QUERO ESCREVER
// // // import java.nio.charset.StandardCharsets;

// // import java.nio.charset.StandardCharsets;
// // import java.nio.file.StandardOpenOption;


// // // SÓ PRO RANDOM NO NOME, SE NÃO USAR, TIRAR
// // import java.util.Random;

// // //import java.io.File;

// // public class my_create_ag extends DefaultInternalAction {

// //     @Override
// //     public Object execute(TransitionSystem ts, Unifier un, Term[] args) throws Exception {

// //         System.out.println("Executing JAVA custom code");

// //         if (Files.exists(Paths.get("/teste/important/send_agent3.txt")) && Files.size(Paths.get("/teste/important/send_agent3.txt")) >= 0 ) {
// //             System.out.println("existe e vazio");
// //         }
// //         else {
// //             System.out.println("não existe ou não vazio");
// //         }

// //         if (Files.exists(Paths.get("/teste/important/data0.txt"))) {
// //             System.out.println("/teste/important/data0.txt não existe");
// //         }
// //         else {
// //             if (Files.exists(Paths.get("/teste/important/send_agent3.txt"))) {
// //                 // use Settings to add initial beliefs and goals for the new agent
// //                 // (as used in the .mas2j project file)
// //                 Settings s = new Settings();
// //                 s.addOption(Settings.INIT_BELS, "b(10),b(20)");
// //                 s.addOption(Settings.INIT_GOALS, "a");

// //                 // RuntimeServices provides services to create agents in the current platform (Local, JADE, JaCaMo, ...)
// //                 RuntimeServices rs = RuntimeServicesFactory.get();

// //                 int line = 1;
// //                 String read_line = Files.readAllLines(Paths.get("/teste/important/send_agent3.txt")).get(line - 1);
// //                 System.out.println(read_line);

// //                 String name = read_line;
// //                 // name = rs.createAgent(name.split(" ")[1], "bob.asl", null, null, null, s, ts.getAg());
// //                 Random random = new Random();
// //                 name = rs.createAgent(Double.toString(random.nextDouble() * 100), "bob.asl", null, null, null, s, ts.getAg());
// //                 rs.startAgent(name);
// //                 System.out.println("Agent created by custom file");
// //             }
// //             else {
// //                 System.out.println("/teste/important/send_agent3.txt não existe");
// //             }
// //         }


// //         // System.out.println("Writing...");

// //         // Files.write(Paths.get("data2.txt"), "the text \n".getBytes(), StandardOpenOption.CREATE);
// //         // Files.write(Paths.get("data2.txt"), "aehoo \n".getBytes(), StandardOpenOption.APPEND);

// //         // System.out.println("Reading...");

// //         // String fileName2 = "data2.txt";
// //         // File file2 = new File(fileName2);

// //         // byte [] fileBytes2 = Files.readAllBytes(file2.toPath());
// //         // char singleChar2;
// //         // for(byte b2 : fileBytes2) {
// //         //   singleChar2 = (char) b2;
// //         //   System.out.print(singleChar2);
// //         // }

// //         // System.out.println("Done.");

// //         // everything ok, so returns true
// //         return true;
// //     }
// // }

// // BACKUP ANTES DE JUNTAR COM TUDO, LÊ E ESCREVE, ANTES DE LER ARQUIVOS DO NETLOGO

// // package mylib;

// // import jason.*;
// // import jason.runtime.*;
// // import jason.asSemantics.*;
// // import jason.asSyntax.*;

// // import java.nio.file.Path;
// // import java.nio.file.Files;
// // import java.nio.file.Paths;
// // import java.io.*;
// // import java.util.List;

// // // FUNCIONAVA SÓ LENDO, AGORA QUERO ESCREVER
// // // import java.nio.charset.StandardCharsets;

// // import java.nio.charset.StandardCharsets;
// // import java.nio.file.StandardOpenOption;

// // //import java.io.File;

// // public class my_create_ag extends DefaultInternalAction {

// //     @Override
// //     public Object execute(TransitionSystem ts, Unifier un, Term[] args) throws Exception {

// //         // use Settings to add initial beliefs and goals for the new agent
// //         // (as used in the .mas2j project file)
// //         Settings s = new Settings();
// //         s.addOption(Settings.INIT_BELS, "b(10),b(20)");
// //         s.addOption(Settings.INIT_GOALS, "a");

// //         // RuntimeServices provides services to create agents in the current platform (Local, JADE, JaCaMo, ...)
// //         RuntimeServices rs = RuntimeServicesFactory.get();

// //         int line = 1;
// //         String read_line = Files.readAllLines(Paths.get("data.txt")).get(line - 1);
// //         System.out.println(read_line);

// //         //Path path2 = Paths.get("data.txt");
// //         //List<String> lines2 = Files.readAllLines(path2, StandardCharsets.UTF_8);
// //         System.out.println("Writing...");
// //         //Path path3 = Paths.get("data2.txt");
// //         //Files.write(path3, lines2, StandardCharsets.UTF_8, StandardOpenOption.CREATE, StandardOpenOption.APPEND);

// //         Files.write(Paths.get("data2.txt"), "the text \n".getBytes(), StandardOpenOption.CREATE);
// //         Files.write(Paths.get("data2.txt"), "aehoo \n".getBytes(), StandardOpenOption.APPEND);

// //         System.out.println("Reading...");

// //         String fileName2 = "data2.txt";
// //         File file2 = new File(fileName2);

// //         byte [] fileBytes2 = Files.readAllBytes(file2.toPath());
// //         char singleChar2;
// //         for(byte b2 : fileBytes2) {
// //           singleChar2 = (char) b2;
// //           System.out.print(singleChar2);
// //         }

// //         // FUNCIONA, LÊ, MAS É A OPÇÃO LENTA
// //         // String fileName2 = "data2.txt";
// //         // FileReader fileReader2 = new FileReader(fileName2);

// //         // BufferedReader bufferedReader2 = new BufferedReader(fileReader2);
// //         // String line2;
// //         // while((line2 = bufferedReader2.readLine()) != null) {
// //         //     System.out.println(line2);
// //         // }

// //         System.out.println("Done.");

// //         // System.out.println("Será?");

// //         // String fileName = "data2.txt";
// //         // File file = new File(fileName);

// //         // byte [] fileBytes = Files.readAllBytes(file.toPath());
// //         // char singleChar;
// //         // for(byte b : fileBytes) {
// //         //   singleChar = (char) b;
// //         //   System.out.println(singleChar);
// //         // }

// //         // System.out.println("foi?");

// //         //String name = System.getProperty("user.dir");
// //         String name = read_line;
// //         //String name = "ta_dificil";
// //         name = rs.createAgent(name, "bob.asl", null, null, null, s, ts.getAg());
// //         rs.startAgent(name);

// //         // int lineNumber = 1;
// //         // String data = "aeee";
// //         // Path path = Paths.get("data2.txt");
// //         // List<String> lines = Files.readAllLines(path, StandardCharsets.UTF_8);
// //         // lines.set(lineNumber - 1, data);
// //         // // IMPRIME EM LINHA ESPECIFICA
// //         // Files.write(path, lines, StandardCharsets.UTF_8);


// //         // String name = read_line.get(0);
// //         // name = rs.createAgent(name, "bob.asl", null, null, null, s, ts.getAg());
// //         // rs.startAgent(name);

// //         // everything ok, so returns true
// //         return true;
// //     }
// // }


// // BACKUP LE E ESCREVE EM ARQUIVO

// // Write your code here
// // System.out.println("Hello, World!");

// // int line = 1;
// // String read_line = Files.readAllLines(Paths.get("data.txt")).get(line - 1);
// // System.out.println(read_line);

// // int lineNumber = 1;
// // String data = "aeee";
// // Path path = Paths.get("data.txt");
// // List<String> lines = Files.readAllLines(path, StandardCharsets.UTF_8);
// // lines.set(lineNumber - 1, data);
// // // IMPRIME EM LINHA ESPECIFICA
// // Files.write(path, lines, StandardCharsets.UTF_8);



// // PELO MENOS FUNCIONA ALGO

// // public class my_create_ag extends DefaultInternalAction {

// //     @Override
// //     public Object execute(TransitionSystem ts, Unifier un, Term[] args) throws Exception {

// //         // use Settings to add initial beliefs and goals for the new agent
// //         // (as used in the .mas2j project file)
// //         Settings s = new Settings();
// //         s.addOption(Settings.INIT_BELS, "b(10),b(20)");
// //         s.addOption(Settings.INIT_GOALS, "a");

// //         // RuntimeServices provides services to create agents in the current platform (Local, JADE, JaCaMo, ...)
// //         RuntimeServices rs = RuntimeServicesFactory.get();

// //         int line = 1;
// //         String read_line = Files.readAllLines(Paths.get("data.txt")).get(line - 1);
// //         System.out.println(read_line);

// //         //String name = System.getProperty("user.dir");
// //         String name = read_line;
// //         //String name = "ta_dificil";
// //         name = rs.createAgent(name, "bob.asl", null, null, null, s, ts.getAg());
// //         rs.startAgent(name);

// //         // String name = read_line.get(0);
// //         // name = rs.createAgent(name, "bob.asl", null, null, null, s, ts.getAg());
// //         // rs.startAgent(name);

// //         // everything ok, so returns true
// //         return true;
// //     }
// // }
