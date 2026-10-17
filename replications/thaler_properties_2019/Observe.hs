module Main where

import Control.Monad (forM_, when)
import Data.List (intercalate)
import System.Environment (getArgs)
import System.IO
import System.Random (StdGen)

import SugarScape.Core.Discrete
import SugarScape.Core.Model
import SugarScape.Core.Scenario
import SugarScape.Core.Simulation

scenarios :: [(String, SugarScapeScenario)]
scenarios = [
    ("mkParamsAnimationII_1", mkParamsAnimationII_1),
    ("mkParamsAnimationII_2", mkParamsAnimationII_2),
    ("mkParamsAnimationII_3", mkParamsAnimationII_3),
    ("mkParamsAnimationII_4", mkParamsAnimationII_4),
    ("mkParamsAnimationII_5", mkParamsAnimationII_5),
    ("mkParamsAnimationII_6", mkParamsAnimationII_6),
    ("mkParamsAnimationII_7", mkParamsAnimationII_7),
    ("mkParamsAnimationII_8", mkParamsAnimationII_8),
    ("mkParamsAnimationIII_1", mkParamsAnimationIII_1),
    ("mkParamsFigureIII_3", mkParamsFigureIII_3),
    ("mkParamsFigureIII_4", mkParamsFigureIII_4),
    ("mkParamsFigureIII_7", mkParamsFigureIII_7),
    ("mkParamsAnimationIII_4", mkParamsAnimationIII_4),
    ("mkParamsAnimationIII_6", mkParamsAnimationIII_6),
    ("mkParamsAnimationIII_7", mkParamsAnimationIII_7),
    ("mkParamsFigureIII_8", mkParamsFigureIII_8),
    ("mkParamsAnimationIII_9", mkParamsAnimationIII_9),
    ("mkParamsAnimationIII_10", mkParamsAnimationIII_10),
    ("mkParamsAnimationIII_11", mkParamsAnimationIII_11),
    ("mkParamsAnimationIII_14", mkParamsAnimationIII_14),
    ("mkParamsAnimationIII_15", mkParamsAnimationIII_15),
    ("mkParamsAnimationIV_1", mkParamsAnimationIV_1),
    ("mkParamsFigureIV_3", mkParamsFigureIV_3),
    ("mkParamsFigureIV_4", mkParamsFigureIV_4),
    ("mkParamsFigureIV_5", mkParamsFigureIV_5),
    ("mkParamsFigureIV_6", mkParamsFigureIV_6),
    ("mkCarryingCapacityWithSpice", mkCarryingCapacityWithSpice),
    ("mkParamsFigureIV_7", mkParamsFigureIV_7),
    ("mkParamsFigureIV_8", mkParamsFigureIV_8),
    ("mkParamsFigureIV_9", mkParamsFigureIV_9),
    ("mkParamsFigureIV_10", mkParamsFigureIV_10),
    ("mkParamsFigureIV_11", mkParamsFigureIV_11),
    ("mkParamsFigureIV_14", mkParamsFigureIV_14),
    ("mkParamsAnimationIV_5", mkParamsAnimationIV_5),
    ("mkParamsAnimationV_1", mkParamsAnimationV_1),
    ("mkParamsAnimationV_2", mkParamsAnimationV_2)
  ]

