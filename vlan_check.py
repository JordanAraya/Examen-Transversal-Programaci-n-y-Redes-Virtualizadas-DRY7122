# vlan_check.py
def rango_vlan(numero):
    if 1 <= numero <= 1005:
        return "Rango normal"
    elif 1006 <= numero <= 4094:
        return "Rango extendido"
    else:
        return "Fuera de rango válido de VLAN"

def main():
    while True:
        entrada = input("Ingrese número de VLAN (o 's' para salir): ").strip()
        if entrada.lower() == 's':
            print("Saliendo...")
            break
        if not entrada.isdigit():
            print("Por favor ingrese un número válido.")
            continue
        num = int(entrada)
        print(f"VLAN {num}: {rango_vlan(num)}\n")

if __name__ == "__main__":
    main()
