module Main where
import Data.Bits (finiteBitSize)
import Data.List (intercalate)
import System.Environment (getArgs)
import System.Random (mkStdGen)
import Test.QuickCheck (Gen, choose, vectorOf)
import Test.QuickCheck.Gen (unGen)
import Test.QuickCheck.Random (mkQCGen)
main :: IO ()
main = do
  [oldPath, newPath, statesPath] <- getArgs
  old <- fmap read (readFile oldPath) :: IO [Int]
  let seeds = unGen (vectorOf 100 (choose (minBound, maxBound) :: Gen Int)) (mkQCGen 20261017) 30
      rows label values = [intercalate "," [label, show i, show seed, show (mkStdGen seed)] | (i, seed) <- zip [0 :: Int ..] values]
  writeFile newPath (show seeds ++ "\n")
  writeFile statesPath (unlines ("cohort,index,seed,stdgen" : rows "historical_protocol" old ++ rows "native_generator" seeds))
  putStrLn ("Int bits: " ++ show (finiteBitSize (0 :: Int)))
  putStrLn ("Native seeds: " ++ show (length seeds))
