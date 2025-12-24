import sys
import subprocess
import random

# irace envía: ID_CONFIG ID_INSTANCE SEED INSTANCE [PARAMETROS...]
args = sys.argv[1:]
instance = args[3]
seed = args[2]
switches = args[4:]

# Construimos el comando para llamar a tu main.py
# Usamos sys.executable para usar el mismo Python que este script
command = [sys.executable, "src_irace/main.py", "--instance", instance, "--seed", seed]
command.extend(switches)

# Ejecutamos y capturamos la salida
result = subprocess.run(command, capture_output=True, text=True)

# irace espera que imprimas SOLO el valor de calidad (o error)
if result.returncode == 0:
    print(result.stdout.strip())
else:
    print(f"Error: {result.stderr}", file=sys.stderr)
    sys.exit(1)