main :: IO ()
main = do
  [key, seedText, stepsText, strideText, prefix] <- getArgs
  let seed = read seedText :: Int
      steps = read stepsText :: Int
      stride = read strideText :: Int
      scenario = case [value | (name, value) <- scenarios, name == key] of
        [value] -> value
        _ -> error "Unknown or ambiguous scenario constructor"
      (initial, initialOutput, resolved) = initSimulationSeed seed scenario
  when (steps <= 0 || stride <= 0) $ error "Positive steps and snapshot stride required"
  writeFile (prefix ++ ".scenario.txt") ("Constructor: " ++ key ++ "\nSeed: " ++ show seed ++ "\n" ++ show resolved ++ "\n")
  withFile (prefix ++ ".summary.csv") WriteMode $ \summary ->
    withFile (prefix ++ ".agents.csv") WriteMode $ \agents ->
      withFile (prefix ++ ".trades.csv") WriteMode $ \trades ->
        withFile (prefix ++ ".cells.csv") WriteMode $ \cells -> do
          hPutStrLn summary "time,population,infected,zero_dominant,red,blue,agent_sugar,agent_spice,trade_count,price_sum,price_sum_squares,environment_sugar,environment_spice,pollution"
          hPutStrLn agents "time,id,x,y,age,sugar,spice,sugar_metabolism,spice_metabolism,vision,gender,tribe,culture,disease_count"
          hPutStrLn trades "time,id,partner,price,sugar,spice"
          hPutStrLn cells "time,x,y,sugar_capacity,sugar,spice_capacity,spice,pollution,occupier"
          observe steps stride summary agents trades cells initialOutput
          run steps stride summary agents trades cells initial

run :: Int -> Int -> Handle -> Handle -> Handle -> Handle -> SimulationState StdGen -> IO ()
run steps stride summary agents trades cells state = do
  let (next, output@(t, _, _, _)) = simulationStep state
  observe steps stride summary agents trades cells output
  if t >= steps then return () else run steps stride summary agents trades cells next

observe :: Int -> Int -> Handle -> Handle -> Handle -> Handle -> SimStepOut -> IO ()
observe steps stride summary agents trades cells (t, _, env, aos) = do
  let observations = map snd aos
      sites = allCells env
      prices = [price | ao <- observations, TradeInfo price _ _ _ <- sugObsTrades ao]
      infected = length $ filter (not . null . sugObsDiseases) observations
      zeroDominant = length $ filter (\ao -> 2 * length (filter not (sugObsCultureTag ao)) > length (sugObsCultureTag ao)) observations
      red = length $ filter ((== Red) . sugObsTribe) observations
      blue = length $ filter ((== Blue) . sugObsTribe) observations
  hPutStrLn summary $ intercalate "," [show t, show (length aos), show infected, show zeroDominant, show red, show blue,
    show (sum $ map sugObsSugLvl observations), show (sum $ map sugObsSpiLvl observations), show (length prices),
    show (sum prices), show (sum $ map (\x -> x*x) prices), show (sum $ map sugEnvSiteSugarLevel sites),
    show (sum $ map sugEnvSiteSpiceLevel sites), show (sum $ map sugEnvSitePolutionLevel sites)]
  when (t `mod` stride == 0 || t == steps) $
    forM_ aos $ \(aid, ao) -> do
      let (x, y) = sugObsCoord ao
          gender = case sugObsGender ao of Male -> "0"; Female -> "1"
          tribe = case sugObsTribe ao of Blue -> "0"; Red -> "1"
          culture = map (\tag -> if tag then '1' else '0') (sugObsCultureTag ao)
      hPutStrLn agents $ intercalate "," [show t, show aid, show x, show y, show (sugObsAge ao), show (sugObsSugLvl ao),
        show (sugObsSpiLvl ao), show (sugObsSugMetab ao), show (sugObsSpiMetab ao), show (sugObsVision ao), gender, tribe,
        culture, show (length $ sugObsDiseases ao)]
      forM_ (sugObsTrades ao) $ \(TradeInfo price sugar spice partner) ->
        hPutStrLn trades $ intercalate "," [show t, show aid, show partner, show price, show sugar, show spice]
  when (t == 0 || t == steps) $
    forM_ (allCellsWithCoords env) $ \((x, y), cell) -> do
      let occupier = case sugEnvSiteOccupier cell of Nothing -> -1; Just owner -> sugEnvOccId owner
      hPutStrLn cells $ intercalate "," [show t, show x, show y, show (sugEnvSiteSugarCapacity cell), show (sugEnvSiteSugarLevel cell),
        show (sugEnvSiteSpiceCapacity cell), show (sugEnvSiteSpiceLevel cell), show (sugEnvSitePolutionLevel cell), show occupier]
  hFlush summary
