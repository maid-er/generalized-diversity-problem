@echo off
:: irace arguments:
:: %1 = Config ID, %2 = Instance ID, %3 = Seed, %4 = Instance Path, %5... = Parameters

set SEED=%3
set INSTANCE=%4

:: Store the configuration parameters (everything from %5 onwards)
:: We use a trick to capture the rest of the command line
for /f "tokens=4,*" %%a in ("%*") do set PARAMS=%%b

:: Run the python script
:: %PARAMS% now contains "--std_interval X --beta Y --threshold Z --delta W"
.\venv\Scripts\python.exe src_irace\main.py --seed %SEED% --instance %INSTANCE% %PARAMS%