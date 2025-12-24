@echo off
:: irace passes arguments in this order:
:: %1 = Configuration ID
:: %2 = Instance ID
:: %3 = Seed
:: %4 = Instance File Path
:: %5... = The parameters (e.g., --beta 0.5 --threshold 10)

:: Capture the fixed arguments we need
set SEED=%3
set INSTANCE=%4

:: Extract all arguments starting from %5 (the parameters)
:: This logic shifts the first 4 arguments away so we capture the rest
shift
shift
shift
shift

:: Run the python script
:: We manually pass --seed and --instance because irace passed them as positional args
.\venv\Scripts\python.exe src_irace\main.py --seed %SEED% --instance %INSTANCE% %1 %2 %3 %4 %5 %6 %7 %8 %9